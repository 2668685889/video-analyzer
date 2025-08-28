#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件夹监控模块
实现文件夹的实时监控，检测新增的视频文件并触发自动分析
"""

import os
import time
import threading
from typing import Callable, Optional, List, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .config import config

class VideoFileHandler(FileSystemEventHandler):
    """
    视频文件事件处理器
    监控文件夹中视频文件的变化
    """
    
    def __init__(self, callback: Callable[[str], None], delete_callback: Optional[Callable[[str], None]] = None):
        """
        初始化视频文件事件处理器
        
        Args:
            callback: 检测到新视频文件时的回调函数
            delete_callback: 检测到文件删除时的回调函数
        """
        super().__init__()
        self.callback = callback
        self.delete_callback = delete_callback
        self.supported_formats = config.get_supported_formats()
        self.recent_files = {}  # 记录最近处理的文件及其时间戳，避免短时间内重复处理
        self.duplicate_threshold = 5  # 5秒内的重复文件事件将被忽略
        
    def is_video_file(self, file_path: str) -> bool:
        """
        检查文件是否为支持的视频格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否为支持的视频文件
        """
        if not os.path.isfile(file_path):
            return False
            
        file_ext = os.path.splitext(file_path)[1][1:].lower()
        return file_ext in self.supported_formats
    
    def on_created(self, event):
        """
        文件创建事件处理
        
        Args:
            event: 文件系统事件
        """
        if not event.is_directory and self.is_video_file(event.src_path):
            # 检查是否为重复事件
            if self._is_duplicate_event(event.src_path):
                # 更新时间戳但不触发回调
                self.recent_files[event.src_path] = time.time()
                return
                
            # 等待文件写入完成
            self._wait_for_file_complete(event.src_path)
            
            # 记录处理时间并触发回调
            self.recent_files[event.src_path] = time.time()
            self.callback(event.src_path)
    
    def on_moved(self, event):
        """
        文件移动事件处理
        
        Args:
            event: 文件系统事件
        """
        if not event.is_directory and self.is_video_file(event.dest_path):
            # 检查是否为重复事件
            if self._is_duplicate_event(event.dest_path):
                # 更新时间戳但不触发回调
                self.recent_files[event.dest_path] = time.time()
                return
                
            # 等待文件移动完成
            self._wait_for_file_complete(event.dest_path)
            
            # 记录处理时间并触发回调
            self.recent_files[event.dest_path] = time.time()
            self.callback(event.dest_path)
    
    def on_deleted(self, event):
        """
        文件删除事件处理
        
        Args:
            event: 文件系统事件
        """
        if not event.is_directory and self.is_video_file(event.src_path):
            # 从最近文件记录中移除
            if event.src_path in self.recent_files:
                del self.recent_files[event.src_path]
            
            # 触发文件删除回调（如果设置了删除回调）
            if hasattr(self, 'delete_callback') and self.delete_callback:
                self.delete_callback(event.src_path)
    
    def _wait_for_file_complete(self, file_path: str, timeout: int = 30):
        """
        等待文件写入完成
        
        Args:
            file_path: 文件路径
            timeout: 超时时间（秒）
        """
        start_time = time.time()
        last_size = 0
        
        while time.time() - start_time < timeout:
            try:
                current_size = os.path.getsize(file_path)
                if current_size == last_size and current_size > 0:
                    # 文件大小稳定，认为写入完成
                    time.sleep(1)  # 再等待1秒确保完成
                    break
                last_size = current_size
                time.sleep(2)  # 等待2秒再检查
            except (OSError, FileNotFoundError):
                # 文件可能还在写入中
                time.sleep(1)
                continue
    
    def _is_duplicate_event(self, file_path: str) -> bool:
        """
        检查是否为重复事件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否为重复事件
        """
        current_time = time.time()
        
        # 清理过期的记录（超过阈值时间的记录）
        expired_files = []
        for path, timestamp in self.recent_files.items():
            if current_time - timestamp > self.duplicate_threshold * 2:  # 保留2倍阈值时间的记录
                expired_files.append(path)
        
        for path in expired_files:
            del self.recent_files[path]
        
        # 检查是否为重复事件
        if file_path in self.recent_files:
            time_diff = current_time - self.recent_files[file_path]
            if time_diff < self.duplicate_threshold:
                return True  # 是重复事件
        
        return False  # 不是重复事件

class FolderMonitor:
    """
    文件夹监控器
    负责监控指定文件夹中的视频文件变化
    """
    
    def __init__(self):
        """
        初始化文件夹监控器
        """
        self.observer = None
        self.is_monitoring = False
        self.monitored_folders = []  # 监控的文件夹列表
        self.file_callback = None
        self.delete_callback = None
        self.status_callback = None
        self.monitor_thread = None
        
    def set_file_callback(self, callback: Callable[[str], None]):
        """
        设置新文件检测回调函数
        
        Args:
            callback: 检测到新视频文件时的回调函数
        """
        self.file_callback = callback
    
    def set_delete_callback(self, callback: Callable[[str], None]):
        """
        设置文件删除回调函数
        
        Args:
            callback: 检测到文件删除时的回调函数
        """
        self.delete_callback = callback
    
    def set_status_callback(self, callback: Callable[[str], None]):
        """
        设置状态更新回调函数
        
        Args:
            callback: 状态更新回调函数
        """
        self.status_callback = callback
    
    def add_folder(self, folder_path: str) -> bool:
        """
        添加要监控的文件夹
        
        Args:
            folder_path: 文件夹路径
            
        Returns:
            bool: 是否添加成功
        """
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return False
            
        if folder_path not in self.monitored_folders:
            self.monitored_folders.append(folder_path)
            
            # 如果正在监控，需要重新启动监控
            if self.is_monitoring:
                self.stop_monitoring()
                self.start_monitoring()
                
        return True
    
    def remove_folder(self, folder_path: str) -> bool:
        """
        移除监控的文件夹
        
        Args:
            folder_path: 文件夹路径
            
        Returns:
            bool: 是否移除成功
        """
        if folder_path in self.monitored_folders:
            self.monitored_folders.remove(folder_path)
            
            # 如果正在监控，需要重新启动监控
            if self.is_monitoring:
                self.stop_monitoring()
                if self.monitored_folders:  # 还有其他文件夹需要监控
                    self.start_monitoring()
                    
            return True
        return False
    
    def get_monitored_folders(self) -> List[str]:
        """
        获取当前监控的文件夹列表
        
        Returns:
            List[str]: 监控的文件夹路径列表
        """
        return self.monitored_folders.copy()
    
    def start_monitoring(self) -> bool:
        """
        开始监控
        
        Returns:
            bool: 是否启动成功
        """
        if self.is_monitoring:
            # 检查Observer是否还在运行
            if self.observer and self.observer.is_alive():
                return True
            else:
                # Observer已停止，需要重新启动
                self.is_monitoring = False
                if self.status_callback:
                    self.status_callback("检测到监控器异常停止，正在重新启动...")
            
        if not self.monitored_folders:
            if self.status_callback:
                self.status_callback("没有设置监控文件夹")
            return False
            
        if not self.file_callback:
            if self.status_callback:
                self.status_callback("没有设置文件回调函数")
            return False
        
        try:
            # 确保之前的Observer已完全停止
            if self.observer:
                self.observer.stop()
                self.observer.join(timeout=5)
                
            self.observer = Observer()
            handler = VideoFileHandler(self.file_callback, self.delete_callback)
            
            # 为每个文件夹添加监控
            valid_folders = []
            for folder_path in self.monitored_folders:
                if os.path.exists(folder_path):
                    self.observer.schedule(handler, folder_path, recursive=True)
                    valid_folders.append(folder_path)
                else:
                    if self.status_callback:
                        self.status_callback(f"警告: 文件夹不存在 {folder_path}")
                    
            if not valid_folders:
                if self.status_callback:
                    self.status_callback("没有有效的监控文件夹")
                return False
                    
            self.observer.start()
            self.is_monitoring = True
            
            if self.status_callback:
                folders_text = ", ".join([os.path.basename(f) for f in valid_folders])
                self.status_callback(f"正在监控文件夹: {folders_text}")
                
            return True
            
        except Exception as e:
            self.is_monitoring = False
            if self.status_callback:
                self.status_callback(f"启动监控失败: {str(e)}")
            return False
    
    def stop_monitoring(self):
        """
        停止监控
        """
        if self.observer and self.is_monitoring:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.is_monitoring = False
            
            if self.status_callback:
                self.status_callback("已停止文件夹监控")
    
    def is_running(self) -> bool:
        """
        检查监控是否正在运行
        
        Returns:
            bool: 是否正在监控
        """
        if not self.is_monitoring:
            return False
            
        # 检查Observer是否还在运行
        if self.observer and self.observer.is_alive():
            return True
        else:
            # Observer已停止，更新状态
            self.is_monitoring = False
            if self.status_callback:
                self.status_callback("监控器已停止")
            return False
    
    def check_health(self) -> bool:
        """
        检查监控器健康状态并尝试自动恢复
        
        Returns:
            bool: 监控器是否健康运行
        """
        if not self.is_monitoring:
            return False
            
        # 检查Observer状态
        if not self.observer or not self.observer.is_alive():
            if self.status_callback:
                self.status_callback("检测到监控器异常，尝试自动恢复...")
            
            # 尝试重新启动
            self.is_monitoring = False
            return self.start_monitoring()
            
        return True
    
    def get_status_info(self) -> Dict[str, Any]:
        """
        获取监控状态信息
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        return {
            'is_monitoring': self.is_monitoring,
            'monitored_folders': self.monitored_folders,
            'folder_count': len(self.monitored_folders),
            'supported_formats': config.get_supported_formats()
        }
    
    def __del__(self):
        """
        析构函数，确保监控器正确关闭
        """
        self.stop_monitoring()
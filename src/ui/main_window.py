#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口模块
实现应用程序的主要用户界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from typing import Optional
from ..utils.file_handler import FileHandler
from ..utils.config import config
from ..utils.database import db
from ..utils.feishu_sync import FeishuSyncService
from ..utils.feishu_doc_sync import FeishuDocSyncService
from ..utils.folder_monitor import FolderMonitor
# 移除SmartFieldSetup导入，该功能已移至历史记录界面
from .settings_dialog import SettingsDialog
from .quick_prompts import QuickPromptsManager
from .history_viewer import HistoryViewer
from .mapping_config_ui import MappingConfigUI
from .oss_upload_dialog import OSSUploadDialog

class MainWindow:
    """
    主窗口类
    负责创建和管理应用程序的主界面
    """
    
    def __init__(self):
        """初始化主窗口"""
        self.root = tk.Tk()
        self.file_handler = FileHandler()
        self.current_file_path = None
        self.current_sequence_id = None
        self.selected_files = []  # 存储多个选中的文件
        self.current_analysis_index = 0  # 当前分析的文件索引
        
        # 初始化快速提示管理器和历史记录查看器
        self.quick_prompts_manager = QuickPromptsManager(self.root)
        self.history_viewer = HistoryViewer(self.root)
        
        # 初始化飞书同步服务
        self.feishu_sync = FeishuSyncService()
        
        # 初始化飞书云文档同步服务
        self.doc_sync = FeishuDocSyncService()
        
        # 初始化飞书电子表格同步服务
        from ..utils.feishu_spreadsheet_sync import feishu_spreadsheet_sync
        self.spreadsheet_sync = feishu_spreadsheet_sync
        
        # 初始化文件夹监控器
        self.folder_monitor = FolderMonitor()
        self.folder_monitor.set_file_callback(self.on_new_file_detected)
        self.folder_monitor.set_delete_callback(self.on_file_deleted)
        self.folder_monitor.set_status_callback(self.on_monitor_status_update)
        self.is_auto_analysis_enabled = False  # 是否启用自动分析
        self.is_analysis_running = False  # 分析状态标志，防止重复分析
        self.pending_auto_analysis = False  # 标记是否有待处理的自动分析
        
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """
        设置窗口属性
        """
        self.root.title("Nova Quest 视频分析系统   -- 唐山肖川科技出品  版本：1.0.0")
        self.root.geometry("1600x700")  # 宽度增加一倍
        self.root.minsize(1200, 500)    # 最小宽度也相应增加
        
        # 设置窗口图标（如果有的话）
        try:
            # 这里可以设置应用图标
            pass
        except:
            pass
    
    def create_widgets(self):
        """
        创建界面组件
        """
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # 左侧控制区域
        main_frame.columnconfigure(1, weight=1)  # 右侧结果区域
        main_frame.rowconfigure(1, weight=1)     # 主要内容区域可扩展
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="Nova Quest 视频分析系统", 
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 创建左侧控制区域
        self.create_left_control_area(main_frame)
        
        # 创建右侧结果区域
        self.create_right_result_area(main_frame)
        
        # 状态栏
        self.create_status_bar(main_frame, row=2)
    
    def create_left_control_area(self, parent):
        """
        创建左侧控制区域
        
        Args:
            parent: 父容器
        """
        # 左侧控制框架
        left_frame = ttk.Frame(parent, padding="5")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        
        # 文件选择区域
        self.create_file_selection_area(left_frame, row=0)
        
        # 提示输入区域
        self.create_prompt_area(left_frame, row=1)
        
        # 控制按钮区域
        self.create_control_buttons(left_frame, row=2)
    
    def create_right_result_area(self, parent):
        """
        创建右侧结果区域
        
        Args:
            parent: 父容器
        """
        # 右侧结果框架
        right_frame = ttk.Frame(parent, padding="5")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # 结果显示区域
        self.create_result_area(right_frame, row=0)
    
    def create_file_selection_area(self, parent, row):
        """
        创建文件选择区域
        
        Args:
            parent: 父容器
            row: 行号
        """
        # 文件选择框架
        file_frame = ttk.LabelFrame(parent, text="视频文件选择", padding="10")
        file_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        file_frame.rowconfigure(1, weight=1)
        
        # 按钮区域
        button_frame = ttk.Frame(file_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        button_frame.columnconfigure(0, weight=1)
        
        # 浏览按钮
        self.browse_button = ttk.Button(
            button_frame, 
            text="选择视频文件", 
            command=self.browse_files
        )
        self.browse_button.grid(row=0, column=0, sticky=tk.W)
        
        # 选择文件夹按钮
        self.browse_folder_button = ttk.Button(
            button_frame, 
            text="选择文件夹", 
            command=self.browse_folder
        )
        self.browse_folder_button.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # 清空按钮
        self.clear_files_button = ttk.Button(
            button_frame, 
            text="清空列表", 
            command=self.clear_file_list
        )
        self.clear_files_button.grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        
        # 刷新按钮
        self.refresh_files_button = ttk.Button(
            button_frame, 
            text="刷新列表", 
            command=self.refresh_file_list
        )
        self.refresh_files_button.grid(row=0, column=3, sticky=tk.W, padx=(10, 0))
        
        # 监控功能区域
        monitor_frame = ttk.Frame(button_frame)
        monitor_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 监控开关
        self.monitor_var = tk.BooleanVar()
        self.monitor_checkbox = ttk.Checkbutton(
            monitor_frame,
            text="启用文件夹监控",
            variable=self.monitor_var,
            command=self.toggle_folder_monitoring
        )
        self.monitor_checkbox.grid(row=0, column=0, sticky=tk.W)
        
        # 自动分析开关
        self.auto_analysis_var = tk.BooleanVar()
        self.auto_analysis_checkbox = ttk.Checkbutton(
            monitor_frame,
            text="检测到新文件时自动分析",
            variable=self.auto_analysis_var,
            command=self.toggle_auto_analysis
        )
        self.auto_analysis_checkbox.grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # 监控状态标签
        self.monitor_status_label = ttk.Label(
            monitor_frame,
            text="监控状态: 未启动",
            foreground="gray"
        )
        self.monitor_status_label.grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        
        # 文件列表区域
        list_frame = ttk.Frame(file_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 文件列表
        from tkinter import ttk as ttk_tree
        self.file_tree = ttk_tree.Treeview(
            list_frame,
            columns=('size', 'status'),
            show='tree headings',
            height=6
        )
        self.file_tree.heading('#0', text='文件名')
        self.file_tree.heading('size', text='大小')
        self.file_tree.heading('status', text='状态')
        self.file_tree.column('#0', width=200)
        self.file_tree.column('size', width=80)
        self.file_tree.column('status', width=80)
        
        # 滚动条
        tree_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.file_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 显示支持的格式
        format_info = self.file_handler.get_supported_formats_info()
        formats_text = f"支持格式: {', '.join(format_info['supported_formats'])} | 最大文件大小: {format_info['max_file_size_mb']}MB"
        ttk.Label(file_frame, text=formats_text, foreground="blue").grid(
            row=2, column=0, sticky=tk.W, pady=(5, 0)
        )
    
    def create_prompt_area(self, parent, row):
        """
        创建提示输入区域
        
        Args:
            parent: 父容器
            row: 行号
        """
        # 提示输入框架
        prompt_frame = ttk.LabelFrame(parent, text="分析提示", padding="10")
        prompt_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        prompt_frame.columnconfigure(0, weight=1)
        
        # 快速提示选择区域
        quick_prompt_frame = self.quick_prompts_manager.create_quick_prompt_frame(prompt_frame)
        quick_prompt_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 移除自定义提示内容栏，避免与快速提示功能冲突
    
    def create_control_buttons(self, parent, row):
        """
        创建控制按钮区域
        
        Args:
            parent: 父容器
            row: 行号
        """
        # 按钮框架
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=3, pady=(0, 10))
        
        # 第一行按钮
        top_button_frame = ttk.Frame(button_frame)
        top_button_frame.pack(pady=(0, 5))
        
        # 分析按钮
        self.analyze_button = ttk.Button(
            top_button_frame, 
            text="开始分析", 
            command=self.start_analysis
        )
        self.analyze_button.grid(row=0, column=0, padx=(0, 10))
        
        # 清除结果按钮
        self.clear_button = ttk.Button(
            top_button_frame, 
            text="清除结果", 
            command=self.clear_results
        )
        self.clear_button.grid(row=0, column=1, padx=(0, 10))
        
        # 保存结果按钮
        self.save_button = ttk.Button(
            top_button_frame, 
            text="保存结果", 
            command=self.save_results,
            state="disabled"
        )
        self.save_button.grid(row=0, column=2, padx=(0, 10))
        
        # 设置按钮
        self.settings_button = ttk.Button(
            top_button_frame, 
            text="设置", 
            command=self.open_settings
        )
        self.settings_button.grid(row=0, column=3, padx=(0, 10))
        
        # 历史记录按钮
        self.history_button = ttk.Button(
            top_button_frame, 
            text="历史记录", 
            command=self.open_history_viewer
        )
        self.history_button.grid(row=0, column=4, padx=(0, 10))
        
        # 飞书同步按钮
        self.feishu_sync_button = ttk.Button(
            top_button_frame, 
            text="飞书同步", 
            command=self.sync_to_feishu,
            state="disabled"
        )
        self.feishu_sync_button.grid(row=0, column=5, padx=(0, 10))
        
        # 映射配置按钮
        self.mapping_config_button = ttk.Button(
            top_button_frame, 
            text="映射配置", 
            command=self.open_mapping_config
        )
        self.mapping_config_button.grid(row=0, column=6, padx=(0, 10))
        
        # OSS上传按钮
        self.oss_upload_button = ttk.Button(
            top_button_frame, 
            text="OSS上传", 
            command=self.open_oss_upload
        )
        self.oss_upload_button.grid(row=0, column=7, padx=(0, 10))
    
    def create_result_area(self, parent, row):
        """
        创建结果显示区域
        
        Args:
            parent: 父容器
            row: 行号
        """
        # 结果显示框架
        result_frame = ttk.LabelFrame(parent, text="分析结果", padding="10")
        result_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(1, weight=1)
        
        # 结果控制区域
        result_control_frame = ttk.Frame(result_frame)
        result_control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        result_control_frame.columnconfigure(1, weight=1)
        
        # 文件选择下拉框
        ttk.Label(result_control_frame, text="查看结果:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.result_file_var = tk.StringVar()
        self.result_file_combo = ttk.Combobox(
            result_control_frame,
            textvariable=self.result_file_var,
            state="readonly",
            width=40
        )
        self.result_file_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.result_file_combo.bind('<<ComboboxSelected>>', self.on_result_file_selected)
        
        # 导出按钮
        self.export_result_button = ttk.Button(
            result_control_frame,
            text="导出当前结果",
            command=self.export_current_result,
            state="disabled"
        )
        self.export_result_button.grid(row=0, column=2, sticky=tk.W)
        
        # 结果文本框（使用ScrolledText）
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            height=25,
            state="disabled"
        )
        self.result_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 存储多文件结果
        self.file_results = {}  # {file_path: result_text}
        
        # 配置网格权重
        parent.rowconfigure(row, weight=1)
    
    def create_status_bar(self, parent, row):
        """
        创建状态栏
        
        Args:
            parent: 父容器
            row: 行号
        """
        # 状态栏框架
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        status_frame.columnconfigure(0, weight=1)
        
        # 状态标签
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        self.status_label = ttk.Label(
            status_frame, 
            textvariable=self.status_var, 
            relief="sunken", 
            anchor="w"
        )
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 飞书多维表格同步状态标签
        self.feishu_status_var = tk.StringVar()
        self.feishu_status_var.set("多维表格: 未配置")
        self.feishu_status_label = ttk.Label(
            status_frame, 
            textvariable=self.feishu_status_var, 
            relief="sunken", 
            anchor="center",
            width=18
        )
        self.feishu_status_label.grid(row=0, column=1, padx=(5, 5))
        
        # 飞书电子表格同步状态标签
        self.spreadsheet_status_var = tk.StringVar()
        self.spreadsheet_status_var.set("电子表格: 未配置")
        self.spreadsheet_status_label = ttk.Label(
            status_frame, 
            textvariable=self.spreadsheet_status_var, 
            relief="sunken", 
            anchor="center",
            width=18
        )
        self.spreadsheet_status_label.grid(row=0, column=2, padx=(5, 5))
        
        # 飞书云文档同步状态标签
        self.doc_status_var = tk.StringVar()
        self.doc_status_var.set("文档: 未配置")
        self.doc_status_label = ttk.Label(
            status_frame, 
            textvariable=self.doc_status_var, 
            relief="sunken", 
            anchor="center",
            width=15
        )
        self.doc_status_label.grid(row=0, column=3, padx=(5, 5))
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            status_frame, 
            variable=self.progress_var, 
            mode="indeterminate"
        )
        self.progress_bar.grid(row=0, column=4, padx=(5, 0), sticky=tk.E)
        
        # 更新飞书状态
        self.update_feishu_status()
        self.update_spreadsheet_status()
        self.update_doc_status()
    
    def browse_files(self):
        """
        浏览并选择多个文件
        """
        format_info = self.file_handler.get_supported_formats_info()
        formats = format_info['supported_formats']
        
        # 构建文件类型过滤器
        filetypes = [
            ('视频文件', ' '.join([f'*.{fmt}' for fmt in formats])),
            ('所有文件', '*.*')
        ]
        
        file_paths = filedialog.askopenfilenames(
            title="选择视频文件（可多选）",
            filetypes=filetypes
        )
        
        if file_paths:
            self.add_files_to_list(file_paths)
    
    def browse_folder(self):
        """
        浏览并选择文件夹，自动扫描其中的视频文件
        """
        folder_path = filedialog.askdirectory(
            title="选择文件夹（将添加到监控列表）"
        )
        
        if folder_path:
            # 先将文件夹添加到监控列表
            if self.folder_monitor.add_folder(folder_path):
                folder_name = os.path.basename(folder_path)
                self.set_status(f"已添加文件夹到监控列表: {folder_name}")
                
                # 然后扫描文件夹中的视频文件
                self.scan_folder_for_videos(folder_path)
            else:
                self.set_status(f"添加文件夹到监控列表失败: {os.path.basename(folder_path)}")
    
    def scan_folder_for_videos(self, folder_path):
        """
        扫描文件夹中的所有视频文件
        
        Args:
            folder_path: 文件夹路径
        """
        try:
            # 获取支持的视频格式
            format_info = self.file_handler.get_supported_formats_info()
            supported_formats = format_info['supported_formats']
            
            # 扫描文件夹中的视频文件
            video_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 检查文件扩展名是否为支持的视频格式
                    file_ext = os.path.splitext(file)[1][1:].lower()  # 去掉点号并转为小写
                    if file_ext in supported_formats:
                        video_files.append(file_path)
            
            if video_files:
                self.set_status(f"在文件夹中找到 {len(video_files)} 个视频文件")
                self.add_files_to_list(video_files)
            else:
                folder_name = os.path.basename(folder_path)
                messagebox.showinfo(
                    "文件夹已添加到监控", 
                    f"文件夹 '{folder_name}' 已成功添加到监控列表！\n\n"
                    f"当前文件夹中未找到支持的视频文件，但系统会持续监控此文件夹。\n"
                    f"当有新的视频文件添加到此文件夹时，系统会自动检测。\n\n"
                    f"支持的格式: {', '.join(supported_formats)}"
                )
                self.set_status(f"文件夹 '{folder_name}' 已添加到监控，当前无视频文件")
                
        except Exception as e:
            messagebox.showerror("错误", f"扫描文件夹时发生错误: {str(e)}")
            self.set_status("扫描文件夹失败")
    
    def add_files_to_list(self, file_paths):
        """
        添加文件到列表
        
        Args:
            file_paths: 文件路径列表
        """
        for file_path in file_paths:
            if file_path not in [f['path'] for f in self.selected_files]:
                # 验证文件
                validation_result = self.file_handler.validate_and_prepare_file(file_path)
                
                file_info = {
                    'path': file_path,
                    'name': os.path.basename(file_path),
                    'size': 0,
                    'status': '待分析'
                }
                
                if validation_result['success']:
                    file_info['size'] = validation_result['file_info']['size_mb']
                    file_info['status'] = '就绪'
                else:
                    file_info['status'] = '错误'
                
                self.selected_files.append(file_info)
                
                # 添加到树形控件
                item_id = self.file_tree.insert('', 'end', 
                    text=file_info['name'],
                    values=(f"{file_info['size']:.1f}MB", file_info['status'])
                )
        
        # 更新按钮状态
        if self.selected_files:
            self.analyze_button.config(state="normal")
    
    def clear_file_list(self):
        """
        清空文件列表
        """
        self.selected_files.clear()
        self.file_tree.delete(*self.file_tree.get_children())
        self.current_file_path = None
        self.analyze_button.config(state="disabled")
    
    def refresh_file_list(self):
        """
        刷新文件列表
        重新验证所有文件的状态和信息
        """
        if not self.selected_files:
            self.set_status("没有文件需要刷新")
            return
        
        self.set_status("正在刷新文件列表...")
        
        # 保存当前文件路径列表
        current_file_paths = [file_info['path'] for file_info in self.selected_files]
        
        # 清空当前列表
        self.selected_files.clear()
        self.file_tree.delete(*self.file_tree.get_children())
        
        # 重新验证并添加文件
        valid_files = []
        invalid_files = []
        
        for file_path in current_file_paths:
            if os.path.exists(file_path):
                validation_result = self.file_handler.validate_and_prepare_file(file_path)
                if validation_result['success']:
                    valid_files.append(file_path)
                else:
                    invalid_files.append((file_path, validation_result['error']))
            else:
                invalid_files.append((file_path, "文件不存在"))
        
        # 重新添加有效文件
        if valid_files:
            self.add_files_to_list(valid_files)
        
        # 报告刷新结果
        if invalid_files:
            invalid_count = len(invalid_files)
            valid_count = len(valid_files)
            self.set_status(f"刷新完成: {valid_count}个有效文件, {invalid_count}个无效文件已移除")
            
            # 显示无效文件详情
            if invalid_count <= 5:  # 如果无效文件不多，显示详细信息
                invalid_names = [os.path.basename(path) for path, _ in invalid_files]
                messagebox.showwarning(
                    "文件刷新", 
                    f"以下文件已从列表中移除:\n{', '.join(invalid_names)}"
                )
        else:
            self.set_status(f"刷新完成: 所有 {len(valid_files)} 个文件均有效")
    
    def set_file_path(self, file_path: str):
        """
        设置文件路径
        
        Args:
            file_path (str): 文件路径
        """
        self.current_file_path = file_path
        
        # 验证文件并显示信息
        validation_result = self.file_handler.validate_and_prepare_file(file_path)
        
        if validation_result['success']:
            file_info = validation_result['file_info']
            # 在文件树中选中对应的文件
            for item in self.file_tree.get_children():
                item_path = self.file_tree.item(item, 'values')[0] if self.file_tree.item(item, 'values') else ''
                if item_path == file_path or self.file_tree.item(item, 'text') == os.path.basename(file_path):
                    self.file_tree.selection_set(item)
                    self.file_tree.focus(item)
                    break
            self.analyze_button.config(state="normal")
        else:
            self.set_status(f"文件验证失败: {validation_result['error']}")
            self.analyze_button.config(state="disabled")
    
    # 移除set_preset_prompt方法，不再需要设置自定义提示文本框
    
    def start_analysis(self):
        """
        开始分析视频
        """
        # 检查是否已经在分析中
        if self.is_analysis_running:
            self.set_status("分析正在进行中，请等待当前分析完成")
            return
            
        if not self.selected_files:
            messagebox.showerror("错误", "请先选择视频文件")
            return
        
        # 从快速提示管理器获取选中的提示内容
        prompt = self.quick_prompts_manager.get_selected_prompt_text()
        if not prompt:
            messagebox.showerror("错误", "请选择一个快速提示")
            return
        
        # 检查API配置
        if not config.is_valid():
            messagebox.showerror(
                "配置错误", 
                "Gemini API密钥未配置。\n请在项目根目录创建.env文件并设置GEMINI_API_KEY。"
            )
            return
        
        # 设置分析状态
        self.is_analysis_running = True
        
        # 重置分析索引
        self.current_analysis_index = 0
        
        # 清空之前的结果
        self.clear_results()
        
        # 在后台线程中执行批量分析
        self.set_ui_analyzing_state(True)
        analysis_thread = threading.Thread(
            target=self.perform_batch_analysis, 
            args=(prompt,)
        )
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def start_single_file_analysis(self, file_path: str):
        """
        开始分析单个视频文件（用于自动分析）
        
        Args:
            file_path (str): 要分析的文件路径
        """
        # 检查是否已经在分析中
        if self.is_analysis_running:
            self.set_status("分析正在进行中，请等待当前分析完成")
            return
        
        # 检查文件是否已经被分析过
        file_already_analyzed = False
        for file_info in self.selected_files:
            if file_info['path'] == file_path and file_info['status'] == '完成':
                file_already_analyzed = True
                break
        
        if file_already_analyzed:
            file_name = os.path.basename(file_path)
            self.set_status(f"文件 {file_name} 已经分析完成，跳过重复分析")
            return
        
        # 从快速提示管理器获取选中的提示内容
        prompt = self.quick_prompts_manager.get_selected_prompt_text()
        if not prompt:
            self.set_status("错误：未选择分析提示")
            return
        
        # 检查API配置
        if not config.is_valid():
            self.set_status("错误：Gemini API密钥未配置")
            return
        
        # 设置分析状态
        self.is_analysis_running = True
        
        # 在后台线程中执行单文件分析
        self.set_ui_analyzing_state(True)
        analysis_thread = threading.Thread(
            target=self.perform_single_file_analysis, 
            args=(file_path, prompt)
        )
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def perform_single_file_analysis(self, file_path: str, prompt: str):
        """
        执行单个文件分析（在后台线程中运行）
        
        Args:
            file_path (str): 文件路径
            prompt (str): 分析提示
        """
        try:
            # 找到文件在列表中的索引
            file_index = -1
            for i, file_info in enumerate(self.selected_files):
                if file_info['path'] == file_path:
                    file_index = i
                    break
            
            if file_index == -1:
                raise Exception(f"文件 {file_path} 不在文件列表中")
            
            # 更新文件状态为分析中
            self.root.after(0, lambda: self.update_file_status(file_index, "分析中"))
            
            # 执行分析
            result = self.file_handler.process_video_analysis(file_path, prompt)
            
            # 在主线程中处理结果
            self.root.after(0, lambda: self.handle_single_analysis_result(result, file_index))
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': f"分析文件 {os.path.basename(file_path)} 时发生错误: {str(e)}",
                'file_path': file_path
            }
            self.root.after(0, lambda: self.handle_single_analysis_result(error_result, file_index))
        finally:
            # 在主线程中重置分析状态
            def reset_analysis_state():
                self.set_ui_analyzing_state(False)
                self.is_analysis_running = False
                
                # 检查是否有待处理的自动分析
                if self.pending_auto_analysis:
                    self.pending_auto_analysis = False
                    # 查找未分析的文件
                    unanalyzed_files = [f for f in self.selected_files if f['status'] in ['就绪', '待分析']]
                    if unanalyzed_files:
                        # 分析第一个未分析的文件
                        next_file = unanalyzed_files[0]
                        self.root.after(100, lambda: self.start_single_file_analysis(next_file['path']))
            
            self.root.after(0, reset_analysis_state)
    
    def perform_batch_analysis(self, prompt: str):
        """
        执行批量视频分析（在后台线程中运行）
        
        Args:
            prompt (str): 分析提示
        """
        # 提取文件路径列表
        file_paths = [file_info['path'] for file_info in self.selected_files]
        
        # 定义进度回调函数
        def progress_callback(progress_info):
            # 在主线程中更新UI
            self.root.after(0, lambda: self.handle_batch_progress(progress_info))
        
        try:
            # 使用文件处理器的批量分析功能
            batch_result = self.file_handler.process_batch_video_analysis(
                file_paths, prompt, progress_callback
            )
            
            # 在主线程中处理最终结果
            self.root.after(0, lambda: self.handle_batch_analysis_complete(batch_result))
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': f"批量分析过程中发生错误: {str(e)}"
            }
            self.root.after(0, lambda: self.handle_batch_analysis_complete(error_result))
    
    def perform_analysis(self, file_path: str, prompt: str):
        """
        执行单个视频分析（在后台线程中运行）
        
        Args:
            file_path (str): 文件路径
            prompt (str): 分析提示
        """
        try:
            # 更新状态
            self.root.after(0, lambda: self.status_var.set("正在上传文件..."))
            
            # 执行分析
            result = self.file_handler.process_video_analysis(file_path, prompt)
            
            # 在主线程中更新UI
            self.root.after(0, lambda: self.handle_analysis_result(result))
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': f"分析过程中发生错误: {str(e)}"
            }
            self.root.after(0, lambda: self.handle_analysis_result(error_result))
    
    def handle_single_analysis_result(self, result: dict, file_index: int):
        """
        处理单个文件的分析结果
        
        Args:
            result (dict): 分析结果
            file_index (int): 文件索引
        """
        file_info = self.selected_files[file_index]
        
        if result['success']:
            # 更新文件状态
            self.update_file_status(file_index, "完成")
            
            # 存储结果到文件结果字典
            result_text = f"=== {file_info['name']} 分析结果 ==="
            # 检查result['result']是否为None，避免TypeError
            analysis_result = result.get('result', '')
            if analysis_result is None:
                analysis_result = '分析结果为空'
            result_text += analysis_result
            
            # 添加OSS链接信息到结果显示
            oss_info = result.get('oss_info')
            if oss_info and not oss_info.get('error'):
                oss_url = oss_info.get('url')
                oss_file_name = oss_info.get('file_name')
                if oss_url:
                    result_text += "\n\n=== OSS上传信息 ==="
                    result_text += f"\nOSS链接: {oss_url}"
                    if oss_file_name:
                        result_text += f"\nOSS文件名: {oss_file_name}"
            elif oss_info and oss_info.get('error'):
                result_text += "\n\n=== OSS上传信息 ==="
                result_text += f"\nOSS上传失败: {oss_info.get('error')}"
            
            # 保存分析结果到数据库
            try:
                # 获取文件信息
                file_name = file_info['name']
                file_size = os.path.getsize(file_info['path'])
                
                # 获取MIME类型
                mime_type = "video/mp4"  # 默认值
                if 'file_info' in result:
                    mime_type = result['file_info'].get('mime_type', mime_type)
                
                # 获取分析提示
                analysis_prompt = self.quick_prompts_manager.get_selected_prompt_text()
                
                # 获取Gemini文件信息
                gemini_file_uri = result.get('gemini_file_uri')
                gemini_file_name = result.get('gemini_file_name')
                
                # 获取OSS信息
                oss_info = result.get('oss_info', {})
                oss_url = oss_info.get('url') if oss_info and not oss_info.get('error') else None
                oss_file_name = oss_info.get('file_name') if oss_info and not oss_info.get('error') else None
                
                # 保存到数据库
                sequence_id = db.save_analysis_result(
                    file_path=file_info['path'],
                    file_name=file_name,
                    file_size=file_size,
                    mime_type=mime_type,
                    analysis_prompt=analysis_prompt,
                    analysis_result=analysis_result,  # 使用已检查的analysis_result
                    gemini_file_uri=gemini_file_uri,
                    gemini_file_name=gemini_file_name,
                    oss_url=oss_url,
                    oss_file_name=oss_file_name
                )
                
                # 在结果中添加序列号信息
                result_text += f"\n\n序列号: {sequence_id} | 已保存到历史记录"
                
            except Exception as e:
                print(f"保存分析结果到数据库失败: {str(e)}")
                result_text += f"\n\n注意: 保存到数据库失败: {str(e)}"
            
            # 存储到文件结果字典
            self.file_results[file_info['path']] = result_text
            
            # 更新结果选择下拉框
            self.update_result_combo()
            
            # 检查是否有待处理的自动分析
            if self.pending_auto_analysis and self.is_auto_analysis_enabled:
                self.pending_auto_analysis = False
                # 检查是否有设置的提示词和文件
                current_prompt = self.quick_prompts_manager.get_selected_prompt_text()
                # 检查是否有未分析的文件（状态为'就绪'或'待分析'的文件）
                unanalyzed_files = [f for f in self.selected_files if f['status'] in ['就绪', '待分析']]
                if current_prompt and unanalyzed_files:
                    if len(unanalyzed_files) > 1:
                        # 如果有多个未分析文件，启动批量分析
                        self.set_status(f"继续批量分析剩余 {len(unanalyzed_files)} 个文件")
                        # 延迟一秒后开始批量分析，避免UI冲突
                        self.root.after(1000, lambda: self.start_analysis())
                    elif len(unanalyzed_files) == 1:
                        # 只有一个文件，进行单文件分析
                        next_file = unanalyzed_files[0]
                        self.set_status(f"开始分析待处理文件: {next_file['name']}")
                        # 延迟一秒后开始单文件分析，避免UI冲突
                        self.root.after(1000, lambda: self.start_single_file_analysis(next_file['path']))
                else:
                    self.set_status("没有待分析的文件，跳过自动分析")
            
            # 如果是第一个完成的文件，自动显示其结果
            if len(self.file_results) == 1:
                self.display_file_result(file_info['path'])
                
        else:
            # 更新文件状态为错误
            self.update_file_status(file_index, "错误")
            
            # 存储错误信息
            error_text = f"=== {file_info['name']} 分析失败 ===\n"
            # 安全地获取错误信息
            error_msg = result.get('error', '未知错误')
            error_text += f"错误: {error_msg}"
            
            self.file_results[file_info['path']] = error_text
            
            # 更新结果选择下拉框
            self.update_result_combo()
        
        # 重置分析状态
        self.is_analysis_running = False
        self.set_ui_analyzing_state(False)
    
    def handle_batch_progress(self, progress_info: dict):
        """
        处理批量分析进度更新
        
        Args:
            progress_info (dict): 进度信息
        """
        current_file = progress_info['current_file']
        total_files = progress_info['total_files']
        file_path = progress_info['file_path']
        status = progress_info['status']
        
        # 更新状态栏
        file_name = os.path.basename(file_path)
        if status == 'waiting':
            status_text = f"已完成文件 {current_file}/{total_files}: {file_name} - {progress_info.get('message', '等待中...')}"
        else:
            status_text = f"正在处理文件 {current_file}/{total_files}: {file_name}"
        self.status_var.set(status_text)
        
        # 查找文件在列表中的索引
        file_index = -1
        for i, file_info in enumerate(self.selected_files):
            if file_info['path'] == file_path:
                file_index = i
                break
        
        if file_index >= 0:
            # 更新文件状态
            if status == 'processing':
                self.update_file_status(file_index, "分析中")
            elif status == 'completed':
                self.update_file_status(file_index, "完成")
                # 处理分析结果
                if 'result' in progress_info:
                    self.handle_single_analysis_result(progress_info['result'], file_index)
            elif status == 'failed':
                self.update_file_status(file_index, "错误")
                # 处理错误结果
                if 'result' in progress_info:
                    self.handle_single_analysis_result(progress_info['result'], file_index)
            elif status == 'waiting':
                # 保持当前状态，只更新状态栏显示等待信息
                pass
    
    def handle_batch_analysis_complete(self, batch_result: dict):
        """
        处理批量分析完成
        
        Args:
            batch_result (dict): 批量分析结果
        """
        # 重置分析状态
        self.is_analysis_running = False
        
        # 恢复UI状态
        self.set_ui_analyzing_state(False)
        
        if batch_result.get('success', False):
            self.status_var.set("批量分析完成")
            
            # 显示完成信息
            completion_text = f"\n\n=== 批量分析完成 ===\n"
            completion_text += f"共处理 {batch_result.get('total_files', 0)} 个文件\n"
            completion_text += f"成功: {batch_result.get('successful_analyses', 0)} 个\n"
            completion_text += f"失败: {batch_result.get('failed_analyses', 0)} 个"
            self.append_result(completion_text)
        else:
            self.status_var.set("批量分析失败")
            # 安全地获取错误信息
            error_msg = batch_result.get('error', '未知错误')
            if 'validation_result' in batch_result:
                # 如果是验证失败，提供更详细的信息
                validation_result = batch_result['validation_result']
                invalid_files = validation_result.get('invalid_files', [])
                if invalid_files:
                    # 安全地获取文件名，支持不同的键名格式
                    invalid_file_names = []
                    for f in invalid_files:
                        if isinstance(f, dict):
                            # 尝试不同的键名
                            file_name = f.get('file_name') or f.get('file_path') or str(f)
                            if file_name and file_name != str(f):
                                invalid_file_names.append(os.path.basename(file_name))
                            else:
                                invalid_file_names.append(str(f))
                        else:
                            invalid_file_names.append(str(f))
                    error_msg += f"\n无效文件: {', '.join(invalid_file_names)}"
            
            error_text = f"\n\n=== 批量分析失败 ===\n错误: {error_msg}"
            self.append_result(error_text)
        
        # 检查是否有待处理的自动分析
        if self.pending_auto_analysis and self.is_auto_analysis_enabled:
            self.pending_auto_analysis = False
            # 检查是否有设置的提示词和文件
            current_prompt = self.quick_prompts_manager.get_selected_prompt_text()
            # 检查是否有未分析的文件（状态为'就绪'或'待分析'的文件）
            unanalyzed_files = [f for f in self.selected_files if f['status'] in ['就绪', '待分析']]
            if current_prompt and unanalyzed_files:
                if len(unanalyzed_files) > 1:
                    # 如果有多个未分析文件，继续批量分析
                    self.set_status(f"继续批量分析剩余 {len(unanalyzed_files)} 个文件")
                    # 延迟一秒后开始批量分析，避免UI冲突
                    self.root.after(1000, lambda: self.start_analysis())
                else:
                    # 只有一个文件，进行单文件分析
                    next_file = unanalyzed_files[0]
                    self.set_status(f"开始分析待处理文件: {next_file['name']}")
                    # 延迟一秒后开始单文件分析，避免UI冲突
                    self.root.after(1000, lambda: self.start_single_file_analysis(next_file['path']))
            else:
                self.set_status("没有待分析的文件，跳过自动分析")
    
    def update_file_status(self, file_index: int, status: str):
        """
        更新文件状态
        
        Args:
            file_index (int): 文件索引
            status (str): 新状态
        """
        if 0 <= file_index < len(self.selected_files):
            self.selected_files[file_index]['status'] = status
            
            # 更新树形控件中的状态
            children = self.file_tree.get_children()
            if file_index < len(children):
                item_id = children[file_index]
                current_values = list(self.file_tree.item(item_id, 'values'))
                current_values[1] = status  # 状态在第二列
                self.file_tree.item(item_id, values=current_values)
    
    def handle_analysis_result(self, result: dict):
        """
        处理分析结果（单文件模式兼容）
        
        Args:
            result (dict): 分析结果
        """
        self.set_ui_analyzing_state(False)
        
        if result['success']:
            # 构建显示结果，包含分析内容和OSS链接
            display_text = result['result']
            
            # 添加OSS链接信息到结果显示
            oss_info = result.get('oss_info')
            if oss_info and not oss_info.get('error'):
                oss_url = oss_info.get('url')
                oss_file_name = oss_info.get('file_name')
                if oss_url:
                    display_text += "\n\n=== OSS上传信息 ==="
                    display_text += f"\nOSS链接: {oss_url}"
                    if oss_file_name:
                        display_text += f"\nOSS文件名: {oss_file_name}"
            elif oss_info and oss_info.get('error'):
                display_text += "\n\n=== OSS上传信息 ==="
                display_text += f"\nOSS上传失败: {oss_info.get('error')}"
            
            # 显示成功结果
            self.display_result(display_text)
            self.status_var.set("分析完成")
            self.save_button.config(state="normal")
            
            # 保存分析结果到数据库
            try:
                if self.current_file_path:
                    # 获取文件信息
                    file_name = os.path.basename(self.current_file_path)
                    file_size = os.path.getsize(self.current_file_path)
                    
                    # 获取MIME类型
                    mime_type = "video/mp4"  # 默认值
                    if 'file_info' in result:
                        mime_type = result['file_info'].get('mime_type', mime_type)
                    
                    # 获取分析提示
                    analysis_prompt = self.quick_prompts_manager.get_selected_prompt_text()
                    
                    # 获取Gemini文件信息
                    gemini_file_uri = result.get('gemini_file_uri')
                    gemini_file_name = result.get('gemini_file_name')
                    
                    # 获取OSS信息
                    oss_info = result.get('oss_info', {})
                    oss_url = oss_info.get('url') if oss_info and not oss_info.get('error') else None
                    oss_file_name = oss_info.get('file_name') if oss_info and not oss_info.get('error') else None
                    
                    # 保存到数据库
                    sequence_id = db.save_analysis_result(
                        file_path=self.current_file_path,
                        file_name=file_name,
                        file_size=file_size,
                        mime_type=mime_type,
                        analysis_prompt=analysis_prompt,
                        analysis_result=result['result'],
                        gemini_file_uri=gemini_file_uri,
                        gemini_file_name=gemini_file_name,
                        oss_url=oss_url,
                        oss_file_name=oss_file_name
                    )
                    
                    self.current_sequence_id = sequence_id
                    
                    # 在结果中显示序列号
                    sequence_info = f"\n\n--- 分析记录 ---\n序列号: {sequence_id}\n已保存到历史记录"
                    self.append_result(sequence_info)
                    
                    # 自动同步到飞书（如果启用）
                    self.auto_sync_to_feishu(sequence_id)
                    
                    # 自动同步到电子表格（如果启用）
                    if config.feishu_spreadsheet_auto_sync:
                        self.auto_sync_to_spreadsheet(sequence_id)
                    
            except Exception as e:
                print(f"保存分析结果到数据库失败: {str(e)}")
            
            # 显示文件信息（如果有）
            if 'file_info' in result:
                file_info = result['file_info']
                info_text = f"\n\n--- 文件信息 ---\n"
                info_text += f"文件名: {file_info['display_name']}\n"
                info_text += f"大小: {file_info['size_bytes']} 字节"
                self.append_result(info_text)
        else:
            # 显示错误信息
            error_msg = f"分析失败: {result['error']}"
            self.display_result(error_msg)
            self.status_var.set("分析失败")
            messagebox.showerror("分析失败", result['error'])
    
    def display_result(self, text: str):
        """
        显示结果文本
        
        Args:
            text (str): 要显示的文本
        """
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, text)
        self.result_text.config(state="disabled")
    
    def append_result(self, text: str):
        """
        追加结果文本
        
        Args:
            text (str): 要追加的文本
        """
        self.result_text.config(state="normal")
        self.result_text.insert(tk.END, text)
        self.result_text.see(tk.END)  # 滚动到底部
        self.result_text.config(state="disabled")
    
    def update_result_combo(self):
        """
        更新结果选择下拉框
        """
        file_names = [os.path.basename(path) for path in self.file_results.keys()]
        self.result_file_combo['values'] = file_names
        
        # 如果有结果，启用导出按钮
        if file_names:
            self.export_result_button.config(state="normal")
    
    def display_file_result(self, file_path: str):
        """
        显示指定文件的分析结果
        
        Args:
            file_path (str): 文件路径
        """
        if file_path in self.file_results:
            self.result_text.config(state="normal")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, self.file_results[file_path])
            self.result_text.config(state="disabled")
            
            # 更新下拉框选择
            file_name = os.path.basename(file_path)
            self.result_file_var.set(file_name)
    
    def on_result_file_selected(self, event=None):
        """
        处理结果文件选择事件
        
        Args:
            event: 事件对象
        """
        selected_name = self.result_file_var.get()
        if selected_name:
            # 根据文件名找到对应的路径
            for file_path in self.file_results.keys():
                if os.path.basename(file_path) == selected_name:
                    self.display_file_result(file_path)
                    break
    
    def export_current_result(self):
        """
        导出当前显示的结果
        """
        selected_name = self.result_file_var.get()
        if not selected_name:
            messagebox.showwarning("警告", "请先选择要导出的结果")
            return
        
        # 找到对应的文件路径
        selected_path = None
        for file_path in self.file_results.keys():
            if os.path.basename(file_path) == selected_name:
                selected_path = file_path
                break
        
        if not selected_path:
            messagebox.showerror("错误", "未找到选中的结果")
            return
        
        # 选择保存位置
        save_path = filedialog.asksaveasfilename(
            title="导出分析结果",
            defaultextension=".txt",
            filetypes=[
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ],
            initialname=f"{os.path.splitext(selected_name)[0]}_分析结果.txt"
        )
        
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(self.file_results[selected_path])
                messagebox.showinfo("成功", f"结果已导出到: {save_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def clear_results(self):
        """
        清除结果
        """
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state="disabled")
        self.save_button.config(state="disabled")
        self.export_result_button.config(state="disabled")
        self.current_sequence_id = None
        
        # 清空文件结果字典和下拉框
        self.file_results.clear()
        self.result_file_combo['values'] = ()
        self.result_file_var.set('')
        self.status_var.set("就绪")
    
    def save_results(self):
        """
        保存结果到文件
        """
        content = self.result_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "没有结果可保存")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存分析结果",
            defaultextension=".txt",
            filetypes=[
                ('文本文件', '*.txt'),
                ('所有文件', '*.*')
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"结果已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存文件失败: {str(e)}")
    
    def set_ui_analyzing_state(self, analyzing: bool):
        """
        设置UI分析状态
        
        Args:
            analyzing (bool): 是否正在分析
        """
        if analyzing:
            self.analyze_button.config(state="disabled")
            self.browse_button.config(state="disabled")
            self.progress_bar.start()
            self.status_var.set("正在分析...")
        else:
            self.analyze_button.config(state="normal")
            self.browse_button.config(state="normal")
            self.progress_bar.stop()
    
    # 移除on_prompt_selected回调方法，快速提示管理器现在直接管理选中状态
    
    def open_history_viewer(self):
        """
        打开历史记录查看器
        """
        self.history_viewer.open_history_viewer()
    
    def open_settings(self):
        """
        打开设置对话框
        """
        settings_dialog = SettingsDialog(self.root)
        if settings_dialog.show():
            # 如果用户保存了设置，重新加载配置并显示提示信息
            config.reload()
            self.set_status("设置已保存并生效")
            # 更新飞书状态
            self.update_feishu_status()
            self.update_spreadsheet_status()
    
    def open_mapping_config(self):
        """
        打开映射配置界面
        """
        try:
            mapping_config_ui = MappingConfigUI(self.root)
            mapping_config_ui.run()
        except Exception as e:
            messagebox.showerror("错误", f"打开映射配置界面失败: {str(e)}")
    
    def open_oss_upload(self):
        """
        打开阿里云OSS文件上传对话框
        """
        try:
            oss_dialog = OSSUploadDialog(self.root)
            oss_dialog.show()
        except Exception as e:
            messagebox.showerror("错误", f"打开OSS上传功能失败：{str(e)}")
    
    def update_feishu_status(self):
        """
        更新飞书多维表格同步状态显示
        """
        try:
            if config.feishu_enabled:
                # 检查飞书配置是否完整
                app_id = config.feishu_app_id
                app_secret = config.feishu_app_secret
                app_token = config.feishu_app_token
                table_id = config.feishu_table_id
                
                if all([app_id, app_secret, app_token, table_id]):
                    self.feishu_status_var.set("多维表格: 已配置")
                    self.feishu_sync_button.config(state="normal")
                else:
                    self.feishu_status_var.set("多维表格: 配置不完整")
                    self.feishu_sync_button.config(state="disabled")
            else:
                self.feishu_status_var.set("多维表格: 未启用")
                self.feishu_sync_button.config(state="disabled")
        except Exception as e:
            self.feishu_status_var.set("多维表格: 错误")
            self.feishu_sync_button.config(state="disabled")
    
    def update_spreadsheet_status(self):
        """
        更新飞书电子表格同步状态显示
        """
        try:
            if config.is_feishu_spreadsheet_valid():
                # 测试连接
                if self.spreadsheet_sync.test_connection():
                    self.spreadsheet_status_var.set("电子表格: 已配置")
                else:
                    self.spreadsheet_status_var.set("电子表格: 连接失败")
            else:
                self.spreadsheet_status_var.set("电子表格: 未配置")
        except Exception as e:
            self.spreadsheet_status_var.set("电子表格: 错误")
    
    def update_doc_status(self):
        """
        更新飞书云文档同步状态显示
        """
        try:
            if config.is_feishu_doc_valid():
                # 测试连接
                if self.doc_sync.test_connection():
                    self.doc_status_var.set("文档: 已配置")
                else:
                    self.doc_status_var.set("文档: 连接失败")
            else:
                self.doc_status_var.set("文档: 未配置")
        except Exception as e:
            self.doc_status_var.set("文档: 错误")
    
    def sync_to_feishu(self):
        """
        手动同步到飞书
        """
        def sync_worker():
            try:
                self.feishu_status_var.set("飞书: 同步中...")
                self.feishu_sync_button.config(state="disabled")
                
                # 获取未同步的记录
                unsynced_records = db.get_unsynced_records()
                
                if not unsynced_records:
                    self.root.after(0, lambda: messagebox.showinfo("提示", "没有需要同步的记录"))
                    return
                
                # 批量同步
                sync_result = self.feishu_sync.sync_all_records_to_feishu()
                success_count = sync_result['success']
                total_count = success_count + sync_result['failed']
                
                # 更新UI
                self.root.after(0, lambda: self._sync_complete_callback(success_count, total_count))
                
            except Exception as e:
                error_msg = f"同步失败: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
            finally:
                self.root.after(0, self._sync_finally_callback)
        
        # 在后台线程中执行同步
        threading.Thread(target=sync_worker, daemon=True).start()
    
    def _sync_complete_callback(self, success_count: int, total_count: int):
        """
        同步完成回调
        """
        if success_count == total_count:
            messagebox.showinfo("成功", f"成功同步 {success_count} 条记录到飞书")
        else:
            messagebox.showwarning("部分成功", f"成功同步 {success_count}/{total_count} 条记录")
    
    def _sync_finally_callback(self):
        """
        同步结束回调
        """
        self.update_feishu_status()
        self.feishu_sync_button.config(state="normal")
    
    def auto_sync_to_feishu(self, sequence_id: str):
        """
        自动同步单条记录到飞书
        
        Args:
            sequence_id: 记录的序列号
        """
        if not config.feishu_enabled or not config.feishu_auto_sync:
            return
        
        def auto_sync_worker():
            try:
                self.feishu_status_var.set("飞书: 自动同步中...")
                
                # 获取记录详情
                record = db.get_analysis_by_sequence_id(sequence_id)
                if record:
                    success = self.feishu_sync.sync_record_to_feishu(sequence_id)
                    if success:
                        self.feishu_status_var.set("飞书: 同步成功")
                    else:
                        self.feishu_status_var.set("飞书: 同步失败")
                
            except Exception as e:
                self.feishu_status_var.set("飞书: 同步错误")
            finally:
                # 3秒后恢复状态显示
                self.root.after(3000, self.update_feishu_status)
        
        # 在后台线程中执行自动同步
        threading.Thread(target=auto_sync_worker, daemon=True).start()
    
    def auto_sync_to_spreadsheet(self, sequence_id: str):
        """
        自动同步单条记录到飞书电子表格
        
        Args:
            sequence_id: 记录的序列号
        """
        if not config.is_feishu_spreadsheet_valid():
            return
        
        def auto_sync_worker():
            try:
                self.spreadsheet_status_var.set("电子表格: 自动同步中...")
                
                # 同步记录到电子表格
                success = self.spreadsheet_sync.sync_record_to_spreadsheet(sequence_id)
                if success:
                    self.spreadsheet_status_var.set("电子表格: 同步成功")
                else:
                    self.spreadsheet_status_var.set("电子表格: 同步失败")
                
            except Exception as e:
                self.spreadsheet_status_var.set("电子表格: 同步错误")
            finally:
                # 3秒后恢复状态显示
                self.root.after(3000, self.update_spreadsheet_status)
        
        # 在后台线程中执行自动同步
        threading.Thread(target=auto_sync_worker, daemon=True).start()
    
    def set_status(self, message: str):
        """
        设置状态栏消息
        
        Args:
            message: 状态消息
        """
        self.status_var.set(message)
    
    # 移除setup_feishu_table方法，该功能已移至历史记录界面
    
    # 移除_smart_setup_complete_callback方法，该功能已移至历史记录界面
    
    def _setup_table_complete_callback(self, success: bool):
        """
        设置表格完成回调（保留兼容性）
        
        Args:
            success (bool): 是否成功
        """
        if success:
            messagebox.showinfo("成功", "飞书表格结构设置完成！\n\n现在可以正常同步数据到飞书了。")
            self.set_status("飞书表格结构设置完成")
            # 更新飞书状态
            self.update_feishu_status()
        else:
            messagebox.showerror(
                "失败", 
                "飞书表格结构设置失败！\n\n" +
                "请检查：\n" +
                "1. 网络连接是否正常\n" +
                "2. 飞书应用权限是否正确\n" +
                "3. 应用是否已添加为表格协作者\n\n" +
                "详细错误信息请查看控制台日志。"
            )
            self.set_status("飞书表格结构设置失败")
    
    def _setup_table_error_callback(self, error_msg: str):
        """
        设置表格错误回调
        
        Args:
            error_msg (str): 错误信息
        """
        if "FieldNameNotFound" in error_msg:
            messagebox.showerror(
                "字段错误", 
                "飞书表格字段不存在！\n\n" +
                "解决方案：\n" +
                "1. 确保应用已被添加为多维表格协作者\n" +
                "2. 检查应用权限设置\n" +
                "3. 参考 shuoming/FEISHU_FIELD_SETUP_GUIDE.md 手动创建字段\n\n" +
                f"错误详情：{error_msg}"
            )
        else:
            messagebox.showerror(
                "设置失败", 
                f"飞书表格结构设置失败！\n\n错误信息：{error_msg}\n\n" +
                "请检查网络连接和飞书配置。"
            )
        self.set_status("飞书表格结构设置失败")
    
    def toggle_folder_monitoring(self):
        """
        切换文件夹监控状态
        """
        if self.monitor_var.get():
            # 启动监控
            if self.folder_monitor.get_monitored_folders():
                if self.folder_monitor.start_monitoring():
                    self.set_status("文件夹监控已启动")
                else:
                    self.monitor_var.set(False)
                    messagebox.showerror("错误", "启动文件夹监控失败")
            else:
                self.monitor_var.set(False)
                messagebox.showwarning("提示", "请先选择要监控的文件夹")
        else:
            # 停止监控
            self.folder_monitor.stop_monitoring()
            self.set_status("文件夹监控已停止")
    
    def toggle_auto_analysis(self):
        """
        切换自动分析功能
        """
        self.is_auto_analysis_enabled = self.auto_analysis_var.get()
        status = "已启用" if self.is_auto_analysis_enabled else "已禁用"
        self.set_status(f"自动分析功能{status}")
    
    def on_new_file_detected(self, file_path: str):
        """
        检测到新文件时的回调函数
        
        Args:
            file_path: 新检测到的文件路径
        """
        # 在主线程中更新UI
        self.root.after(0, self._handle_new_file_in_main_thread, file_path)
    
    def _handle_new_file_in_main_thread(self, file_path: str):
        """
        在主线程中处理新文件检测
        
        Args:
            file_path: 新检测到的文件路径
        """
        file_name = os.path.basename(file_path)
        self.set_status(f"检测到新文件: {file_name}")
        
        # 检查文件是否已经在列表中，避免重复添加
        if file_path in [f['path'] for f in self.selected_files]:
            self.set_status(f"文件 {file_name} 已在列表中，跳过重复添加")
            return
        
        # 将新文件添加到文件列表
        self.add_files_to_list([file_path])
        
        # 如果启用了自动分析，则自动分析新添加的文件
        if self.is_auto_analysis_enabled:
            # 检查是否有设置的提示词
            current_prompt = self.quick_prompts_manager.get_selected_prompt_text()
            if current_prompt:
                if not self.is_analysis_running:
                    # 检查未分析的文件数量
                    unanalyzed_files = [f for f in self.selected_files if f['status'] in ['就绪', '待分析']]
                    if len(unanalyzed_files) > 1:
                        # 如果有多个未分析文件，启动批量分析
                        self.set_status(f"开始批量分析 {len(unanalyzed_files)} 个文件")
                        self.start_analysis()
                    else:
                        # 只有一个文件，进行单文件分析
                        self.set_status(f"开始分析新文件: {file_name}")
                        self.start_single_file_analysis(file_path)
                else:
                    # 如果正在分析中，设置标记等待当前分析完成后自动开始
                    self.pending_auto_analysis = True
                    self.set_status(f"检测到新文件 {file_name}，将在当前分析完成后自动分析")
            else:
                messagebox.showwarning(
                    "提示", 
                    f"检测到新文件 {file_name}，但未设置分析提示词，无法自动分析"
                )
    
    def on_file_deleted(self, file_path: str):
        """
        检测到文件删除时的回调函数
        
        Args:
            file_path: 被删除的文件路径
        """
        # 在主线程中更新UI
        self.root.after(0, self._handle_file_deletion_in_main_thread, file_path)
    
    def _handle_file_deletion_in_main_thread(self, file_path: str):
        """
        在主线程中处理文件删除
        
        Args:
            file_path: 被删除的文件路径
        """
        file_name = os.path.basename(file_path)
        self.set_status(f"检测到文件删除: {file_name}")
        
        # 从文件列表中移除被删除的文件
        self._remove_file_from_list(file_path)
    
    def _remove_file_from_list(self, file_path: str):
        """
        从文件列表中移除指定文件
        
        Args:
            file_path: 要移除的文件路径
        """
        file_name = os.path.basename(file_path)
        
        # 从selected_files列表中找到并移除匹配的文件
        file_index_to_remove = None
        for i, file_info in enumerate(self.selected_files):
            if file_info['path'] == file_path:
                file_index_to_remove = i
                break
        
        if file_index_to_remove is not None:
            # 从selected_files列表中移除
            self.selected_files.pop(file_index_to_remove)
            
            # 从文件树中移除对应的项目
            tree_items = list(self.file_tree.get_children())
            if file_index_to_remove < len(tree_items):
                self.file_tree.delete(tree_items[file_index_to_remove])
        
        # 如果当前选中的文件被删除，清空当前文件路径
        if self.current_file_path == file_path:
            self.current_file_path = None
            
        # 更新按钮状态
        if not self.selected_files:
            self.analyze_button.config(state="disabled")
    
    def on_monitor_status_update(self, status_message: str):
        """
        监控状态更新回调函数
        
        Args:
            status_message: 状态消息
        """
        # 在主线程中更新UI
        self.root.after(0, self._update_monitor_status_in_main_thread, status_message)
    
    def _update_monitor_status_in_main_thread(self, status_message: str):
        """
        在主线程中更新监控状态显示
        
        Args:
            status_message: 状态消息
        """
        self.monitor_status_label.config(text=f"监控状态: {status_message}")
        
        # 根据状态设置颜色
        if "正在监控" in status_message:
            self.monitor_status_label.config(foreground="green")
        elif "已停止" in status_message or "未启动" in status_message:
            self.monitor_status_label.config(foreground="gray")
        else:
            self.monitor_status_label.config(foreground="orange")
    
    def __del__(self):
        """
        析构函数，确保监控器正确关闭
        """
        if hasattr(self, 'folder_monitor'):
            self.folder_monitor.stop_monitoring()
    
    def run(self):
        """
        运行应用程序
        """
        self.root.mainloop()
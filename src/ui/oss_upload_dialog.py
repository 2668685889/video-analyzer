#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云OSS文件上传对话框

功能：
- 提供图形化界面进行OSS配置和文件上传
- 支持单文件和批量文件上传
- 实时显示上传进度
- 支持拖拽文件上传

作者：AI Assistant
创建时间：2025-01-25
"""

import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict, Any, Optional
import threading
from datetime import datetime

try:
    from ..utils.aliyun_oss_uploader import AliyunOSSUploader
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.aliyun_oss_uploader import AliyunOSSUploader


class OSSUploadDialog:
    """OSS文件上传对话框"""
    
    def __init__(self, parent=None):
        """
        初始化上传对话框
        
        Args:
            parent: 父窗口
        """
        self.parent = parent
        self.uploader = None
        self.upload_thread = None
        self.is_uploading = False
        
        # 初始化文件路径列表
        self.file_paths = []
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent) if parent else tk.Tk()
        self.dialog.title("阿里云OSS文件上传")
        self.dialog.geometry("900x800")  # 增加窗口大小以显示所有内容
        self.dialog.resizable(True, True)
        
        # 设置最小窗口大小
        self.dialog.minsize(800, 700)
        
        # 配置文件路径
        self.config_file = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'oss_config.json')
        
        self._create_widgets()
        self._load_config()
        
        # 绑定关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_widgets(self):
        """创建界面组件（左右布局）"""
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # 左侧列
        main_frame.columnconfigure(1, weight=1)  # 右侧列
        main_frame.rowconfigure(0, weight=1)
        
        # 创建左右两个主要区域
        left_frame = ttk.Frame(main_frame, padding="5")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        right_frame = ttk.Frame(main_frame, padding="5")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # 配置左右框架的网格权重
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(2, weight=1)  # 文件列表区域可扩展
        
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)  # 结果显示区域可扩展
        
        # 左侧区域：配置、文件选择、上传选项
        self._create_config_section(left_frame)
        self._create_file_section(left_frame)
        self._create_options_section(left_frame)
        
        # 右侧区域：进度显示、结果显示、按钮
        self._create_progress_section(right_frame)
        self._create_result_section(right_frame)
        self._create_button_section(right_frame)
    
    def _create_config_section(self, parent):
        """创建OSS配置区域"""
        # 配置标题
        config_label = ttk.Label(parent, text="OSS配置", font=('Arial', 12, 'bold'))
        config_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # 配置框架
        config_frame = ttk.LabelFrame(parent, text="连接配置", padding="10")
        config_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Access Key ID
        ttk.Label(config_frame, text="Access Key ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.access_key_id_var = tk.StringVar()
        self.access_key_id_entry = ttk.Entry(config_frame, textvariable=self.access_key_id_var, width=30)
        self.access_key_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Access Key Secret
        ttk.Label(config_frame, text="Access Key Secret:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.access_key_secret_var = tk.StringVar()
        self.access_key_secret_entry = ttk.Entry(config_frame, textvariable=self.access_key_secret_var, 
                                               width=30, show="*")
        self.access_key_secret_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Endpoint
        ttk.Label(config_frame, text="Endpoint:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.endpoint_var = tk.StringVar(value="oss-cn-hangzhou.aliyuncs.com")
        self.endpoint_entry = ttk.Entry(config_frame, textvariable=self.endpoint_var, width=30)
        self.endpoint_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Bucket Name
        ttk.Label(config_frame, text="Bucket名称:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.bucket_name_var = tk.StringVar()
        self.bucket_name_entry = ttk.Entry(config_frame, textvariable=self.bucket_name_var, width=30)
        self.bucket_name_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # 按钮框架
        button_frame = ttk.Frame(config_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        # 测试连接按钮
        self.test_btn = ttk.Button(button_frame, text="测试连接", command=self._test_connection)
        self.test_btn.grid(row=0, column=0, padx=(0, 10))
        
        # 保存配置按钮
        self.save_config_btn = ttk.Button(button_frame, text="保存配置", command=self._save_config)
        self.save_config_btn.grid(row=0, column=1)
    
    def _create_file_section(self, parent):
        """创建文件选择区域"""
        # 分隔线
        separator1 = ttk.Separator(parent, orient='horizontal')
        separator1.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        # 文件选择框架
        file_frame = ttk.LabelFrame(parent, text="文件选择", padding="10")
        file_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        file_frame.rowconfigure(1, weight=1)
        
        # 文件选择按钮框架
        button_frame = ttk.Frame(file_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.select_files_btn = ttk.Button(button_frame, text="选择文件", command=self._select_files)
        self.select_files_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.select_folder_btn = ttk.Button(button_frame, text="选择文件夹", command=self._select_folder)
        self.select_folder_btn.grid(row=0, column=1, padx=(0, 5))
        
        self.clear_files_btn = ttk.Button(button_frame, text="清空列表", command=self._clear_files)
        self.clear_files_btn.grid(row=0, column=2)
        
        # 文件列表框架
        list_frame = ttk.Frame(file_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview
        columns = ('文件名', '大小', '路径')
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=6)
        
        # 设置列标题
        for col in columns:
            self.file_tree.heading(col, text=col)
        
        # 设置列宽
        self.file_tree.column('文件名', width=120)
        self.file_tree.column('大小', width=80)
        self.file_tree.column('路径', width=200)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 绑定拖拽事件
        self.file_tree.bind('<Button-1>', self._on_file_tree_click)
    
    def _create_options_section(self, parent):
        """创建上传选项区域"""
        # 分隔线
        separator2 = ttk.Separator(parent, orient='horizontal')
        separator2.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        # 上传选项框架
        options_frame = ttk.LabelFrame(parent, text="上传选项", padding="10")
        options_frame.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        
        # 自定义路径
        ttk.Label(options_frame, text="存储路径:").grid(row=0, column=0, sticky=tk.W, pady=2)
        path_frame = ttk.Frame(options_frame)
        path_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        path_frame.columnconfigure(0, weight=1)
        
        self.custom_path_var = tk.StringVar()
        self.custom_path_entry = ttk.Entry(path_frame, textvariable=self.custom_path_var, width=30)
        self.custom_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # 路径说明标签
        path_desc = ttk.Label(path_frame, text="(留空则按日期自动分组，如: videos/2025/01)", 
                            font=('Arial', 8), foreground='gray')
        path_desc.grid(row=1, column=0, sticky=tk.W, pady=(2, 0))
        
        # 文件权限选择
        ttk.Label(options_frame, text="文件权限:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.permission_var = tk.StringVar(value="private")
        permission_frame = ttk.Frame(options_frame)
        permission_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # 权限选择下拉框
        self.permission_combo = ttk.Combobox(permission_frame, textvariable=self.permission_var, 
                                           values=["private", "public-read", "public-read-write"], 
                                           state="readonly", width=15)
        self.permission_combo.grid(row=0, column=0, sticky=tk.W)
        
        # 权限说明标签
        permission_desc = ttk.Label(permission_frame, text="(private: 私有, public-read: 公共读, public-read-write: 公共读写)", 
                                  font=('Arial', 8), foreground='gray')
        permission_desc.grid(row=1, column=0, sticky=tk.W, pady=(2, 0))
        
        # 选项复选框
        checkbox_frame = ttk.Frame(options_frame)
        checkbox_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        self.use_timestamp_var = tk.BooleanVar(value=True)
        self.use_timestamp_cb = ttk.Checkbutton(checkbox_frame, text="文件名添加时间戳", 
                                              variable=self.use_timestamp_var)
        self.use_timestamp_cb.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.overwrite_var = tk.BooleanVar(value=False)
        self.overwrite_cb = ttk.Checkbutton(checkbox_frame, text="覆盖已存在文件", 
                                          variable=self.overwrite_var)
        self.overwrite_cb.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
    
    def _create_progress_section(self, parent):
        """创建进度显示区域"""
        # 进度框架
        progress_frame = ttk.LabelFrame(parent, text="上传进度", padding="10")
        progress_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(1, weight=1)
        
        # 当前文件进度
        ttk.Label(progress_frame, text="当前文件:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.current_file_var = tk.StringVar(value="未开始")
        self.current_file_label = ttk.Label(progress_frame, textvariable=self.current_file_var, wraplength=250)
        self.current_file_label.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # 文件进度条
        self.file_progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.file_progress.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 总体进度
        ttk.Label(progress_frame, text="总体进度:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.overall_progress_var = tk.StringVar(value="0/0")
        self.overall_progress_label = ttk.Label(progress_frame, textvariable=self.overall_progress_var)
        self.overall_progress_label.grid(row=2, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # 总体进度条
        self.overall_progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.overall_progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
    
    def _create_result_section(self, parent):
        """创建结果显示区域"""
        # 结果框架
        result_frame = ttk.LabelFrame(parent, text="上传结果", padding="10")
        result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 结果文本框框架
        text_frame = ttk.Frame(result_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.result_text = tk.Text(text_frame, height=6, wrap=tk.WORD, font=('Arial', 9))
        result_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def _create_button_section(self, parent):
        """创建按钮区域"""
        # 按钮框架
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 开始上传按钮
        self.upload_btn = ttk.Button(button_frame, text="开始上传", command=self._start_upload)
        self.upload_btn.grid(row=0, column=0, padx=(0, 5))
        
        # 停止上传按钮
        self.stop_btn = ttk.Button(button_frame, text="停止上传", command=self._stop_upload, state='disabled')
        self.stop_btn.grid(row=0, column=1, padx=(0, 5))
        
        # 清空结果按钮
        self.clear_result_btn = ttk.Button(button_frame, text="清空结果", command=self._clear_result)
        self.clear_result_btn.grid(row=0, column=2, padx=(0, 5))
        
        # 关闭按钮
        self.close_btn = ttk.Button(button_frame, text="关闭", command=self._on_closing)
        self.close_btn.grid(row=0, column=3)
    
    def _select_files(self):
        """选择文件"""
        files = filedialog.askopenfilenames(
            title="选择要上传的文件",
            filetypes=[
                ("所有文件", "*.*"),
                ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("视频文件", "*.mp4 *.avi *.mov *.wmv *.flv"),
                ("文档文件", "*.pdf *.doc *.docx *.txt *.xlsx")
            ]
        )
        
        if files:
            self._add_files(files)
    
    def _select_folder(self):
        """选择文件夹"""
        folder = filedialog.askdirectory(title="选择要上传的文件夹")
        
        if folder:
            files = []
            for root, dirs, filenames in os.walk(folder):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
            
            if files:
                self._add_files(files)
            else:
                messagebox.showwarning("警告", "选择的文件夹中没有文件")
    
    def _add_files(self, files: List[str]):
        """添加文件到列表"""
        for file_path in files:
            if file_path not in self.file_paths:
                self.file_paths.append(file_path)
                
                # 获取文件信息
                filename = os.path.basename(file_path)
                file_size = self._format_file_size(os.path.getsize(file_path))
                
                # 添加到树形视图
                self.file_tree.insert('', 'end', values=(filename, file_size, file_path))
        
        self._log_result(f"已添加 {len(files)} 个文件到上传列表")
    
    def _clear_files(self):
        """清空文件列表"""
        self.file_paths.clear()
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        self._log_result("已清空文件列表")
    
    def _format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def _test_connection(self):
        """测试OSS连接"""
        try:
            # 获取配置
            config = self._get_config()
            
            # 验证配置完整性
            missing_fields = [k for k, v in config.items() if not v]
            if missing_fields:
                raise ValueError(f"请填写完整的OSS配置信息：{', '.join(missing_fields)}")
            
            # 创建上传器
            uploader = AliyunOSSUploader(**config)
            
            # 显式测试连接
            uploader._test_connection()
            
            # 测试连接成功
            messagebox.showinfo("成功", "OSS连接测试成功！")
            self.uploader = uploader
            self._log_result("OSS连接测试成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"OSS连接测试失败：{str(e)}")
            self._log_result(f"OSS连接测试失败：{str(e)}")
    
    def _get_config(self) -> Dict[str, str]:
        """获取OSS配置"""
        config = {
            'access_key_id': self.access_key_id_var.get().strip(),
            'access_key_secret': self.access_key_secret_var.get().strip(),
            'endpoint': self.endpoint_var.get().strip(),
            'bucket_name': self.bucket_name_var.get().strip(),
            'default_storage_path': self.custom_path_var.get().strip()  # 保存默认存储路径
        }
        
        # 验证必填配置
        required_fields = ['access_key_id', 'access_key_secret', 'endpoint', 'bucket_name']
        for key in required_fields:
            if not config[key]:
                raise ValueError(f"请填写{key}")
        
        return config
    
    def _save_config(self):
        """保存OSS配置"""
        try:
            config = self._get_config()
            
            # 确保配置目录存在
            config_dir = os.path.dirname(self.config_file)
            os.makedirs(config_dir, exist_ok=True)
            
            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("成功", "配置已保存")
            self._log_result("OSS配置已保存")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败：{str(e)}")
    
    def _load_config(self):
        """加载OSS配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.access_key_id_var.set(config.get('access_key_id', ''))
                self.access_key_secret_var.set(config.get('access_key_secret', ''))
                self.endpoint_var.set(config.get('endpoint', 'oss-cn-hangzhou.aliyuncs.com'))
                self.bucket_name_var.set(config.get('bucket_name', ''))
                self.custom_path_var.set(config.get('default_storage_path', ''))  # 加载默认存储路径
                
                self._log_result("已加载OSS配置")
        except Exception as e:
            self._log_result(f"加载配置失败：{str(e)}")
    
    def _start_upload(self):
        """开始上传"""
        if self.is_uploading:
            return
        
        if not self.file_paths:
            messagebox.showwarning("警告", "请先选择要上传的文件")
            return
        
        try:
            # 获取配置并创建上传器
            if not self.uploader:
                config = self._get_config()
                # 验证配置完整性
                missing_fields = [k for k, v in config.items() if not v]
                if missing_fields:
                    raise ValueError(f"请填写完整的OSS配置信息：{', '.join(missing_fields)}")
                
                # 创建上传器（可能会抛出连接异常）
                self.uploader = AliyunOSSUploader(**config)
            
            # 设置上传状态
            self.is_uploading = True
            self.upload_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            
            # 重置进度
            self.file_progress['value'] = 0
            self.overall_progress['value'] = 0
            self.current_file_var.set("准备上传...")
            self.overall_progress_var.set(f"0/{len(self.file_paths)}")
            
            # 启动上传线程
            self.upload_thread = threading.Thread(target=self._upload_files_thread)
            self.upload_thread.daemon = True
            self.upload_thread.start()
            
        except Exception as e:
            messagebox.showerror("错误", f"启动上传失败：{str(e)}")
            self._reset_upload_state()
    
    def _upload_files_thread(self):
        """上传文件线程"""
        try:
            total_files = len(self.file_paths)
            success_count = 0
            
            for i, file_path in enumerate(self.file_paths):
                if not self.is_uploading:
                    break
                
                # 更新当前文件信息
                filename = os.path.basename(file_path)
                self.dialog.after(0, lambda f=filename: self.current_file_var.set(f"正在上传: {f}"))
                self.dialog.after(0, lambda: self.file_progress.config(value=0))
                
                # 进度回调函数
                def progress_callback(bytes_consumed, total_bytes):
                    if total_bytes > 0:
                        percent = (bytes_consumed / total_bytes) * 100
                        self.dialog.after(0, lambda p=percent: self.file_progress.config(value=p))
                
                # 获取存储路径
                storage_path = self.custom_path_var.get().strip()
                # 如果用户设置了存储路径，直接使用；否则传入None让系统自动按日期分组
                custom_path = storage_path if storage_path else None
                
                # 上传文件
                result = self.uploader.upload_file(
                    file_path,
                    custom_path=custom_path,
                    use_timestamp=self.use_timestamp_var.get(),
                    progress_callback=progress_callback,
                    overwrite=self.overwrite_var.get(),
                    permission=self.permission_var.get()  # 添加权限参数
                )
                
                # 更新结果
                if result['success']:
                    success_count += 1
                    self.dialog.after(0, lambda r=result: self._log_upload_success(r))
                else:
                    self.dialog.after(0, lambda r=result: self._log_upload_error(r))
                
                # 更新总体进度
                overall_percent = ((i + 1) / total_files) * 100
                self.dialog.after(0, lambda p=overall_percent: self.overall_progress.config(value=p))
                self.dialog.after(0, lambda c=i+1, t=total_files: 
                                self.overall_progress_var.set(f"{c}/{t}"))
            
            # 上传完成
            if self.is_uploading:
                self.dialog.after(0, lambda: self.current_file_var.set("上传完成"))
                self.dialog.after(0, lambda: self._log_result(
                    f"上传完成！成功: {success_count}/{total_files}"))
            
        except Exception as e:
            error_msg = f"上传过程中发生错误：{str(e)}"
            self.dialog.after(0, lambda msg=error_msg: self._log_result(msg))
        
        finally:
            self.dialog.after(0, self._reset_upload_state)
    
    def _stop_upload(self):
        """停止上传"""
        self.is_uploading = False
        self._log_result("用户取消上传")
    
    def _reset_upload_state(self):
        """重置上传状态"""
        self.is_uploading = False
        self.upload_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
    
    def _log_upload_success(self, result: Dict[str, Any]):
        """记录上传成功"""
        self._log_result(f"✓ {os.path.basename(result['object_key'])} - {result['file_url']}")
    
    def _log_upload_error(self, result: Dict[str, Any]):
        """记录上传错误"""
        filename = os.path.basename(result['file_path'])
        self._log_result(f"✗ {filename} - 错误: {result['error']}")
    
    def _log_result(self, message: str):
        """记录结果信息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.result_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.result_text.see(tk.END)
    
    def _clear_result(self):
        """清空结果"""
        self.result_text.delete(1.0, tk.END)
    
    def _on_file_tree_click(self, event):
        """文件树点击事件"""
        # 可以在这里添加右键菜单等功能
        pass
    
    def _on_closing(self):
        """关闭对话框"""
        if self.is_uploading:
            if messagebox.askquestion("确认", "正在上传文件，确定要关闭吗？") == 'yes':
                self.is_uploading = False
                self.dialog.destroy()
        else:
            self.dialog.destroy()
    
    def show(self):
        """显示对话框"""
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.focus_set()
        
        # 居中显示
        if self.parent:
            self.dialog.geometry("+%d+%d" % (
                self.parent.winfo_rootx() + 50,
                self.parent.winfo_rooty() + 50
            ))
        
        self.dialog.wait_window()


def main():
    """测试函数"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    dialog = OSSUploadDialog()
    dialog.show()


if __name__ == "__main__":
    main()
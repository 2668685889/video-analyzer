#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置对话框模块
实现API密钥配置功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from typing import Optional
from ..utils.config import config

class SettingsDialog:
    """
    设置对话框类
    负责API密钥的配置和管理
    """
    
    def __init__(self, parent):
        """
        初始化设置对话框
        
        Args:
            parent: 父窗口
        """
        self.parent = parent
        self.dialog = None
        self.api_key_var = tk.StringVar()
        self.max_file_size_var = tk.StringVar()
        self.model_var = tk.StringVar()
        
        # 飞书相关变量
        self.feishu_app_id_var = tk.StringVar()
        self.feishu_app_secret_var = tk.StringVar()
        self.feishu_app_token_var = tk.StringVar()
        self.feishu_table_id_var = tk.StringVar()
        self.feishu_enabled_var = tk.BooleanVar()
        self.feishu_auto_sync_var = tk.BooleanVar()
        
        # 飞书电子表格相关变量
        self.feishu_spreadsheet_enabled_var = tk.BooleanVar()
        self.feishu_spreadsheet_token_var = tk.StringVar()
        self.feishu_sheet_id_var = tk.StringVar()
        self.feishu_spreadsheet_auto_sync_var = tk.BooleanVar()
        
        # 飞书云文档相关变量
        self.feishu_doc_enabled_var = tk.BooleanVar()
        self.feishu_doc_token_var = tk.StringVar()
        self.feishu_doc_auto_sync_var = tk.BooleanVar()
        
        self.result = False  # 用于标识是否保存了设置
        
    def show(self) -> bool:
        """
        显示设置对话框
        
        Returns:
            bool: 是否保存了设置
        """
        self.create_dialog()
        self.load_current_settings()
        self.center_dialog()
        
        # 模态对话框
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.wait_window()
        
        return self.result
    
    def create_dialog(self):
        """
        创建对话框界面
        """
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("设置")
        self.dialog.geometry("600x700")
        self.dialog.resizable(True, True)
        
        # 创建主容器框架
        container = ttk.Frame(self.dialog)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建画布和滚动条
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # 配置滚动区域
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # 将滚动框架添加到画布
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 布局画布和滚动条
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 主框架（在滚动框架内）
        main_frame = ttk.Frame(self.scrollable_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="应用程序设置", 
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # API配置区域
        self.create_api_config_area(main_frame)
        
        # 飞书配置区域
        self.create_feishu_config_area(main_frame)
        
        # 高级设置区域
        self.create_advanced_settings_area(main_frame)
        
        # 按钮区域
        self.create_button_area(main_frame)
        
        # 绑定鼠标滚轮事件
        self._bind_mousewheel(canvas)
        
        # 绑定关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
    
    def _bind_mousewheel(self, canvas):
        """
        绑定鼠标滚轮事件
        
        Args:
            canvas: 画布对象
        """
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        # 绑定进入和离开事件
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
    
    def create_api_config_area(self, parent):
        """
        创建API配置区域
        
        Args:
            parent: 父容器
        """
        # API配置框架
        api_frame = ttk.LabelFrame(parent, text="Gemini API配置", padding="15")
        api_frame.pack(fill=tk.X, pady=(0, 15))
        
        # API密钥标签和说明
        key_label = ttk.Label(api_frame, text="API密钥:")
        key_label.pack(anchor=tk.W)
        
        help_label = ttk.Label(
            api_frame, 
            text="请在Google AI Studio (https://aistudio.google.com/) 获取API密钥",
            foreground="gray",
            font=('Arial', 9)
        )
        help_label.pack(anchor=tk.W, pady=(0, 5))
        
        # API密钥输入框
        key_frame = ttk.Frame(api_frame)
        key_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.api_key_entry = ttk.Entry(
            key_frame, 
            textvariable=self.api_key_var,
            show="*",  # 隐藏密钥显示
            font=('Courier', 10)
        )
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # 显示/隐藏按钮
        self.show_key_var = tk.BooleanVar()
        self.show_key_button = ttk.Checkbutton(
            key_frame,
            text="显示",
            variable=self.show_key_var,
            command=self.toggle_key_visibility
        )
        self.show_key_button.pack(side=tk.RIGHT)
        
        # 模型选择
        model_label = ttk.Label(api_frame, text="选择模型:")
        model_label.pack(anchor=tk.W, pady=(10, 0))
        
        model_frame = ttk.Frame(api_frame)
        model_frame.pack(fill=tk.X, pady=(5, 10))
        
        # 获取可用模型
        available_models = config.get_available_models()
        model_values = list(available_models.values())
        
        self.model_combobox = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=model_values,
            state="readonly",
            width=40
        )
        self.model_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 模型说明
        model_help_label = ttk.Label(
            api_frame,
            text="不同模型具有不同的性能和成本特点，推荐使用Gemini 2.5 Flash",
            foreground="gray",
            font=('Arial', 9)
        )
        model_help_label.pack(anchor=tk.W, pady=(0, 10))
        
        # 测试连接按钮
        self.test_button = ttk.Button(
            api_frame,
            text="测试连接",
            command=self.test_api_connection
        )
        self.test_button.pack(anchor=tk.W, pady=(5, 0))
    
    def create_feishu_config_area(self, parent):
        """
        创建飞书配置区域
        
        Args:
            parent: 父容器
        """
        # 飞书配置框架
        feishu_frame = ttk.LabelFrame(parent, text="飞书多维表格配置", padding="15")
        feishu_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 启用飞书同步
        enable_frame = ttk.Frame(feishu_frame)
        enable_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.feishu_enabled_check = ttk.Checkbutton(
            enable_frame,
            text="启用飞书多维表格同步",
            variable=self.feishu_enabled_var,
            command=self.on_feishu_enabled_changed
        )
        self.feishu_enabled_check.pack(side=tk.LEFT)
        
        # 应用ID
        app_id_frame = ttk.Frame(feishu_frame)
        app_id_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(app_id_frame, text="应用ID (App ID):").pack(anchor=tk.W)
        self.feishu_app_id_entry = ttk.Entry(
            app_id_frame,
            textvariable=self.feishu_app_id_var,
            font=('Courier', 10)
        )
        self.feishu_app_id_entry.pack(fill=tk.X, pady=(2, 0))
        
        # 应用密钥
        app_secret_frame = ttk.Frame(feishu_frame)
        app_secret_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(app_secret_frame, text="应用密钥 (App Secret):").pack(anchor=tk.W)
        self.feishu_app_secret_entry = ttk.Entry(
            app_secret_frame,
            textvariable=self.feishu_app_secret_var,
            show="*",
            font=('Courier', 10)
        )
        self.feishu_app_secret_entry.pack(fill=tk.X, pady=(2, 0))
        
        # 应用令牌
        app_token_frame = ttk.Frame(feishu_frame)
        app_token_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(app_token_frame, text="应用令牌 (App Token):").pack(anchor=tk.W)
        self.feishu_app_token_entry = ttk.Entry(
            app_token_frame,
            textvariable=self.feishu_app_token_var,
            font=('Courier', 10)
        )
        self.feishu_app_token_entry.pack(fill=tk.X, pady=(2, 0))
        
        # 表格ID
        table_id_frame = ttk.Frame(feishu_frame)
        table_id_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(table_id_frame, text="表格ID (Table ID):").pack(anchor=tk.W)
        self.feishu_table_id_entry = ttk.Entry(
            table_id_frame,
            textvariable=self.feishu_table_id_var,
            font=('Courier', 10)
        )
        self.feishu_table_id_entry.pack(fill=tk.X, pady=(2, 0))
        
        # 电子表格配置分隔线
        separator = ttk.Separator(feishu_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(10, 10))
        
        # 电子表格配置标题
        spreadsheet_title_label = ttk.Label(
            feishu_frame,
            text="电子表格同步配置",
            font=('Arial', 10, 'bold')
        )
        spreadsheet_title_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 电子表格配置说明
        spreadsheet_note_label = ttk.Label(
            feishu_frame,
            text="注意：电子表格同步功能使用上方的应用ID和应用密钥",
            foreground="blue",
            font=('Arial', 9)
        )
        spreadsheet_note_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 启用电子表格同步
        spreadsheet_enable_frame = ttk.Frame(feishu_frame)
        spreadsheet_enable_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.feishu_spreadsheet_enabled_var = tk.BooleanVar()
        self.feishu_spreadsheet_enabled_check = ttk.Checkbutton(
            spreadsheet_enable_frame,
            text="启用飞书电子表格同步",
            variable=self.feishu_spreadsheet_enabled_var,
            command=self.on_feishu_spreadsheet_enabled_changed
        )
        self.feishu_spreadsheet_enabled_check.pack(side=tk.LEFT)
        
        # 电子表格Token
        spreadsheet_token_frame = ttk.Frame(feishu_frame)
        spreadsheet_token_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(spreadsheet_token_frame, text="电子表格Token:").pack(anchor=tk.W)
        self.feishu_spreadsheet_token_var = tk.StringVar()
        self.feishu_spreadsheet_token_entry = ttk.Entry(
            spreadsheet_token_frame,
            textvariable=self.feishu_spreadsheet_token_var,
            font=('Courier', 10)
        )
        self.feishu_spreadsheet_token_entry.pack(fill=tk.X, pady=(2, 0))
        
        # 工作表ID
        sheet_id_frame = ttk.Frame(feishu_frame)
        sheet_id_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(sheet_id_frame, text="工作表ID (可选，留空将使用第一个工作表):").pack(anchor=tk.W)
        self.feishu_sheet_id_var = tk.StringVar()
        self.feishu_sheet_id_entry = ttk.Entry(
            sheet_id_frame,
            textvariable=self.feishu_sheet_id_var,
            font=('Courier', 10)
        )
        self.feishu_sheet_id_entry.pack(fill=tk.X, pady=(2, 0))
        
        # 自动同步选项
        auto_sync_frame = ttk.Frame(feishu_frame)
        auto_sync_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.feishu_auto_sync_check = ttk.Checkbutton(
            auto_sync_frame,
            text="自动同步新的分析结果到多维表格",
            variable=self.feishu_auto_sync_var
        )
        self.feishu_auto_sync_check.pack(side=tk.LEFT)
        
        # 电子表格自动同步选项
        spreadsheet_auto_sync_frame = ttk.Frame(feishu_frame)
        spreadsheet_auto_sync_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.feishu_spreadsheet_auto_sync_var = tk.BooleanVar()
        self.feishu_spreadsheet_auto_sync_check = ttk.Checkbutton(
            spreadsheet_auto_sync_frame,
            text="自动同步新的分析结果到电子表格",
            variable=self.feishu_spreadsheet_auto_sync_var
        )
        self.feishu_spreadsheet_auto_sync_check.pack(side=tk.LEFT)
        
        # 多维表格按钮
        feishu_btn_frame = ttk.Frame(feishu_frame)
        feishu_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.test_feishu_button = ttk.Button(
            feishu_btn_frame,
            text="测试多维表格连接",
            command=self.test_feishu_connection
        )
        self.test_feishu_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.setup_feishu_button = ttk.Button(
            feishu_btn_frame,
            text="设置多维表格结构",
            command=self.setup_feishu_table
        )
        self.setup_feishu_button.pack(side=tk.LEFT)
        
        # 电子表格按钮
        spreadsheet_btn_frame = ttk.Frame(feishu_frame)
        spreadsheet_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.test_spreadsheet_button = ttk.Button(
            spreadsheet_btn_frame,
            text="测试电子表格连接",
            command=self.test_spreadsheet_connection
        )
        self.test_spreadsheet_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.setup_spreadsheet_button = ttk.Button(
            spreadsheet_btn_frame,
            text="设置电子表格结构",
            command=self.setup_spreadsheet_structure
        )
        self.setup_spreadsheet_button.pack(side=tk.LEFT)
        
        # 云文档配置分隔线
        doc_separator = ttk.Separator(feishu_frame, orient='horizontal')
        doc_separator.pack(fill=tk.X, pady=(10, 10))
        
        # 云文档配置标题
        doc_title_label = ttk.Label(
            feishu_frame,
            text="云文档同步配置",
            font=('Arial', 10, 'bold')
        )
        doc_title_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 云文档配置说明
        doc_note_label = ttk.Label(
            feishu_frame,
            text="注意：云文档同步功能使用上方的应用ID和应用密钥",
            foreground="blue",
            font=('Arial', 9)
        )
        doc_note_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 启用云文档同步
        doc_enable_frame = ttk.Frame(feishu_frame)
        doc_enable_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.feishu_doc_enabled_check = ttk.Checkbutton(
            doc_enable_frame,
            text="启用飞书云文档同步",
            variable=self.feishu_doc_enabled_var,
            command=self.on_feishu_doc_enabled_changed
        )
        self.feishu_doc_enabled_check.pack(side=tk.LEFT)
        
        # 云文档Token
        doc_token_frame = ttk.Frame(feishu_frame)
        doc_token_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(doc_token_frame, text="云文档Token:").pack(anchor=tk.W)
        self.feishu_doc_token_entry = ttk.Entry(
            doc_token_frame,
            textvariable=self.feishu_doc_token_var,
            font=('Courier', 10)
        )
        self.feishu_doc_token_entry.pack(fill=tk.X, pady=(2, 0))
        
        # 云文档自动同步选项
        doc_auto_sync_frame = ttk.Frame(feishu_frame)
        doc_auto_sync_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.feishu_doc_auto_sync_check = ttk.Checkbutton(
            doc_auto_sync_frame,
            text="自动同步新的分析结果到云文档",
            variable=self.feishu_doc_auto_sync_var
        )
        self.feishu_doc_auto_sync_check.pack(side=tk.LEFT)
        
        # 云文档按钮
        doc_btn_frame = ttk.Frame(feishu_frame)
        doc_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.test_doc_button = ttk.Button(
            doc_btn_frame,
            text="测试云文档连接",
            command=self.test_doc_connection
        )
        self.test_doc_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.setup_doc_button = ttk.Button(
            doc_btn_frame,
            text="设置云文档结构",
            command=self.setup_doc_structure
        )
        self.setup_doc_button.pack(side=tk.LEFT)
        
        # 飞书配置说明
        feishu_help_text = (
            "飞书配置说明:\n"
            "• 需要在飞书开放平台创建应用并获取相关凭证\n"
            "• 应用需要开通多维表格、电子表格和云文档相关权限\n"
            "• 多维表格ID可以从多维表格URL中获取\n"
            "• 电子表格Token可以从电子表格URL中获取\n"
            "• 云文档Token可以从云文档URL中获取\n"
            "• 可以选择同步到多维表格、电子表格或云文档，或者多个都启用\n"
            "• 启用后将自动同步视频分析结果到对应的飞书应用"
        )
        
        feishu_help_label = ttk.Label(
            feishu_frame,
            text=feishu_help_text,
            foreground="gray",
            font=('Arial', 9),
            justify=tk.LEFT
        )
        feishu_help_label.pack(anchor=tk.W, pady=(10, 0))
    
    def create_advanced_settings_area(self, parent):
        """
        创建高级设置区域
        
        Args:
            parent: 父容器
        """
        # 高级设置框架
        advanced_frame = ttk.LabelFrame(parent, text="高级设置", padding="15")
        advanced_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 最大文件大小设置
        size_frame = ttk.Frame(advanced_frame)
        size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(size_frame, text="最大文件大小 (MB):").pack(side=tk.LEFT)
        
        self.max_file_size_entry = ttk.Entry(
            size_frame,
            textvariable=self.max_file_size_var,
            width=10
        )
        self.max_file_size_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # 说明文本
        info_text = (
            "提示:\n"
            "• API密钥将安全保存在本地配置文件中\n"
            "• 建议定期更换API密钥以确保安全\n"
            "• 最大文件大小限制可根据网络情况调整"
        )
        
        info_label = ttk.Label(
            advanced_frame,
            text=info_text,
            foreground="gray",
            font=('Arial', 9),
            justify=tk.LEFT
        )
        info_label.pack(anchor=tk.W, pady=(10, 0))
    
    def create_button_area(self, parent):
        """
        创建按钮区域
        
        Args:
            parent: 父容器
        """
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # 取消按钮
        cancel_button = ttk.Button(
            button_frame,
            text="取消",
            command=self.on_cancel
        )
        cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 保存按钮
        save_button = ttk.Button(
            button_frame,
            text="保存",
            command=self.on_save
        )
        save_button.pack(side=tk.RIGHT)
        
        # 重置按钮
        reset_button = ttk.Button(
            button_frame,
            text="重置",
            command=self.on_reset
        )
        reset_button.pack(side=tk.LEFT)
    
    def load_current_settings(self):
        """
        加载当前设置
        """
        # 重新加载配置以获取最新值
        config.reload()
        
        # 加载API密钥
        current_key = config.gemini_api_key
        if current_key and current_key != "your_gemini_api_key_here":
            self.api_key_var.set(current_key)
        
        # 加载最大文件大小
        self.max_file_size_var.set(str(config.max_file_size_mb))
        
        # 加载当前模型
        current_model = config.get_current_model()
        available_models = config.get_available_models()
        if current_model in available_models:
            self.model_var.set(available_models[current_model])
        else:
            # 如果当前模型不在可用列表中，设置为默认模型
            default_model = 'gemini-2.5-flash'
            if default_model in available_models:
                self.model_var.set(available_models[default_model])
        
        # 加载飞书配置
        self.feishu_app_id_var.set(config.feishu_app_id)
        self.feishu_app_secret_var.set(config.feishu_app_secret)
        self.feishu_app_token_var.set(config.feishu_app_token)
        self.feishu_table_id_var.set(config.feishu_table_id)
        self.feishu_enabled_var.set(config.feishu_enabled)
        self.feishu_auto_sync_var.set(config.feishu_auto_sync)
        
        # 加载飞书电子表格配置
        self.feishu_spreadsheet_enabled_var.set(getattr(config, 'feishu_spreadsheet_enabled', False))
        self.feishu_spreadsheet_token_var.set(getattr(config, 'feishu_spreadsheet_token', ''))
        self.feishu_sheet_id_var.set(getattr(config, 'feishu_sheet_id', ''))
        self.feishu_spreadsheet_auto_sync_var.set(getattr(config, 'feishu_spreadsheet_auto_sync', False))
        
        # 加载飞书云文档配置
        self.feishu_doc_enabled_var.set(getattr(config, 'feishu_doc_enabled', False))
        self.feishu_doc_token_var.set(getattr(config, 'feishu_doc_token', ''))
        self.feishu_doc_auto_sync_var.set(getattr(config, 'feishu_doc_auto_sync', False))
        
        # 根据启用状态设置控件状态
        self.on_feishu_enabled_changed()
    
    def toggle_key_visibility(self):
        """
        切换API密钥的显示/隐藏状态
        """
        if self.show_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")
    
    def test_api_connection(self):
        """
        测试API连接
        """
        api_key = self.api_key_var.get().strip()
        
        if not api_key:
            messagebox.showwarning("警告", "请先输入API密钥")
            return
        
        # 禁用测试按钮
        self.test_button.config(state="disabled", text="测试中...")
        
        try:
            # 这里可以添加实际的API测试逻辑
            # 暂时只做基本验证
            if len(api_key) < 20:
                messagebox.showerror("错误", "API密钥格式不正确")
            else:
                messagebox.showinfo("成功", "API密钥格式验证通过")
        except Exception as e:
            messagebox.showerror("错误", f"测试连接失败: {str(e)}")
        finally:
            # 恢复测试按钮
            self.test_button.config(state="normal", text="测试连接")
    
    def on_save(self):
        """
        保存设置
        """
        api_key = self.api_key_var.get().strip()
        max_size = self.max_file_size_var.get().strip()
        selected_model_display = self.model_var.get().strip()
        
        # 验证输入
        if not api_key:
            messagebox.showwarning("警告", "请输入API密钥")
            return
        
        if not selected_model_display:
            messagebox.showwarning("警告", "请选择一个模型")
            return
        
        try:
            max_size_int = int(max_size)
            if max_size_int <= 0:
                raise ValueError("文件大小必须大于0")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的文件大小数值")
            return
        
        # 获取模型ID
        available_models = config.get_available_models()
        selected_model_id = None
        for model_id, display_name in available_models.items():
            if display_name == selected_model_display:
                selected_model_id = model_id
                break
        
        if not selected_model_id:
            messagebox.showerror("错误", "选择的模型无效")
            return
        
        # 保存到.env文件
        try:
            self.save_to_env_file(api_key, max_size_int, selected_model_id)
            
            # 保存飞书云文档配置
            feishu_doc_config = {
                'doc_enabled': self.feishu_doc_enabled_var.get(),
                'doc_token': self.feishu_doc_token_var.get().strip(),
                'doc_auto_sync': self.feishu_doc_auto_sync_var.get()
            }
            
            # 更新配置
            config.update_feishu_config(feishu_doc_config)
            
            messagebox.showinfo("成功", "设置已保存并生效")
            self.result = True
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"保存设置时出错: {str(e)}")
    
    def on_feishu_enabled_changed(self):
        """
        飞书启用状态改变时的处理
        """
        enabled = self.feishu_enabled_var.get()
        
        # 设置相关控件的状态
        state = 'normal' if enabled else 'disabled'
        
        if hasattr(self, 'feishu_app_id_entry'):
            self.feishu_app_id_entry.config(state=state)
            self.feishu_app_secret_entry.config(state=state)
            self.feishu_app_token_entry.config(state=state)
            self.feishu_table_id_entry.config(state=state)
            self.feishu_auto_sync_check.config(state=state)
            self.test_feishu_button.config(state=state)
            self.setup_feishu_button.config(state=state)
    
    def on_feishu_spreadsheet_enabled_changed(self):
        """
        飞书电子表格启用状态改变时的处理
        """
        enabled = self.feishu_spreadsheet_enabled_var.get()
        
        # 设置相关控件的状态
        state = 'normal' if enabled else 'disabled'
        
        if hasattr(self, 'feishu_spreadsheet_token_entry'):
            self.feishu_spreadsheet_token_entry.config(state=state)
            self.feishu_sheet_id_entry.config(state=state)
            self.feishu_spreadsheet_auto_sync_check.config(state=state)
            self.test_spreadsheet_button.config(state=state)
            self.setup_spreadsheet_button.config(state=state)
    
    def on_feishu_doc_enabled_changed(self):
        """
        飞书云文档启用状态改变时的处理
        """
        enabled = self.feishu_doc_enabled_var.get()
        
        # 设置相关控件的状态
        state = 'normal' if enabled else 'disabled'
        
        if hasattr(self, 'feishu_doc_token_entry'):
            self.feishu_doc_token_entry.config(state=state)
            self.feishu_doc_auto_sync_check.config(state=state)
            self.test_doc_button.config(state=state)
            self.setup_doc_button.config(state=state)
    
    def test_feishu_connection(self):
        """
        测试飞书连接
        """
        try:
            from ..api.feishu_client import FeishuClient
            
            app_id = self.feishu_app_id_var.get().strip()
            app_secret = self.feishu_app_secret_var.get().strip()
            
            if not app_id or not app_secret:
                messagebox.showwarning("警告", "请先填写应用ID和应用密钥")
                return
            
            # 创建飞书客户端并测试连接
            client = FeishuClient(app_id, app_secret)
            
            if client.test_connection():
                messagebox.showinfo("成功", "飞书连接测试成功！")
            else:
                messagebox.showerror("失败", "飞书连接测试失败，请检查配置信息")
                
        except Exception as e:
            messagebox.showerror("错误", f"测试连接时出错: {str(e)}")
    
    def setup_feishu_table(self):
        """
        设置飞书表格结构
        """
        try:
            from ..utils.feishu_sync import FeishuSyncService
            
            app_id = self.feishu_app_id_var.get().strip()
            app_secret = self.feishu_app_secret_var.get().strip()
            app_token = self.feishu_app_token_var.get().strip()
            table_id = self.feishu_table_id_var.get().strip()
            
            if not all([app_id, app_secret, app_token]):
                messagebox.showwarning("警告", "请先填写完整的飞书配置信息")
                return
            
            # 创建同步服务并设置表格
            sync_service = FeishuSyncService()
            
            if table_id:
                # 如果有表格ID，验证表格是否存在
                result = sync_service.setup_feishu_table(app_token, table_id)
            else:
                # 如果没有表格ID，创建新表格
                result = sync_service.setup_feishu_table(app_token)
                if result and 'table_id' in result:
                    self.feishu_table_id_var.set(result['table_id'])
            
            if result:
                messagebox.showinfo("成功", "飞书表格设置成功！")
            else:
                messagebox.showerror("失败", "飞书表格设置失败，请检查配置信息")
                
        except Exception as e:
            messagebox.showerror("错误", f"设置表格时出错: {str(e)}")
    
    def test_spreadsheet_connection(self):
        """
        测试飞书电子表格连接
        """
        try:
            from ..api.feishu_client import FeishuClient
            
            app_id = self.feishu_app_id_var.get().strip()
            app_secret = self.feishu_app_secret_var.get().strip()
            spreadsheet_token = self.feishu_spreadsheet_token_var.get().strip()
            
            if not app_id or not app_secret:
                messagebox.showwarning("警告", "请先填写应用ID和应用密钥")
                return
            
            if not spreadsheet_token:
                messagebox.showwarning("警告", "请先填写电子表格Token")
                return
            
            # 创建飞书客户端并测试电子表格连接
            client = FeishuClient(app_id, app_secret)
            
            if client.test_spreadsheet_connection(spreadsheet_token):
                messagebox.showinfo("成功", "飞书电子表格连接测试成功！")
            else:
                messagebox.showerror("失败", "飞书电子表格连接测试失败，请检查配置信息")
                
        except Exception as e:
            messagebox.showerror("错误", f"测试电子表格连接时出错: {str(e)}")
    
    def setup_spreadsheet_structure(self):
        """
        设置飞书电子表格结构
        """
        try:
            from ..utils.feishu_sync import FeishuSyncService
            
            app_id = self.feishu_app_id_var.get().strip()
            app_secret = self.feishu_app_secret_var.get().strip()
            spreadsheet_token = self.feishu_spreadsheet_token_var.get().strip()
            sheet_id = self.feishu_sheet_id_var.get().strip()
            
            if not all([app_id, app_secret, spreadsheet_token]):
                messagebox.showwarning("警告", "请先填写完整的飞书电子表格配置信息")
                return
            
            # 创建同步服务并设置电子表格
            sync_service = FeishuSyncService()
            
            result = sync_service.setup_spreadsheet_structure(spreadsheet_token, sheet_id)
            
            if result:
                messagebox.showinfo("成功", "飞书电子表格结构设置成功！")
            else:
                messagebox.showerror("失败", "飞书电子表格结构设置失败，请检查配置信息")
                
        except Exception as e:
            messagebox.showerror("错误", f"设置电子表格结构时出错: {str(e)}")
    
    def test_doc_connection(self):
        """
        测试飞书云文档连接
        """
        try:
            from ..api.feishu_client import FeishuClient
            
            app_id = self.feishu_app_id_var.get().strip()
            app_secret = self.feishu_app_secret_var.get().strip()
            doc_token = self.feishu_doc_token_var.get().strip()
            
            if not app_id or not app_secret:
                messagebox.showwarning("警告", "请先填写应用ID和应用密钥")
                return
            
            if not doc_token:
                messagebox.showwarning("警告", "请先填写云文档Token")
                return
            
            # 创建飞书客户端并测试云文档连接
            client = FeishuClient(app_id, app_secret)
            
            if client.test_doc_connection(doc_token):
                messagebox.showinfo("成功", "飞书云文档连接测试成功！")
            else:
                messagebox.showerror("失败", "飞书云文档连接测试失败，请检查配置信息")
                
        except Exception as e:
            messagebox.showerror("错误", f"测试云文档连接时出错: {str(e)}")
    
    def setup_doc_structure(self):
        """
        设置飞书云文档结构
        """
        try:
            from ..utils.feishu_sync import FeishuSyncService
            
            app_id = self.feishu_app_id_var.get().strip()
            app_secret = self.feishu_app_secret_var.get().strip()
            doc_token = self.feishu_doc_token_var.get().strip()
            
            if not all([app_id, app_secret, doc_token]):
                messagebox.showwarning("警告", "请先填写完整的飞书云文档配置信息")
                return
            
            # 创建同步服务并设置云文档
            sync_service = FeishuSyncService()
            
            result = sync_service.setup_doc_structure(doc_token)
            
            if result:
                messagebox.showinfo("成功", "飞书云文档结构设置成功！")
            else:
                messagebox.showerror("失败", "飞书云文档结构设置失败，请检查配置信息")
                
        except Exception as e:
            messagebox.showerror("错误", f"设置云文档结构时出错: {str(e)}")
    
    def save_to_env_file(self, api_key: str, max_size: int, model_id: str):
        """
        保存设置到.env文件
        
        Args:
            api_key: API密钥
            max_size: 最大文件大小
            model_id: 选择的模型ID
        """
        env_path = os.path.join(os.getcwd(), '.env')
        
        # 读取现有内容
        env_content = {}
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_content[key.strip()] = value.strip()
        
        # 更新设置
        env_content['GEMINI_API_KEY'] = api_key
        env_content['MAX_FILE_SIZE_MB'] = str(max_size)
        env_content['GEMINI_MODEL'] = model_id
        
        # 更新飞书配置
        env_content['FEISHU_APP_ID'] = self.feishu_app_id_var.get().strip()
        env_content['FEISHU_APP_SECRET'] = self.feishu_app_secret_var.get().strip()
        env_content['FEISHU_APP_TOKEN'] = self.feishu_app_token_var.get().strip()
        env_content['FEISHU_TABLE_ID'] = self.feishu_table_id_var.get().strip()
        env_content['FEISHU_ENABLED'] = 'true' if self.feishu_enabled_var.get() else 'false'
        env_content['FEISHU_AUTO_SYNC'] = 'true' if self.feishu_auto_sync_var.get() else 'false'
        
        # 更新飞书电子表格配置
        env_content['FEISHU_SPREADSHEET_ENABLED'] = 'true' if self.feishu_spreadsheet_enabled_var.get() else 'false'
        env_content['FEISHU_SPREADSHEET_TOKEN'] = self.feishu_spreadsheet_token_var.get().strip()
        env_content['FEISHU_SHEET_ID'] = self.feishu_sheet_id_var.get().strip()
        env_content['FEISHU_SPREADSHEET_AUTO_SYNC'] = 'true' if self.feishu_spreadsheet_auto_sync_var.get() else 'false'
        
        # 更新飞书云文档配置
        env_content['FEISHU_DOC_ENABLED'] = 'true' if self.feishu_doc_enabled_var.get() else 'false'
        env_content['FEISHU_DOC_TOKEN'] = self.feishu_doc_token_var.get().strip()
        env_content['FEISHU_DOC_AUTO_SYNC'] = 'true' if self.feishu_doc_auto_sync_var.get() else 'false'
        
        # 写入文件
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("# Gemini API配置\n")
            f.write("# 请将此文件复制为.env并填入您的API密钥\n")
            f.write(f"GEMINI_API_KEY={env_content.get('GEMINI_API_KEY', '')}\n")
            f.write(f"MAX_FILE_SIZE_MB={env_content.get('MAX_FILE_SIZE_MB', '100')}\n")
            f.write(f"GEMINI_MODEL={env_content.get('GEMINI_MODEL', 'gemini-2.5-flash')}\n")
            f.write("\n# 飞书多维表格配置\n")
            f.write(f"FEISHU_APP_ID={env_content.get('FEISHU_APP_ID', '')}\n")
            f.write(f"FEISHU_APP_SECRET={env_content.get('FEISHU_APP_SECRET', '')}\n")
            f.write(f"FEISHU_APP_TOKEN={env_content.get('FEISHU_APP_TOKEN', '')}\n")
            f.write(f"FEISHU_TABLE_ID={env_content.get('FEISHU_TABLE_ID', '')}\n")
            f.write(f"FEISHU_ENABLED={env_content.get('FEISHU_ENABLED', 'false')}\n")
            f.write(f"FEISHU_AUTO_SYNC={env_content.get('FEISHU_AUTO_SYNC', 'true')}\n")
            f.write("\n# 飞书电子表格配置\n")
            f.write(f"FEISHU_SPREADSHEET_ENABLED={env_content.get('FEISHU_SPREADSHEET_ENABLED', 'false')}\n")
            f.write(f"FEISHU_SPREADSHEET_TOKEN={env_content.get('FEISHU_SPREADSHEET_TOKEN', '')}\n")
            f.write(f"FEISHU_SHEET_ID={env_content.get('FEISHU_SHEET_ID', '')}\n")
            f.write(f"FEISHU_SPREADSHEET_AUTO_SYNC={env_content.get('FEISHU_SPREADSHEET_AUTO_SYNC', 'false')}\n")
            f.write("\n# 飞书云文档配置\n")
            f.write(f"FEISHU_DOC_ENABLED={env_content.get('FEISHU_DOC_ENABLED', 'false')}\n")
            f.write(f"FEISHU_DOC_TOKEN={env_content.get('FEISHU_DOC_TOKEN', '')}\n")
            f.write(f"FEISHU_DOC_AUTO_SYNC={env_content.get('FEISHU_DOC_AUTO_SYNC', 'false')}\n")
            f.write("\n# 可选配置\n")
            f.write("# SUPPORTED_VIDEO_FORMATS=mp4,avi,mov,mkv,webm\n")
    
    def on_reset(self):
        """
        重置设置
        """
        if messagebox.askyesno("确认", "确定要重置所有设置吗？"):
            self.api_key_var.set("")
            self.max_file_size_var.set("100")
            self.model_var.set("gemini-2.5-flash - 快速响应，适合日常使用")
            self.show_key_var.set(False)
            
            # 重置飞书配置
            self.feishu_app_id_var.set("")
            self.feishu_app_secret_var.set("")
            self.feishu_app_token_var.set("")
            self.feishu_table_id_var.set("")
            self.feishu_enabled_var.set(False)
            self.feishu_auto_sync_var.set(True)
            
            # 重置飞书电子表格配置
            self.feishu_spreadsheet_enabled_var.set(False)
            self.feishu_spreadsheet_token_var.set("")
            self.feishu_sheet_id_var.set("")
            self.feishu_spreadsheet_auto_sync_var.set(False)
            
            # 重置飞书云文档配置
            self.feishu_doc_enabled_var.set(False)
            self.feishu_doc_token_var.set("")
            self.feishu_doc_auto_sync_var.set(False)
            
            self.toggle_key_visibility()
            self.on_feishu_enabled_changed()
            self.on_feishu_spreadsheet_enabled_changed()
            self.on_feishu_doc_enabled_changed()
    
    def on_cancel(self):
        """
        取消设置
        """
        self.result = False
        self.dialog.destroy()
    
    def center_dialog(self):
        """
        将对话框居中显示
        """
        self.dialog.update_idletasks()
        
        # 获取对话框大小
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # 获取父窗口位置和大小
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # 计算居中位置
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
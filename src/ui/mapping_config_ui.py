#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
映射配置UI界面
用于管理自定义字段映射配置的图形界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.mapping_config_manager import MappingConfigManager
from utils.custom_field_mapper import CustomFieldMapper

class MappingConfigUI:
    """映射配置UI类"""
    
    def __init__(self, parent=None):
        """
        初始化映射配置UI
        
        Args:
            parent: 父窗口
        """
        self.parent = parent
        self.config_manager = MappingConfigManager()
        self.config_manager.initialize_default_config()
        self.custom_mapper = CustomFieldMapper()
        
        # 初始化UI
        self.setup_ui()
        self.load_config_list()
        
    def setup_ui(self):
        """
        设置UI界面
        """
        if self.parent:
            self.window = tk.Toplevel(self.parent)
        else:
            self.window = tk.Tk()
        
        self.window.title("字段映射配置管理")
        self.window.geometry("1200x800")
        self.window.resizable(True, True)
        
        # 设置最小窗口大小
        self.window.minsize(1000, 600)
        
        # 创建主框架
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建左侧配置列表
        self.create_config_list_frame(main_frame)
        
        # 创建右侧配置编辑器
        self.create_config_editor_frame(main_frame)
        
        # 创建底部按钮栏
        self.create_button_frame(main_frame)
    
    def create_config_list_frame(self, parent):
        """
        创建配置列表框架
        
        Args:
            parent: 父容器
        """
        # 左侧框架
        left_frame = ttk.LabelFrame(parent, text="配置列表", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        left_frame.configure(width=300)
        
        # 配置列表
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview
        columns = ('name', 'description')
        self.config_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题
        self.config_tree.heading('name', text='配置名称')
        self.config_tree.heading('description', text='描述')
        
        # 设置列宽
        self.config_tree.column('name', width=150)
        self.config_tree.column('description', width=200)
        
        # 添加滚动条
        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.config_tree.yview)
        self.config_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.config_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.config_tree.bind('<<TreeviewSelect>>', self.on_config_select)
        
        # 配置操作按钮
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="新建配置", command=self.new_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="删除配置", command=self.delete_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="刷新", command=self.load_config_list).pack(side=tk.LEFT)
        
        # 导入导出按钮
        io_frame = ttk.Frame(left_frame)
        io_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(io_frame, text="导入配置", command=self.import_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(io_frame, text="导出配置", command=self.export_config).pack(side=tk.LEFT)
    
    def create_config_editor_frame(self, parent):
        """
        创建配置编辑器框架
        
        Args:
            parent: 父容器
        """
        # 右侧框架
        right_frame = ttk.LabelFrame(parent, text="配置编辑器", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 创建Notebook
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本信息标签页
        self.create_basic_info_tab()
        
        # AI字段标签页
        self.create_ai_fields_tab()
        
        # 飞书映射标签页
        self.create_feishu_mapping_tab()
        
        # 转换规则标签页
        self.create_transformation_rules_tab()
    
    def create_basic_info_tab(self):
        """
        创建基本信息标签页
        """
        basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(basic_frame, text="基本信息")
        
        # 配置名称
        ttk.Label(basic_frame, text="配置名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.config_name_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=self.config_name_var, width=50).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 版本
        ttk.Label(basic_frame, text="版本:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.version_var = tk.StringVar(value="1.0.0")
        ttk.Entry(basic_frame, textvariable=self.version_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 描述
        ttk.Label(basic_frame, text="描述:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        self.description_text = tk.Text(basic_frame, width=60, height=5)
        self.description_text.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 创建时间（只读）
        ttk.Label(basic_frame, text="创建时间:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.created_at_var = tk.StringVar()
        ttk.Label(basic_frame, textvariable=self.created_at_var).grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
    
    def create_ai_fields_tab(self):
        """
        创建AI字段标签页
        """
        ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(ai_frame, text="AI字段")
        
        # 工具栏
        toolbar = ttk.Frame(ai_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="添加字段", command=self.add_ai_field).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="删除字段", command=self.delete_ai_field).pack(side=tk.LEFT, padx=(0, 5))
        
        # 保存按钮（右对齐）
        ttk.Button(toolbar, text="保存配置", command=self.save_config).pack(side=tk.RIGHT)
        
        # AI字段列表
        ai_list_frame = ttk.Frame(ai_frame)
        ai_list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('field_name', 'type', 'description', 'required')
        self.ai_fields_tree = ttk.Treeview(ai_list_frame, columns=columns, show='headings')
        
        # 设置列标题
        self.ai_fields_tree.heading('field_name', text='字段名')
        self.ai_fields_tree.heading('type', text='类型')
        self.ai_fields_tree.heading('description', text='描述')
        self.ai_fields_tree.heading('required', text='必需')
        
        # 设置列宽
        self.ai_fields_tree.column('field_name', width=150)
        self.ai_fields_tree.column('type', width=100)
        self.ai_fields_tree.column('description', width=200)
        self.ai_fields_tree.column('required', width=80)
        
        # 添加滚动条
        ai_scroll = ttk.Scrollbar(ai_list_frame, orient=tk.VERTICAL, command=self.ai_fields_tree.yview)
        self.ai_fields_tree.configure(yscrollcommand=ai_scroll.set)
        
        self.ai_fields_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ai_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击编辑事件
        self.ai_fields_tree.bind('<Double-1>', self.edit_ai_field)
    
    def create_feishu_mapping_tab(self):
        """
        创建飞书映射标签页
        """
        feishu_frame = ttk.Frame(self.notebook)
        self.notebook.add(feishu_frame, text="飞书映射")
        
        # 工具栏
        toolbar = ttk.Frame(feishu_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="添加映射", command=self.add_feishu_mapping).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="删除映射", command=self.delete_feishu_mapping).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="自动匹配", command=self.auto_match_mappings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="保存配置", command=self.save_config).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 飞书映射列表
        feishu_list_frame = ttk.Frame(feishu_frame)
        feishu_list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ai_field', 'feishu_name', 'feishu_type')
        self.feishu_mapping_tree = ttk.Treeview(feishu_list_frame, columns=columns, show='headings')
        
        # 设置列标题
        self.feishu_mapping_tree.heading('ai_field', text='AI字段')
        self.feishu_mapping_tree.heading('feishu_name', text='飞书字段名')
        self.feishu_mapping_tree.heading('feishu_type', text='飞书字段类型')
        
        # 设置列宽
        self.feishu_mapping_tree.column('ai_field', width=200)
        self.feishu_mapping_tree.column('feishu_name', width=200)
        self.feishu_mapping_tree.column('feishu_type', width=150)
        
        # 添加滚动条
        feishu_scroll = ttk.Scrollbar(feishu_list_frame, orient=tk.VERTICAL, command=self.feishu_mapping_tree.yview)
        self.feishu_mapping_tree.configure(yscrollcommand=feishu_scroll.set)
        
        self.feishu_mapping_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        feishu_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击编辑事件
        self.feishu_mapping_tree.bind('<Double-1>', self.edit_feishu_mapping)
    
    def create_transformation_rules_tab(self):
        """
        创建转换规则标签页
        """
        rules_frame = ttk.Frame(self.notebook)
        self.notebook.add(rules_frame, text="转换规则")
        
        # 工具栏
        toolbar = ttk.Frame(rules_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="添加规则", command=self.add_transformation_rule).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="删除规则", command=self.delete_transformation_rule).pack(side=tk.LEFT, padx=(0, 5))
        
        # 保存按钮（右对齐）
        ttk.Button(toolbar, text="保存配置", command=self.save_config).pack(side=tk.RIGHT)
        
        # 转换规则列表
        rules_list_frame = ttk.Frame(rules_frame)
        rules_list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('field_name', 'rule_type', 'parameters')
        self.rules_tree = ttk.Treeview(rules_list_frame, columns=columns, show='headings')
        
        # 设置列标题
        self.rules_tree.heading('field_name', text='字段名')
        self.rules_tree.heading('rule_type', text='规则类型')
        self.rules_tree.heading('parameters', text='参数')
        
        # 设置列宽
        self.rules_tree.column('field_name', width=150)
        self.rules_tree.column('rule_type', width=120)
        self.rules_tree.column('parameters', width=300)
        
        # 添加滚动条
        rules_scroll = ttk.Scrollbar(rules_list_frame, orient=tk.VERTICAL, command=self.rules_tree.yview)
        self.rules_tree.configure(yscrollcommand=rules_scroll.set)
        
        self.rules_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rules_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击编辑事件
        self.rules_tree.bind('<Double-1>', self.edit_transformation_rule)
    
    def create_button_frame(self, parent):
        """
        创建底部按钮框架
        
        Args:
            parent: 父容器
        """
        # 创建分隔线
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill=tk.X, pady=(10, 5))
        
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(5, 10))
        
        # 左侧按钮组（导入导出）
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)
        
        ttk.Button(left_buttons, text="导入配置", command=self.import_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(left_buttons, text="导出配置", command=self.export_config).pack(side=tk.LEFT, padx=(0, 5))
        
        # 右对齐按钮组（主要操作）
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(right_buttons, text="保存配置", command=self.save_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_buttons, text="验证配置", command=self.validate_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_buttons, text="测试映射", command=self.test_mapping, width=10).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_buttons, text="关闭", command=self.close_window).pack(side=tk.LEFT)
    
    def load_config_list(self):
        """
        加载配置列表
        """
        # 清空现有项目
        for item in self.config_tree.get_children():
            self.config_tree.delete(item)
        
        # 加载配置
        configs = self.config_manager.list_configs()
        for config in configs:
            # 为默认配置添加标记
            config_name = config['name']
            if config.get('is_default', False):
                config_name = f"[默认] {config_name}"
            
            self.config_tree.insert('', 'end', 
                                   values=(config_name, config['description']))
    
    def on_config_select(self, event):
        """
        配置选择事件处理
        
        Args:
            event: 事件对象
        """
        selection = self.config_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.config_tree.item(item, 'values')
        if not values:
            return
        
        config_name = values[0]  # 第一列是配置名称
        
        # 移除默认配置的标记
        if config_name.startswith('[默认] '):
            config_name = config_name[5:]
        
        self.load_config_to_editor(config_name)
    
    def load_config_to_editor(self, config_name: str):
        """
        加载配置到编辑器
        
        Args:
            config_name: 配置名称
        """
        if config_name == "default":
            config = self.config_manager.create_default_config()
        else:
            config = self.config_manager.load_config(config_name)
        
        if not config:
            messagebox.showerror("错误", f"无法加载配置: {config_name}")
            return
        
        # 加载基本信息
        self.config_name_var.set(config.get('config_name', ''))
        self.version_var.set(config.get('version', '1.0.0'))
        self.description_text.delete('1.0', tk.END)
        self.description_text.insert('1.0', config.get('description', ''))
        self.created_at_var.set(config.get('created_at', ''))
        
        # 加载AI字段
        self.load_ai_fields(config.get('ai_fields', {}))
        
        # 加载飞书映射
        self.load_feishu_mappings(config.get('feishu_mappings', {}))
        
        # 加载转换规则
        self.load_transformation_rules(config.get('transformation_rules', {}))
    
    def load_ai_fields(self, ai_fields: Dict[str, Any]):
        """
        加载AI字段到列表
        
        Args:
            ai_fields: AI字段字典
        """
        # 清空现有项目
        for item in self.ai_fields_tree.get_children():
            self.ai_fields_tree.delete(item)
        
        # 添加字段
        for field_name, field_info in ai_fields.items():
            self.ai_fields_tree.insert('', 'end', values=(
                field_name,
                field_info.get('type', 'text'),
                field_info.get('description', ''),
                '是' if field_info.get('required', False) else '否'
            ))
    
    def load_feishu_mappings(self, feishu_mappings: Dict[str, Any]):
        """
        加载飞书映射到列表
        
        Args:
            feishu_mappings: 飞书映射字典
        """
        # 清空现有项目
        for item in self.feishu_mapping_tree.get_children():
            self.feishu_mapping_tree.delete(item)
        
        # 添加映射
        for ai_field, mapping_info in feishu_mappings.items():
            self.feishu_mapping_tree.insert('', 'end', values=(
                ai_field,
                mapping_info.get('field_name', ''),
                mapping_info.get('field_type', 'text')
            ))
    
    def load_transformation_rules(self, transformation_rules: Dict[str, Any]):
        """
        加载转换规则到列表
        
        Args:
            transformation_rules: 转换规则字典
        """
        # 清空现有项目
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
        
        # 添加规则
        for field_name, rule_info in transformation_rules.items():
            rule_type = rule_info.get('type', '')
            parameters = ', '.join([f"{k}={v}" for k, v in rule_info.items() if k != 'type'])
            
            self.rules_tree.insert('', 'end', values=(
                field_name,
                rule_type,
                parameters
            ))
    
    def new_config(self):
        """
        创建新配置
        """
        # 清空编辑器
        self.config_name_var.set("新配置")
        self.version_var.set("1.0.0")
        self.description_text.delete('1.0', tk.END)
        self.created_at_var.set("")
        
        # 清空所有列表
        for item in self.ai_fields_tree.get_children():
            self.ai_fields_tree.delete(item)
        for item in self.feishu_mapping_tree.get_children():
            self.feishu_mapping_tree.delete(item)
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
    
    def delete_config(self):
        """
        删除选中的配置
        """
        selection = self.config_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的配置")
            return
        
        item = selection[0]
        config_name = self.config_tree.item(item, 'text')
        
        # 移除默认配置的标记
        if config_name.startswith('[默认] '):
            messagebox.showwarning("警告", "不能删除默认配置")
            return
        
        # 确认删除
        if messagebox.askyesno("确认删除", f"确定要删除配置 '{config_name}' 吗？"):
            if self.config_manager.delete_config(config_name):
                messagebox.showinfo("成功", "配置删除成功")
                self.load_config_list()
            else:
                messagebox.showerror("错误", "配置删除失败")
    
    def save_config(self):
        """
        保存当前配置
        """
        try:
            config = self.get_current_config()
            config_name = self.config_name_var.get().strip()
            
            if not config_name:
                messagebox.showwarning("警告", "请输入配置名称")
                return
            
            # 验证配置
            errors = self.config_manager.validate_config(config)
            if errors:
                messagebox.showerror("配置验证失败", "\n".join(errors))
                return
            
            # 保存配置
            saved_path = self.config_manager.save_config(config, config_name)
            messagebox.showinfo("成功", f"配置已保存到: {saved_path}")
            self.load_config_list()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")
    
    def get_current_config(self) -> Dict[str, Any]:
        """
        获取当前编辑器中的配置
        
        Returns:
            配置字典
        """
        from datetime import datetime
        
        config = {
            "config_name": self.config_name_var.get().strip(),
            "version": self.version_var.get().strip(),
            "description": self.description_text.get('1.0', tk.END).strip(),
            "created_at": self.created_at_var.get() or datetime.now().isoformat(),
            "ai_fields": {},
            "feishu_mappings": {},
            "transformation_rules": {}
        }
        
        # 获取AI字段
        for item in self.ai_fields_tree.get_children():
            values = self.ai_fields_tree.item(item, 'values')
            field_name = values[0]
            config["ai_fields"][field_name] = {
                "type": values[1],
                "description": values[2],
                "required": values[3] == '是'
            }
        
        # 获取飞书映射
        for item in self.feishu_mapping_tree.get_children():
            values = self.feishu_mapping_tree.item(item, 'values')
            ai_field = values[0]
            config["feishu_mappings"][ai_field] = {
                "field_name": values[1],
                "field_type": values[2]
            }
        
        # 获取转换规则
        for item in self.rules_tree.get_children():
            values = self.rules_tree.item(item, 'values')
            field_name = values[0]
            rule_type = values[1]
            parameters_str = values[2]
            
            rule_info = {"type": rule_type}
            
            # 解析参数
            if parameters_str:
                for param in parameters_str.split(', '):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        # 尝试转换为适当的类型
                        try:
                            if value.isdigit():
                                value = int(value)
                            elif value.lower() in ('true', 'false'):
                                value = value.lower() == 'true'
                        except:
                            pass
                        rule_info[key.strip()] = value.strip() if isinstance(value, str) else value
            
            config["transformation_rules"][field_name] = rule_info
        
        return config
    
    def validate_config(self):
        """
        验证当前配置
        """
        try:
            config = self.get_current_config()
            errors = self.config_manager.validate_config(config)
            
            if errors:
                messagebox.showerror("配置验证失败", "\n".join(errors))
            else:
                messagebox.showinfo("验证成功", "配置验证通过")
                
        except Exception as e:
            messagebox.showerror("错误", f"验证配置失败: {str(e)}")
    
    def test_mapping(self):
        """
        测试映射功能
        """
        try:
            config = self.get_current_config()
            
            # 创建测试数据
            test_data = {}
            for field_name, field_info in config.get("ai_fields", {}).items():
                if field_info.get("type") == "text":
                    test_data[field_name] = f"测试{field_info.get('description', field_name)}"
                elif field_info.get("type") == "number":
                    test_data[field_name] = 123
                elif field_info.get("type") == "boolean":
                    test_data[field_name] = True
                elif field_info.get("type") == "date":
                    test_data[field_name] = "2024-01-01"
                else:
                    test_data[field_name] = "测试数据"
            
            # 使用自定义映射器进行转换
            mapper = CustomFieldMapper()
            mapper.load_config_from_dict(config)
            
            result = mapper.transform_data(test_data)
            
            # 显示详细的测试结果
            self._show_detailed_test_result(config, test_data, result)
            
        except Exception as e:
            messagebox.showerror("错误", f"测试映射失败: {str(e)}")
    
    def _show_detailed_test_result(self, config: Dict[str, Any], test_data: Dict[str, Any], result: Dict[str, Any]):
        """
        显示详细的测试结果
        
        Args:
            config: 配置信息
            test_data: 测试数据
            result: 映射结果
        """
        result_window = tk.Toplevel(self.window)
        result_window.title("映射测试结果")
        result_window.geometry("800x600")
        result_window.resizable(True, True)
        
        # 创建主框架
        main_frame = ttk.Frame(result_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建标签页
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 概览标签页
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="测试概览")
        self._create_overview_tab(overview_frame, config, test_data, result)
        
        # 字段映射标签页
        mapping_frame = ttk.Frame(notebook)
        notebook.add(mapping_frame, text="字段映射详情")
        self._create_mapping_details_tab(mapping_frame, config, test_data, result)
        
        # 原始数据标签页
        raw_data_frame = ttk.Frame(notebook)
        notebook.add(raw_data_frame, text="原始数据")
        self._create_raw_data_tab(raw_data_frame, test_data, result)
        
        # 添加关闭按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="关闭", command=result_window.destroy).pack(side=tk.RIGHT)
    
    def _create_overview_tab(self, parent, config: Dict[str, Any], test_data: Dict[str, Any], result: Dict[str, Any]):
        """
        创建概览标签页
        
        Args:
            parent: 父容器
            config: 配置信息
            test_data: 测试数据
            result: 映射结果
        """
        # 创建滚动框架
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 配置信息
        info_frame = ttk.LabelFrame(scrollable_frame, text="配置信息")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_frame, text=f"配置名称: {config.get('config_name', '未命名')}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"版本: {config.get('version', '1.0')}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"描述: {config.get('description', '无描述')}").pack(anchor=tk.W, padx=5, pady=2)
        
        # 统计信息
        stats_frame = ttk.LabelFrame(scrollable_frame, text="统计信息")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ai_fields_count = len(config.get('ai_fields', {}))
        feishu_mappings_count = len(config.get('feishu_mappings', {}))
        transformation_rules_count = len(config.get('transformation_rules', {}))
        
        ttk.Label(stats_frame, text=f"AI字段数量: {ai_fields_count}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, text=f"飞书映射数量: {feishu_mappings_count}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, text=f"转换规则数量: {transformation_rules_count}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, text=f"测试数据字段数量: {len(test_data)}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, text=f"映射结果字段数量: {len(result)}").pack(anchor=tk.W, padx=5, pady=2)
        
        # 测试状态
        status_frame = ttk.LabelFrame(scrollable_frame, text="测试状态")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        if result:
            status_text = "✅ 映射测试成功"
            status_color = "green"
        else:
            status_text = "❌ 映射测试失败"
            status_color = "red"
        
        status_label = ttk.Label(status_frame, text=status_text, foreground=status_color)
        status_label.pack(anchor=tk.W, padx=5, pady=2)
    
    def _create_mapping_details_tab(self, parent, config: Dict[str, Any], test_data: Dict[str, Any], result: Dict[str, Any]):
        """
        创建字段映射详情标签页
        
        Args:
            parent: 父容器
            config: 配置信息
            test_data: 测试数据
            result: 映射结果
        """
        # 创建树形视图
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建树形控件
        columns = ("ai_field", "test_value", "feishu_field", "mapped_value", "status")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # 设置列标题
        tree.heading("ai_field", text="AI字段")
        tree.heading("test_value", text="测试值")
        tree.heading("feishu_field", text="飞书字段")
        tree.heading("mapped_value", text="映射值")
        tree.heading("status", text="状态")
        
        # 设置列宽
        tree.column("ai_field", width=150)
        tree.column("test_value", width=150)
        tree.column("feishu_field", width=150)
        tree.column("mapped_value", width=150)
        tree.column("status", width=100)
        
        # 添加滚动条
        scrollbar_tree = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar_tree.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar_tree.pack(side="right", fill="y")
        
        # 填充数据
        feishu_mappings = config.get('feishu_mappings', {})
        
        for ai_field, test_value in test_data.items():
            # 获取飞书字段映射
            feishu_mapping = feishu_mappings.get(ai_field, {})
            if isinstance(feishu_mapping, dict):
                feishu_field = feishu_mapping.get('field_name', '未映射')
            else:
                feishu_field = str(feishu_mapping) if feishu_mapping else '未映射'
            
            # 获取映射后的值
            mapped_value = result.get(feishu_field, '未找到')
            
            # 确定状态
            if feishu_field == '未映射':
                status = "❌ 未映射"
            elif mapped_value == '未找到':
                status = "⚠️ 映射失败"
            else:
                status = "✅ 成功"
            
            tree.insert("", "end", values=(
                ai_field,
                str(test_value),
                feishu_field,
                str(mapped_value),
                status
            ))
    
    def _create_raw_data_tab(self, parent, test_data: Dict[str, Any], result: Dict[str, Any]):
        """
        创建原始数据标签页
        
        Args:
            parent: 父容器
            test_data: 测试数据
            result: 映射结果
        """
        # 创建文本框架
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建文本控件
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Courier', 10))
        scrollbar_text = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar_text.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar_text.pack(side="right", fill="y")
        
        # 插入数据
        text_widget.insert(tk.END, "=" * 50 + "\n")
        text_widget.insert(tk.END, "测试数据 (AI字段)\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        text_widget.insert(tk.END, json.dumps(test_data, ensure_ascii=False, indent=2))
        
        text_widget.insert(tk.END, "\n\n" + "=" * 50 + "\n")
        text_widget.insert(tk.END, "映射结果 (飞书字段)\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        text_widget.insert(tk.END, json.dumps(result, ensure_ascii=False, indent=2))
        
        text_widget.config(state=tk.DISABLED)
    
    def import_config(self):
        """
        导入配置文件
        """
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            config_name = self.config_manager.import_config(file_path)
            if config_name:
                messagebox.showinfo("成功", f"配置 '{config_name}' 导入成功")
                self.load_config_list()
            else:
                messagebox.showerror("错误", "配置导入失败")
    
    def export_config(self):
        """
        导出选中的配置
        """
        selection = self.config_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要导出的配置")
            return
        
        item = selection[0]
        config_name = self.config_tree.item(item, 'text')
        
        # 移除默认配置的标记
        if config_name.startswith('[默认] '):
            config_name = config_name[5:]
        
        file_path = filedialog.asksaveasfilename(
            title="保存配置文件",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            if self.config_manager.export_config(config_name, file_path):
                messagebox.showinfo("成功", f"配置已导出到: {file_path}")
            else:
                messagebox.showerror("错误", "配置导出失败")
    
    def add_ai_field(self):
        """
        添加AI字段
        """
        dialog = FieldEditDialog(self.window, "添加AI字段")
        if dialog.result:
            field_info = dialog.result
            self.ai_fields_tree.insert('', 'end', values=(
                field_info['name'],
                field_info['type'],
                field_info['description'],
                '是' if field_info['required'] else '否'
            ))
    
    def edit_ai_field(self, event):
        """
        编辑AI字段
        
        Args:
            event: 事件对象
        """
        selection = self.ai_fields_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.ai_fields_tree.item(item, 'values')
        
        current_data = {
            'name': values[0],
            'type': values[1],
            'description': values[2],
            'required': values[3] == '是'
        }
        
        dialog = FieldEditDialog(self.window, "编辑AI字段", current_data)
        if dialog.result:
            field_info = dialog.result
            self.ai_fields_tree.item(item, values=(
                field_info['name'],
                field_info['type'],
                field_info['description'],
                '是' if field_info['required'] else '否'
            ))
    
    def delete_ai_field(self):
        """
        删除AI字段
        """
        selection = self.ai_fields_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的字段")
            return
        
        if messagebox.askyesno("确认删除", "确定要删除选中的字段吗？"):
            for item in selection:
                self.ai_fields_tree.delete(item)
    
    def add_feishu_mapping(self):
        """
        添加飞书映射
        """
        dialog = MappingEditDialog(self.window, "添加飞书映射")
        if dialog.result:
            mapping_info = dialog.result
            self.feishu_mapping_tree.insert('', 'end', values=(
                mapping_info['ai_field'],
                mapping_info['feishu_name'],
                mapping_info['feishu_type']
            ))
    
    def edit_feishu_mapping(self, event):
        """
        编辑飞书映射
        
        Args:
            event: 事件对象
        """
        selection = self.feishu_mapping_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.feishu_mapping_tree.item(item, 'values')
        
        current_data = {
            'ai_field': values[0],
            'feishu_name': values[1],
            'feishu_type': values[2]
        }
        
        dialog = MappingEditDialog(self.window, "编辑飞书映射", current_data)
        if dialog.result:
            mapping_info = dialog.result
            self.feishu_mapping_tree.item(item, values=(
                mapping_info['ai_field'],
                mapping_info['feishu_name'],
                mapping_info['feishu_type']
            ))
    
    def delete_feishu_mapping(self):
        """
        删除飞书映射
        """
        selection = self.feishu_mapping_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的映射")
            return
        
        if messagebox.askyesno("确认删除", "确定要删除选中的映射吗？"):
            for item in selection:
                self.feishu_mapping_tree.delete(item)
    
    def auto_match_mappings(self):
        """
        自动匹配AI字段和飞书映射
        """
        # 获取所有AI字段
        ai_fields = []
        for item in self.ai_fields_tree.get_children():
            values = self.ai_fields_tree.item(item, 'values')
            ai_fields.append(values[0])
        
        # 获取现有的飞书映射
        existing_mappings = set()
        for item in self.feishu_mapping_tree.get_children():
            values = self.feishu_mapping_tree.item(item, 'values')
            existing_mappings.add(values[0])
        
        # 为没有映射的AI字段创建默认映射
        added_count = 0
        for ai_field in ai_fields:
            if ai_field not in existing_mappings:
                self.feishu_mapping_tree.insert('', 'end', values=(
                    ai_field,
                    ai_field,  # 默认使用相同的名称
                    'text',    # 默认类型
                    f'fld_{ai_field}'  # 默认ID
                ))
                added_count += 1
        
        if added_count > 0:
            messagebox.showinfo("成功", f"自动添加了 {added_count} 个映射")
        else:
            messagebox.showinfo("提示", "所有AI字段都已有对应的映射")
    
    def add_transformation_rule(self):
        """
        添加转换规则
        """
        dialog = RuleEditDialog(self.window, "添加转换规则")
        if dialog.result:
            rule_info = dialog.result
            parameters = ', '.join([f"{k}={v}" for k, v in rule_info.items() if k not in ('field_name', 'type')])
            
            self.rules_tree.insert('', 'end', values=(
                rule_info['field_name'],
                rule_info['type'],
                parameters
            ))
    
    def edit_transformation_rule(self, event):
        """
        编辑转换规则
        
        Args:
            event: 事件对象
        """
        selection = self.rules_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.rules_tree.item(item, 'values')
        
        current_data = {
            'field_name': values[0],
            'type': values[1]
        }
        
        # 解析参数
        parameters_str = values[2]
        if parameters_str:
            for param in parameters_str.split(', '):
                if '=' in param:
                    key, value = param.split('=', 1)
                    current_data[key.strip()] = value.strip()
        
        dialog = RuleEditDialog(self.window, "编辑转换规则", current_data)
        if dialog.result:
            rule_info = dialog.result
            parameters = ', '.join([f"{k}={v}" for k, v in rule_info.items() if k not in ('field_name', 'type')])
            
            self.rules_tree.item(item, values=(
                rule_info['field_name'],
                rule_info['type'],
                parameters
            ))
    
    def delete_transformation_rule(self):
        """
        删除转换规则
        """
        selection = self.rules_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的规则")
            return
        
        if messagebox.askyesno("确认删除", "确定要删除选中的规则吗？"):
            for item in selection:
                self.rules_tree.delete(item)
    
    def close_window(self):
        """
        关闭窗口
        """
        self.window.destroy()
    
    def run(self):
        """
        运行UI
        """
        if not self.parent:
            self.window.mainloop()


class FieldEditDialog:
    """字段编辑对话框"""
    
    def __init__(self, parent, title, initial_data=None):
        """
        初始化字段编辑对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            initial_data: 初始数据
        """
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui(initial_data)
        
        # 等待对话框关闭
        self.dialog.wait_window()
    
    def setup_ui(self, initial_data):
        """
        设置UI
        
        Args:
            initial_data: 初始数据
        """
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 字段名
        ttk.Label(frame, text="字段名:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=initial_data.get('name', '') if initial_data else '')
        ttk.Entry(frame, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 类型
        ttk.Label(frame, text="类型:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar(value=initial_data.get('type', 'text') if initial_data else 'text')
        type_combo = ttk.Combobox(frame, textvariable=self.type_var, values=['text', 'number', 'boolean', 'date'], width=27)
        type_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 描述
        ttk.Label(frame, text="描述:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        self.description_text = tk.Text(frame, width=30, height=5)
        self.description_text.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        if initial_data and 'description' in initial_data:
            self.description_text.insert('1.0', initial_data['description'])
        
        # 必需
        self.required_var = tk.BooleanVar(value=initial_data.get('required', False) if initial_data else False)
        ttk.Checkbutton(frame, text="必需字段", variable=self.required_var).grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.LEFT)
    
    def ok_clicked(self):
        """
        确定按钮点击事件
        """
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("警告", "请输入字段名")
            return
        
        self.result = {
            'name': name,
            'type': self.type_var.get(),
            'description': self.description_text.get('1.0', tk.END).strip(),
            'required': self.required_var.get()
        }
        
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """
        取消按钮点击事件
        """
        self.dialog.destroy()


class MappingEditDialog:
    """映射编辑对话框"""
    
    def __init__(self, parent, title, initial_data=None):
        """
        初始化映射编辑对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            initial_data: 初始数据
        """
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("450x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui(initial_data)
        
        # 等待对话框关闭
        self.dialog.wait_window()
    
    def setup_ui(self, initial_data):
        """
        设置UI
        
        Args:
            initial_data: 初始数据
        """
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # AI字段
        ttk.Label(frame, text="AI字段:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ai_field_var = tk.StringVar(value=initial_data.get('ai_field', '') if initial_data else '')
        ttk.Entry(frame, textvariable=self.ai_field_var, width=35).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 飞书字段名
        ttk.Label(frame, text="飞书字段名:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.feishu_name_var = tk.StringVar(value=initial_data.get('feishu_name', '') if initial_data else '')
        ttk.Entry(frame, textvariable=self.feishu_name_var, width=35).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 飞书字段类型
        ttk.Label(frame, text="飞书字段类型:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.feishu_type_var = tk.StringVar(value=initial_data.get('feishu_type', 'text') if initial_data else 'text')
        type_combo = ttk.Combobox(frame, textvariable=self.feishu_type_var, 
                                values=['text', 'number', 'select', 'multiSelect', 'date', 'checkbox'], width=32)
        type_combo.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.LEFT)
    
    def ok_clicked(self):
        """
        确定按钮点击事件
        """
        ai_field = self.ai_field_var.get().strip()
        feishu_name = self.feishu_name_var.get().strip()
        
        if not ai_field:
            messagebox.showwarning("警告", "请输入AI字段名")
            return
        
        if not feishu_name:
            messagebox.showwarning("警告", "请输入飞书字段名")
            return
        
        self.result = {
            'ai_field': ai_field,
            'feishu_name': feishu_name,
            'feishu_type': self.feishu_type_var.get()
        }
        
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """
        取消按钮点击事件
        """
        self.dialog.destroy()


class RuleEditDialog:
    """规则编辑对话框"""
    
    def __init__(self, parent, title, initial_data=None):
        """
        初始化规则编辑对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            initial_data: 初始数据
        """
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui(initial_data)
        
        # 等待对话框关闭
        self.dialog.wait_window()
    
    def setup_ui(self, initial_data):
        """
        设置UI
        
        Args:
            initial_data: 初始数据
        """
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 字段名
        ttk.Label(frame, text="字段名:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.field_name_var = tk.StringVar(value=initial_data.get('field_name', '') if initial_data else '')
        ttk.Entry(frame, textvariable=self.field_name_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 规则类型
        ttk.Label(frame, text="规则类型:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.rule_type_var = tk.StringVar(value=initial_data.get('type', 'split') if initial_data else 'split')
        type_combo = ttk.Combobox(frame, textvariable=self.rule_type_var, 
                                values=['split', 'format', 'validate', 'transform'], width=37)
        type_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        type_combo.bind('<<ComboboxSelected>>', self.on_rule_type_change)
        
        # 参数框架
        self.params_frame = ttk.LabelFrame(frame, text="参数设置", padding=10)
        self.params_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        # 初始化参数UI
        self.param_vars = {}
        self.update_params_ui(initial_data)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.LEFT)
    
    def on_rule_type_change(self, event):
        """
        规则类型改变事件
        
        Args:
            event: 事件对象
        """
        self.update_params_ui()
    
    def update_params_ui(self, initial_data=None):
        """
        更新参数UI
        
        Args:
            initial_data: 初始数据
        """
        # 清空现有控件
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        self.param_vars.clear()
        
        rule_type = self.rule_type_var.get()
        
        if rule_type == 'split':
            # 分隔符
            ttk.Label(self.params_frame, text="分隔符:").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.param_vars['separator'] = tk.StringVar(value=initial_data.get('separator', ',') if initial_data else ',')
            ttk.Entry(self.params_frame, textvariable=self.param_vars['separator'], width=20).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
            
            # 最大项目数
            ttk.Label(self.params_frame, text="最大项目数:").grid(row=1, column=0, sticky=tk.W, pady=2)
            self.param_vars['max_items'] = tk.StringVar(value=str(initial_data.get('max_items', 10)) if initial_data else '10')
            ttk.Entry(self.params_frame, textvariable=self.param_vars['max_items'], width=20).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
            
        elif rule_type == 'format':
            # 格式模板
            ttk.Label(self.params_frame, text="格式模板:").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.param_vars['template'] = tk.StringVar(value=initial_data.get('template', '{value}') if initial_data else '{value}')
            ttk.Entry(self.params_frame, textvariable=self.param_vars['template'], width=30).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
            
        elif rule_type == 'validate':
            # 验证规则
            ttk.Label(self.params_frame, text="验证规则:").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.param_vars['pattern'] = tk.StringVar(value=initial_data.get('pattern', '') if initial_data else '')
            ttk.Entry(self.params_frame, textvariable=self.param_vars['pattern'], width=30).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
            
        elif rule_type == 'transform':
            # 转换函数
            ttk.Label(self.params_frame, text="转换函数:").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.param_vars['function'] = tk.StringVar(value=initial_data.get('function', 'upper') if initial_data else 'upper')
            func_combo = ttk.Combobox(self.params_frame, textvariable=self.param_vars['function'], 
                                    values=['upper', 'lower', 'title', 'strip'], width=27)
            func_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
    
    def ok_clicked(self):
        """
        确定按钮点击事件
        """
        field_name = self.field_name_var.get().strip()
        if not field_name:
            messagebox.showwarning("警告", "请输入字段名")
            return
        
        rule_type = self.rule_type_var.get()
        if not rule_type:
            messagebox.showwarning("警告", "请选择规则类型")
            return
        
        self.result = {
            'field_name': field_name,
            'type': rule_type
        }
        
        # 添加参数
        for param_name, param_var in self.param_vars.items():
            value = param_var.get().strip()
            if value:
                # 尝试转换为适当的类型
                try:
                    if value.isdigit():
                        value = int(value)
                    elif value.lower() in ('true', 'false'):
                        value = value.lower() == 'true'
                except:
                    pass
                self.result[param_name] = value
        
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """
        取消按钮点击事件
        """
        self.dialog.destroy()


if __name__ == "__main__":
    # 测试运行
    app = MappingConfigUI()
    app.run()
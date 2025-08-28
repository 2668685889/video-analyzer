#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速提示管理界面模块
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, List, Optional, Callable
from ..utils.database import db

class QuickPromptsManager:
    """
    快速提示管理器
    """
    
    def __init__(self, parent: tk.Widget):
        """
        初始化快速提示管理器
        
        Args:
            parent (tk.Widget): 父窗口
        """
        self.parent = parent
        self.prompts_data = []
        
        # 创建管理窗口（初始隐藏）
        self.manager_window = None
        
    def create_quick_prompt_frame(self, parent_frame: tk.Frame) -> tk.Frame:
        """
        创建快速提示选择框架
        
        Args:
            parent_frame (tk.Frame): 父框架
            
        Returns:
            tk.Frame: 快速提示框架
        """
        # 快速提示框架
        prompt_frame = tk.Frame(parent_frame)
        
        # 标题
        title_label = tk.Label(prompt_frame, text="快速提示:", font=("Arial", 10, "bold"))
        title_label.pack(anchor="w", pady=(0, 5))
        
        # 提示选择和管理按钮框架
        control_frame = tk.Frame(prompt_frame)
        control_frame.pack(fill="x", pady=(0, 5))
        
        # 提示选择下拉框
        self.prompt_var = tk.StringVar()
        self.prompt_combobox = ttk.Combobox(
            control_frame, 
            textvariable=self.prompt_var,
            state="readonly",
            width=30
        )
        self.prompt_combobox.pack(side="left", padx=(0, 5))
        self.prompt_combobox.bind("<<ComboboxSelected>>", self._on_prompt_selected)
        
        # 管理按钮
        manage_btn = ttk.Button(
            control_frame,
            text="管理提示",
            command=self.open_manager
        )
        manage_btn.pack(side="left", padx=(0, 5))
        
        # 移除应用按钮，现在直接通过get_selected_prompt_text()获取选中的提示
        
        # 预览文本框
        preview_label = tk.Label(prompt_frame, text="提示预览:", font=("Arial", 9))
        preview_label.pack(anchor="w", pady=(10, 2))
        
        self.preview_text = scrolledtext.ScrolledText(
            prompt_frame,
            height=12,  # 增加高度以填充空白位置
            wrap=tk.WORD,
            font=("Arial", 9),
            state="disabled"
        )
        self.preview_text.pack(fill="both", expand=True)
        
        # 设置最小高度增加100像素
        self.preview_text.configure(height=12)
        prompt_frame.update_idletasks()
        current_height = self.preview_text.winfo_reqheight()
        self.preview_text.configure(height=int((current_height + 100) / 16))  # 大约增加100像素
        
        # 加载提示数据
        self._load_prompts()
        
        return prompt_frame
    
    def _load_prompts(self) -> None:
        """
        加载快速提示数据
        """
        try:
            self.prompts_data = db.get_all_quick_prompts()
            
            # 更新下拉框
            prompt_names = [prompt['name'] for prompt in self.prompts_data]
            self.prompt_combobox['values'] = prompt_names
            
            # 默认选择第一个
            if prompt_names:
                self.prompt_combobox.set(prompt_names[0])
                self._update_preview()
                
        except Exception as e:
            messagebox.showerror("错误", f"加载快速提示失败: {str(e)}")
    
    def _on_prompt_selected(self, event=None) -> None:
        """
        提示选择事件处理
        
        Args:
            event: 事件对象
        """
        self._update_preview()
    
    def _update_preview(self) -> None:
        """
        更新提示预览
        """
        selected_name = self.prompt_var.get()
        if not selected_name:
            return
            
        # 查找选中的提示
        selected_prompt = None
        for prompt in self.prompts_data:
            if prompt['name'] == selected_name:
                selected_prompt = prompt
                break
        
        if selected_prompt:
            # 更新预览文本
            self.preview_text.config(state="normal")
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, selected_prompt['prompt_text'])
            self.preview_text.config(state="disabled")
    
    # 移除_apply_selected_prompt方法，现在通过get_selected_prompt_text()直接获取提示
    
    def get_selected_prompt_text(self) -> str:
        """
        获取当前选中的提示文本
        
        Returns:
            str: 提示文本
        """
        selected_name = self.prompt_var.get()
        if not selected_name:
            return ""
            
        # 查找选中的提示
        for prompt in self.prompts_data:
            if prompt['name'] == selected_name:
                return prompt['prompt_text']
        
        return ""
    
    def open_manager(self) -> None:
        """
        打开快速提示管理窗口
        """
        if self.manager_window and self.manager_window.winfo_exists():
            self.manager_window.lift()
            return
            
        self.manager_window = tk.Toplevel(self.parent)
        self.manager_window.title("快速提示管理")
        self.manager_window.geometry("800x600")
        self.manager_window.resizable(True, True)
        
        # 创建管理界面
        self._create_manager_ui()
        
        # 加载数据
        self._load_manager_data()
    
    def _create_manager_ui(self) -> None:
        """
        创建管理界面UI
        """
        # 主框架
        main_frame = tk.Frame(self.manager_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 左侧列表框架
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # 提示列表标题
        list_label = tk.Label(left_frame, text="快速提示列表", font=("Arial", 12, "bold"))
        list_label.pack(anchor="w", pady=(0, 5))
        
        # 提示列表
        list_frame = tk.Frame(left_frame)
        list_frame.pack(fill="both", expand=True)
        
        self.prompts_listbox = tk.Listbox(list_frame, font=("Arial", 10))
        self.prompts_listbox.pack(side="left", fill="both", expand=True)
        self.prompts_listbox.bind("<<ListboxSelect>>", self._on_manager_prompt_selected)
        
        # 列表滚动条
        list_scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        list_scrollbar.pack(side="right", fill="y")
        self.prompts_listbox.config(yscrollcommand=list_scrollbar.set)
        list_scrollbar.config(command=self.prompts_listbox.yview)
        
        # 列表操作按钮
        list_btn_frame = tk.Frame(left_frame)
        list_btn_frame.pack(fill="x", pady=(10, 0))
        
        new_btn = ttk.Button(
            list_btn_frame,
            text="新建提示",
            command=self._new_prompt
        )
        new_btn.pack(side="left", padx=(0, 5))
        
        delete_btn = ttk.Button(
            list_btn_frame,
            text="删除提示",
            command=self._delete_prompt
        )
        delete_btn.pack(side="left")
        
        # 右侧编辑框架
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # 编辑标题
        edit_label = tk.Label(right_frame, text="编辑提示", font=("Arial", 12, "bold"))
        edit_label.pack(anchor="w", pady=(0, 10))
        
        # 名称输入
        name_frame = tk.Frame(right_frame)
        name_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(name_frame, text="名称:", font=("Arial", 10)).pack(anchor="w")
        self.name_entry = tk.Entry(name_frame, font=("Arial", 10))
        self.name_entry.pack(fill="x", pady=(2, 0))
        
        # 描述输入
        desc_frame = tk.Frame(right_frame)
        desc_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(desc_frame, text="描述:", font=("Arial", 10)).pack(anchor="w")
        self.desc_entry = tk.Entry(desc_frame, font=("Arial", 10))
        self.desc_entry.pack(fill="x", pady=(2, 0))
        
        # 提示内容输入
        content_frame = tk.Frame(right_frame)
        content_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        tk.Label(content_frame, text="提示内容:", font=("Arial", 10)).pack(anchor="w")
        self.content_text = scrolledtext.ScrolledText(
            content_frame,
            wrap=tk.WORD,
            font=("Arial", 10)
        )
        self.content_text.pack(fill="both", expand=True, pady=(2, 0))
        
        # 保存按钮
        save_btn = ttk.Button(
            right_frame, 
            text="保存提示", 
            command=self._save_prompt
        )
        save_btn.pack(pady=(10, 0))
        
        # 当前编辑的提示ID
        self.editing_prompt_id = None
    
    def _load_manager_data(self) -> None:
        """
        加载管理器数据
        """
        try:
            self.prompts_data = db.get_all_quick_prompts()
            
            # 清空列表
            self.prompts_listbox.delete(0, tk.END)
            
            # 添加提示到列表
            for prompt in self.prompts_data:
                display_text = prompt['name']
                if prompt['is_default']:
                    display_text += " (默认)"
                self.prompts_listbox.insert(tk.END, display_text)
                
        except Exception as e:
            messagebox.showerror("错误", f"加载数据失败: {str(e)}")
    
    def _on_manager_prompt_selected(self, event=None) -> None:
        """
        管理器中提示选择事件
        
        Args:
            event: 事件对象
        """
        selection = self.prompts_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if index < len(self.prompts_data):
            prompt = self.prompts_data[index]
            
            # 填充编辑框
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, prompt['name'])
            
            self.desc_entry.delete(0, tk.END)
            if prompt['description']:
                self.desc_entry.insert(0, prompt['description'])
            
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(1.0, prompt['prompt_text'])
            
            # 设置当前编辑的提示ID
            self.editing_prompt_id = prompt['id']
            
            # 如果是默认提示，禁用编辑
            if prompt['is_default']:
                self.name_entry.config(state="disabled")
                self.desc_entry.config(state="disabled")
                self.content_text.config(state="disabled")
            else:
                self.name_entry.config(state="normal")
                self.desc_entry.config(state="normal")
                self.content_text.config(state="normal")
    
    def _new_prompt(self) -> None:
        """
        新建提示
        """
        # 清空编辑框
        self.name_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.content_text.delete(1.0, tk.END)
        
        # 启用编辑
        self.name_entry.config(state="normal")
        self.desc_entry.config(state="normal")
        self.content_text.config(state="normal")
        
        # 清除选择
        self.prompts_listbox.selection_clear(0, tk.END)
        self.editing_prompt_id = None
        
        # 焦点到名称输入框
        self.name_entry.focus()
    
    def _save_prompt(self) -> None:
        """
        保存提示
        """
        name = self.name_entry.get().strip()
        description = self.desc_entry.get().strip()
        content = self.content_text.get(1.0, tk.END).strip()
        
        if not name:
            messagebox.showwarning("警告", "请输入提示名称")
            return
            
        if not content:
            messagebox.showwarning("警告", "请输入提示内容")
            return
        
        try:
            if self.editing_prompt_id is None:
                # 新建提示
                success = db.add_quick_prompt(name, content, description)
                if success:
                    messagebox.showinfo("成功", "提示创建成功")
                    self._load_manager_data()
                    self._load_prompts()  # 刷新主界面
                else:
                    messagebox.showerror("错误", "提示名称已存在")
            else:
                # 更新提示
                success = db.update_quick_prompt(self.editing_prompt_id, name, content, description)
                if success:
                    messagebox.showinfo("成功", "提示更新成功")
                    self._load_manager_data()
                    self._load_prompts()  # 刷新主界面
                else:
                    messagebox.showerror("错误", "更新失败，提示名称可能已存在")
                    
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def _delete_prompt(self) -> None:
        """
        删除提示
        """
        selection = self.prompts_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的提示")
            return
            
        index = selection[0]
        if index < len(self.prompts_data):
            prompt = self.prompts_data[index]
            
            # 移除默认提示删除限制，现在可以删除默认提示
            
            # 确认删除
            if messagebox.askyesno("确认", f"确定要删除提示 '{prompt['name']}' 吗？"):
                try:
                    success = db.delete_quick_prompt(prompt['id'])
                    if success:
                        messagebox.showinfo("成功", "提示删除成功")
                        self._load_manager_data()
                        self._load_prompts()  # 刷新主界面
                        
                        # 清空编辑框
                        self.name_entry.delete(0, tk.END)
                        self.desc_entry.delete(0, tk.END)
                        self.content_text.delete(1.0, tk.END)
                        self.editing_prompt_id = None
                    else:
                        messagebox.showerror("错误", "删除失败")
                        
                except Exception as e:
                    messagebox.showerror("错误", f"删除失败: {str(e)}")
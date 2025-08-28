#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史记录查看界面模块
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import csv
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from ..utils.database import db
from ..utils.feishu_sync import feishu_sync
from ..utils.smart_field_setup import SmartFieldSetup
from ..utils.feishu_doc_sync import FeishuDocSyncService

class HistoryViewer:
    """
    历史记录查看器
    """
    
    def __init__(self, parent: tk.Widget):
        """
        初始化历史记录查看器
        
        Args:
            parent (tk.Widget): 父窗口
        """
        self.parent = parent
        self.history_window = None
        self.history_data = []
        self.filtered_data = []
        
    def open_history_viewer(self) -> None:
        """
        打开历史记录查看窗口
        """
        if self.history_window and self.history_window.winfo_exists():
            self.history_window.lift()
            return
            
        self.history_window = tk.Toplevel(self.parent)
        self.history_window.title("视频分析历史记录")
        self.history_window.geometry("1600x900")
        self.history_window.resizable(True, True)
        
        # 创建界面
        self._create_history_ui()
        
        # 加载数据
        self._load_history_data()
    
    def _create_history_ui(self) -> None:
        """
        创建历史记录界面UI
        """
        # 主框架
        main_frame = tk.Frame(self.history_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 顶部工具栏 - 重新设计为多行布局
        toolbar_frame = tk.Frame(main_frame)
        toolbar_frame.pack(fill="x", pady=(0, 10))
        
        # 第一行：搜索和基本操作
        first_row_frame = tk.Frame(toolbar_frame)
        first_row_frame.pack(fill="x", pady=(0, 5))
        
        # 搜索框架
        search_frame = tk.Frame(first_row_frame)
        search_frame.pack(side="left", fill="x", expand=True)
        
        tk.Label(search_frame, text="搜索:", font=("Arial", 10)).pack(side="left", padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 10),
            width=30
        )
        self.search_entry.pack(side="left", padx=(0, 5))
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)
        
        search_btn = ttk.Button(
            search_frame,
            text="搜索",
            command=self._search_records
        )
        search_btn.pack(side="left", padx=(0, 5))
        
        clear_btn = ttk.Button(
            search_frame,
            text="清除",
            command=self._clear_search
        )
        clear_btn.pack(side="left", padx=(0, 10))
        
        # 基本操作按钮
        basic_action_frame = tk.Frame(first_row_frame)
        basic_action_frame.pack(side="right")
        
        refresh_btn = ttk.Button(
            basic_action_frame,
            text="刷新",
            command=self._load_history_data
        )
        refresh_btn.pack(side="left", padx=(0, 5))
        
        export_btn = ttk.Button(
            basic_action_frame,
            text="导出CSV",
            command=self._export_to_csv
        )
        export_btn.pack(side="left", padx=(0, 5))
        
        # 第二行：删除操作
        second_row_frame = tk.Frame(toolbar_frame)
        second_row_frame.pack(fill="x", pady=(0, 5))
        
        delete_label = tk.Label(second_row_frame, text="删除操作:", font=("Arial", 10, "bold"))
        delete_label.pack(side="left", padx=(0, 10))
        
        delete_btn = ttk.Button(
            second_row_frame,
            text="删除选中记录",
            command=self._delete_selected_record
        )
        delete_btn.pack(side="left", padx=(0, 5))
        
        batch_delete_btn = ttk.Button(
            second_row_frame,
            text="批量删除",
            command=self._batch_delete_records
        )
        batch_delete_btn.pack(side="left", padx=(0, 5))
        
        delete_all_btn = ttk.Button(
            second_row_frame,
            text="删除所有数据",
            command=self._delete_all_records
        )
        delete_all_btn.pack(side="left")
        
        # 第三行：飞书多维表格同步
        third_row_frame = tk.Frame(toolbar_frame)
        third_row_frame.pack(fill="x", pady=(0, 5))
        
        feishu_label = tk.Label(third_row_frame, text="多维表格同步:", font=("Arial", 10, "bold"))
        feishu_label.pack(side="left", padx=(0, 10))
        
        feishu_sync_selected_btn = ttk.Button(
            third_row_frame,
            text="同步选中到多维表格",
            command=self._sync_selected_to_feishu
        )
        feishu_sync_selected_btn.pack(side="left", padx=(0, 5))
        
        feishu_sync_all_btn = ttk.Button(
            third_row_frame,
            text="同步所有到多维表格",
            command=self._sync_all_to_feishu
        )
        feishu_sync_all_btn.pack(side="left")
        
        # 第四行：飞书电子表格同步
        fourth_row_frame = tk.Frame(toolbar_frame)
        fourth_row_frame.pack(fill="x", pady=(0, 5))
        
        spreadsheet_label = tk.Label(fourth_row_frame, text="电子表格同步:", font=("Arial", 10, "bold"))
        spreadsheet_label.pack(side="left", padx=(0, 10))
        
        spreadsheet_sync_selected_btn = ttk.Button(
            fourth_row_frame,
            text="同步选中到电子表格",
            command=self._sync_selected_to_spreadsheet
        )
        spreadsheet_sync_selected_btn.pack(side="left", padx=(0, 5))
        
        spreadsheet_sync_all_btn = ttk.Button(
            fourth_row_frame,
            text="同步所有到电子表格",
            command=self._sync_all_to_spreadsheet
        )
        spreadsheet_sync_all_btn.pack(side="left")
        
        # 第五行：飞书云文档同步
        fifth_row_frame = tk.Frame(toolbar_frame)
        fifth_row_frame.pack(fill="x", pady=(0, 5))
        
        doc_label = tk.Label(fifth_row_frame, text="云文档同步:", font=("Arial", 10, "bold"))
        doc_label.pack(side="left", padx=(0, 10))
        
        doc_sync_selected_btn = ttk.Button(
            fifth_row_frame,
            text="同步选中到云文档",
            command=self._sync_selected_to_doc
        )
        doc_sync_selected_btn.pack(side="left", padx=(0, 5))
        
        doc_sync_all_btn = ttk.Button(
            fifth_row_frame,
            text="同步所有到云文档",
            command=self._sync_all_to_doc
        )
        doc_sync_all_btn.pack(side="left")
        
        # 分割器
        paned_window = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill="both", expand=True)
        
        # 左侧列表框架
        left_frame = tk.Frame(paned_window)
        paned_window.add(left_frame, width=1000)
        
        # 记录列表标题
        list_label = tk.Label(left_frame, text="分析记录列表", font=("Arial", 12, "bold"))
        list_label.pack(anchor="w", pady=(0, 5))
        
        # 创建Treeview表格
        tree_frame = tk.Frame(left_frame)
        tree_frame.pack(fill="both", expand=True)
        
        # 定义列（包含隐藏的sequence_id_data列用于存储数据）
        columns = ("选择", "序列号", "文件名", "文件大小", "分析时间", "飞书状态", "sequence_id_data")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15, selectmode="extended")
        
        # 用于跟踪选中状态的字典
        self.selected_items = {}
        
        # 设置列标题和宽度
        self.tree.heading("选择", text="☐", command=self._toggle_select_all)
        self.tree.heading("序列号", text="序列号")
        self.tree.heading("文件名", text="文件名")
        self.tree.heading("文件大小", text="文件大小")
        self.tree.heading("分析时间", text="分析时间")
        self.tree.heading("飞书状态", text="飞书状态")
        self.tree.heading("sequence_id_data", text="")  # 隐藏列的标题
        
        self.tree.column("选择", width=50, minwidth=50)
        self.tree.column("序列号", width=200, minwidth=180)  # 增加序列号列宽度
        self.tree.column("文件名", width=400, minwidth=350)  # 大幅增加文件名列宽度
        self.tree.column("文件大小", width=100, minwidth=90)  # 稍微增加文件大小列宽度
        self.tree.column("分析时间", width=160, minwidth=140)  # 增加分析时间列宽度
        self.tree.column("飞书状态", width=120, minwidth=100)  # 增加飞书状态列宽度
        # 隐藏sequence_id_data列
        self.tree.column("sequence_id_data", width=0, minwidth=0, stretch=False)
        
        # 全选状态
        self.select_all_state = False
        
        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self._on_record_selected)
        self.tree.bind("<Button-1>", self._on_tree_click)
        
        # 添加滚动条
        tree_scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        tree_scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scrollbar_y.set, xscrollcommand=tree_scrollbar_x.set)
        
        # 布局
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar_y.pack(side="right", fill="y")
        tree_scrollbar_x.pack(side="bottom", fill="x")
        
        # 统计信息
        stats_frame = tk.Frame(left_frame)
        stats_frame.pack(fill="x", pady=(5, 0))
        
        self.stats_label = tk.Label(
            stats_frame,
            text="总记录数: 0",
            font=("Arial", 9),
            fg="#666666"
        )
        self.stats_label.pack(anchor="w")
        
        # 右侧详情框架
        right_frame = tk.Frame(paned_window)
        paned_window.add(right_frame, width=500)
        
        # 详情标题
        detail_label = tk.Label(right_frame, text="记录详情", font=("Arial", 12, "bold"))
        detail_label.pack(anchor="w", pady=(0, 10))
        
        # 基本信息框架
        info_frame = tk.Frame(right_frame)
        info_frame.pack(fill="x", pady=(0, 10))
        
        # 序列号
        seq_frame = tk.Frame(info_frame)
        seq_frame.pack(fill="x", pady=(0, 5))
        tk.Label(seq_frame, text="序列号:", font=("Arial", 10, "bold")).pack(side="left")
        self.seq_label = tk.Label(seq_frame, text="", font=("Arial", 10), fg="#2196F3")
        self.seq_label.pack(side="left", padx=(5, 0))
        
        # 文件信息
        file_frame = tk.Frame(info_frame)
        file_frame.pack(fill="x", pady=(0, 5))
        tk.Label(file_frame, text="文件:", font=("Arial", 10, "bold")).pack(side="left")
        self.file_label = tk.Label(file_frame, text="", font=("Arial", 10))
        self.file_label.pack(side="left", padx=(5, 0))
        
        # 时间信息
        time_frame = tk.Frame(info_frame)
        time_frame.pack(fill="x", pady=(0, 5))
        tk.Label(time_frame, text="分析时间:", font=("Arial", 10, "bold")).pack(side="left")
        self.time_label = tk.Label(time_frame, text="", font=("Arial", 10))
        self.time_label.pack(side="left", padx=(5, 0))
        
        # 分析提示
        prompt_label = tk.Label(right_frame, text="分析提示:", font=("Arial", 10, "bold"))
        prompt_label.pack(anchor="w", pady=(10, 2))
        
        self.prompt_text = scrolledtext.ScrolledText(
            right_frame,
            height=6,
            wrap=tk.WORD,
            font=("Arial", 9),
            state="disabled"
        )
        self.prompt_text.pack(fill="x", pady=(0, 10))
        
        # 分析结果
        result_label = tk.Label(right_frame, text="分析结果:", font=("Arial", 10, "bold"))
        result_label.pack(anchor="w", pady=(0, 2))
        
        self.result_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            font=("Arial", 9),
            state="disabled"
        )
        self.result_text.pack(fill="both", expand=True)
        
        # 详情操作按钮 - 重新设计为多行布局
        detail_btn_frame = tk.Frame(right_frame)
        detail_btn_frame.pack(fill="x", pady=(10, 0))
        
        # 第一行：基本操作
        detail_first_row = tk.Frame(detail_btn_frame)
        detail_first_row.pack(fill="x", pady=(0, 5))
        
        copy_btn = ttk.Button(
            detail_first_row,
            text="复制结果",
            command=self._copy_result
        )
        copy_btn.pack(side="left", padx=(0, 5))
        
        save_btn = ttk.Button(
            detail_first_row,
            text="保存为文本",
            command=self._save_result_as_text
        )
        save_btn.pack(side="left", padx=(0, 5))
        
        edit_btn = ttk.Button(
            detail_first_row,
            text="编辑内容",
            command=self._edit_record_content
        )
        edit_btn.pack(side="left")
        
        # 第二行：飞书操作
        detail_second_row = tk.Frame(detail_btn_frame)
        detail_second_row.pack(fill="x")
        
        feishu_single_sync_btn = ttk.Button(
            detail_second_row,
            text="同步此记录到飞书",
            command=self._sync_selected_to_feishu
        )
        feishu_single_sync_btn.pack(side="left", padx=(0, 5))
        
        generate_template_btn = ttk.Button(
            detail_second_row,
            text="生成字段模板",
            command=self._generate_field_template
        )
        generate_template_btn.pack(side="left")
    
    def _load_history_data(self) -> None:
        """
        加载历史记录数据
        """
        try:
            self.history_data = db.get_all_analysis_results(limit=1000)
            self.filtered_data = self.history_data.copy()
            self._update_tree_view()
            self._update_stats()
            
        except Exception as e:
            messagebox.showerror("错误", f"加载历史记录失败: {str(e)}")
    
    def _update_tree_view(self) -> None:
        """
        更新树形视图
        """
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加数据
        for record in self.filtered_data:
            # 格式化文件大小
            file_size = self._format_file_size(record.get('file_size', 0))
            
            # 格式化时间
            created_at = record.get('created_at', '')
            if created_at:
                try:
                    # 解析时间字符串
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    formatted_time = created_at
            else:
                formatted_time = ''
            
            # 飞书同步状态 - 综合考虑电子表格和云文档同步状态
            spreadsheet_row = record.get('feishu_spreadsheet_row')
            spreadsheet_sync_status = record.get('spreadsheet_sync_status', 0)
            doc_sync_status = record.get('doc_sync_status', 0)
            
            # 检查各种同步状态
            spreadsheet_synced = spreadsheet_row and spreadsheet_sync_status == 1
            doc_synced = doc_sync_status == 1
            
            if spreadsheet_synced and doc_synced:
                feishu_status = "✓ 全部已同步"
            elif spreadsheet_synced or doc_synced:
                if spreadsheet_synced:
                    feishu_status = "✓ 表格已同步"
                else:
                    feishu_status = "✓ 文档已同步"
            else:
                feishu_status = "○ 未同步"
            
            # 检查选择状态
            sequence_id = record.get('sequence_id', '')
            select_status = "☑" if sequence_id in self.selected_items else "☐"
            
            # 插入数据（包含所有7列的值）
            item_id = self.tree.insert("", "end", values=(
                select_status,
                sequence_id,
                record.get('file_name', ''),
                file_size,
                formatted_time,
                feishu_status,
                sequence_id  # sequence_id_data列的值
            ))
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        格式化文件大小
        
        Args:
            size_bytes (int): 文件大小（字节）
            
        Returns:
            str: 格式化后的文件大小
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def _update_stats(self) -> None:
        """
        更新统计信息
        """
        total_count = len(self.filtered_data)
        if len(self.filtered_data) != len(self.history_data):
            self.stats_label.config(text=f"显示记录数: {total_count} / 总记录数: {len(self.history_data)}")
        else:
            self.stats_label.config(text=f"总记录数: {total_count}")
    
    def _on_record_selected(self, event=None) -> None:
        """
        记录选择事件处理
        
        Args:
            event: 事件对象
        """
        selection = self.tree.selection()
        if not selection:
            return
        
        # 从隐藏的sequence_id_data列获取正确的sequence_id
        sequence_id = self.tree.set(selection[0], "sequence_id_data")
        
        if not sequence_id:
            return
        
        # 查找对应的记录
        selected_record = None
        for record in self.filtered_data:
            if record.get('sequence_id') == sequence_id:
                selected_record = record
                break
        
        if selected_record:
            self._display_record_details(selected_record)
    
    def _display_record_details(self, record: Dict) -> None:
        """
        显示记录详情
        
        Args:
            record (Dict): 记录数据
        """
        # 更新基本信息
        self.seq_label.config(text=record.get('sequence_id', ''))
        
        file_info = f"{record.get('file_name', '')} ({self._format_file_size(record.get('file_size', 0))})"
        self.file_label.config(text=file_info)
        
        created_at = record.get('created_at', '')
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                formatted_time = created_at
        else:
            formatted_time = ''
        self.time_label.config(text=formatted_time)
        
        # 更新分析提示
        self.prompt_text.config(state="normal")
        self.prompt_text.delete(1.0, tk.END)
        self.prompt_text.insert(1.0, record.get('analysis_prompt', ''))
        self.prompt_text.config(state="disabled")
        
        # 更新分析结果
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        
        # 显示分析结果
        analysis_result = record.get('analysis_result', '')
        self.result_text.insert(1.0, analysis_result)
        
        # 添加OSS链接信息（如果存在）
        oss_url = record.get('oss_url')
        oss_file_name = record.get('oss_file_name')
        if oss_url:
            oss_info = "\n\n=== OSS上传信息 ==="
            oss_info += f"\nOSS链接: {oss_url}"
            if oss_file_name:
                oss_info += f"\nOSS文件名: {oss_file_name}"
            self.result_text.insert(tk.END, oss_info)
        
        self.result_text.config(state="disabled")
    
    def _sync_all_to_spreadsheet(self) -> None:
        """
        同步所有记录到飞书电子表格
        """
        try:
            # 检查配置
            from ..utils.config import config
            if not config.is_feishu_spreadsheet_valid():
                messagebox.showwarning("配置错误", "请先在设置中配置飞书电子表格信息")
                return
            
            # 获取所有记录
            all_records = db.get_all_history_records()
            if not all_records:
                messagebox.showinfo("提示", "没有可同步的记录")
                return
            
            # 确认同步
            if not messagebox.askyesno("确认同步", f"确定要同步 {len(all_records)} 条记录到飞书电子表格吗？"):
                return
            
            # 创建进度窗口
            progress_window = tk.Toplevel(self.history_window)
            progress_window.title("同步进度")
            progress_window.geometry("400x150")
            progress_window.transient(self.history_window)
            progress_window.grab_set()
            
            # 居中显示
            progress_window.geometry("+%d+%d" % (
                self.history_window.winfo_rootx() + 50,
                self.history_window.winfo_rooty() + 50
            ))
            
            # 进度标签
            progress_label = tk.Label(progress_window, text="准备同步...", font=("Arial", 10))
            progress_label.pack(pady=10)
            
            # 进度条
            progress_bar = ttk.Progressbar(
                progress_window,
                mode='determinate',
                maximum=len(all_records)
            )
            progress_bar.pack(pady=10, padx=20, fill="x")
            
            # 状态标签
            status_label = tk.Label(progress_window, text="", font=("Arial", 9), fg="gray")
            status_label.pack(pady=5)
            
            progress_window.update()
            
            # 执行同步
            from ..utils.feishu_spreadsheet_sync import FeishuSpreadsheetSync
            sync_service = FeishuSpreadsheetSync()
            
            success_count = 0
            error_count = 0
            error_messages = []
            
            for i, record in enumerate(all_records):
                try:
                    progress_label.config(text=f"正在同步第 {i+1}/{len(all_records)} 条记录...")
                    status_label.config(text=f"文件: {record.get('file_name', 'Unknown')}")
                    progress_bar['value'] = i
                    progress_window.update()
                    
                    # 同步单条记录（强制更新以确保数据写入）
                    result = sync_service.sync_record_to_spreadsheet(
                        record.get('sequence_id'), 
                        force_update=True
                    )
                    if result:
                        success_count += 1
                    else:
                        raise Exception("同步失败")
                    
                except Exception as e:
                    error_count += 1
                    error_messages.append(f"记录 {record.get('sequence_id', 'Unknown')}: {str(e)}")
                    
                time.sleep(0.1)  # 避免请求过快
            
            progress_bar['value'] = len(all_records)
            progress_label.config(text="同步完成")
            progress_window.update()
            
            # 等待一下再关闭进度窗口
            progress_window.after(1000, progress_window.destroy)
            
            # 显示结果
            if error_count == 0:
                result_message = f"成功同步 {success_count} 条记录到飞书电子表格"
                messagebox.showinfo("同步完成", result_message)
            else:
                result_message = f"同步完成：成功 {success_count} 条，失败 {error_count} 条"
                if len(error_messages) <= 5:
                    result_message += "\n\n失败详情：\n" + "\n".join(error_messages)
                else:
                    result_message += f"\n\n失败详情（前5条）：\n" + "\n".join(error_messages[:5])
                    result_message += f"\n... 还有 {len(error_messages) - 5} 条错误"
                messagebox.showwarning("同步完成", result_message)
            
            # 刷新数据
            self._load_history_data()
            
        except Exception as e:
            messagebox.showerror("错误", f"同步失败: {str(e)}")
    
    def _sync_selected_to_spreadsheet(self) -> None:
        """
        同步选中的记录到飞书电子表格
        """
        try:
            # 检查配置
            from ..utils.config import config
            if not config.is_feishu_spreadsheet_valid():
                messagebox.showwarning("配置错误", "请先在设置中配置飞书电子表格信息")
                return
            
            # 获取选中的记录
            selected_items = self.tree.selection()
            if not selected_items:
                messagebox.showwarning("提示", "请先选择要同步的记录")
                return
            
            # 获取记录详情
            selected_records = []
            for item in selected_items:
                # sequence_id在第二列（索引1），第一列（索引0）是选择状态
                sequence_id = self.tree.item(item, "values")[1]
                record = db.get_analysis_by_sequence_id(sequence_id)
                if record:
                    selected_records.append(record)
            
            if not selected_records:
                messagebox.showwarning("提示", "未找到有效的记录")
                return
            
            # 确认同步
            if not messagebox.askyesno("确认同步", f"确定要同步 {len(selected_records)} 条记录到飞书电子表格吗？"):
                return
            
            # 创建进度窗口（如果记录数量较多）
            progress_window = None
            progress_label = None
            progress_bar = None
            
            if len(selected_records) > 1:
                progress_window = tk.Toplevel(self.history_window)
                progress_window.title("同步进度")
                progress_window.geometry("400x120")
                progress_window.transient(self.history_window)
                progress_window.grab_set()
                
                # 居中显示
                progress_window.geometry("+%d+%d" % (
                    self.history_window.winfo_rootx() + 50,
                    self.history_window.winfo_rooty() + 50
                ))
                
                # 进度标签
                progress_label = tk.Label(progress_window, text="准备同步...", font=("Arial", 10))
                progress_label.pack(pady=10)
                
                # 进度条
                progress_bar = ttk.Progressbar(
                    progress_window,
                    mode='determinate',
                    maximum=len(selected_records)
                )
                progress_bar.pack(pady=10, padx=20, fill="x")
                
                progress_window.update()
            
            # 执行同步
            from ..utils.feishu_spreadsheet_sync import FeishuSpreadsheetSync
            sync_service = FeishuSpreadsheetSync()
            
            success_count = 0
            error_count = 0
            error_messages = []
            
            for i, record in enumerate(selected_records):
                try:
                    if progress_window:
                        progress_label.config(text=f"正在同步第 {i+1}/{len(selected_records)} 条记录...")
                        progress_bar['value'] = i
                        progress_window.update()
                    
                    # 同步单条记录（强制更新以确保数据写入）
                    result = sync_service.sync_record_to_spreadsheet(
                        record.get('sequence_id'), 
                        force_update=True
                    )
                    if result:
                        success_count += 1
                    else:
                        raise Exception("同步失败")
                    
                except Exception as e:
                    error_count += 1
                    error_messages.append(f"记录 {record.get('sequence_id', 'Unknown')}: {str(e)}")
                    
                if len(selected_records) > 1:
                    time.sleep(0.1)  # 避免请求过快
            
            if progress_window:
                progress_bar['value'] = len(selected_records)
                progress_label.config(text="同步完成")
                progress_window.update()
                
                # 等待一下再关闭进度窗口
                progress_window.after(1000, progress_window.destroy)
            
            # 显示结果
            if error_count == 0:
                result_message = f"成功同步 {success_count} 条记录到飞书电子表格"
                if len(selected_records) == 1:
                    result_message = "记录已成功同步到飞书电子表格"
                messagebox.showinfo("同步完成", result_message)
            else:
                result_message = f"同步完成：成功 {success_count} 条，失败 {error_count} 条"
                if len(error_messages) <= 3:
                    result_message += "\n\n失败详情：\n" + "\n".join(error_messages)
                else:
                    result_message += f"\n\n失败详情（前3条）：\n" + "\n".join(error_messages[:3])
                    result_message += f"\n... 还有 {len(error_messages) - 3} 条错误"
                if error_count == len(selected_records):
                    messagebox.showerror("同步失败", result_message)
                else:
                    messagebox.showinfo("同步完成", result_message)
            
            # 刷新数据
            self._load_history_data()
            
            # 重新选中记录
            if len(selected_records) == 1:
                sequence_id = selected_records[0]['sequence_id']
                for item in self.tree.get_children():
                    if self.tree.item(item)['values'][0] == sequence_id:
                        self.tree.selection_set(item)
                        self.tree.focus(item)
                        break
                
        except Exception as e:
            messagebox.showerror("错误", f"同步失败: {str(e)}")
    
    def _on_search_changed(self, event=None) -> None:
        """
        搜索框内容变化事件
        
        Args:
            event: 事件对象
        """
        # 实时搜索（可选）
        pass
    
    def _search_records(self) -> None:
        """
        搜索记录
        """
        keyword = self.search_var.get().strip()
        
        if not keyword:
            self.filtered_data = self.history_data.copy()
        else:
            try:
                # 使用数据库搜索
                self.filtered_data = db.search_analysis_results(keyword)
            except Exception as e:
                messagebox.showerror("错误", f"搜索失败: {str(e)}")
                return
        
        self._update_tree_view()
        self._update_stats()
    
    def _clear_search(self) -> None:
        """
        清除搜索
        """
        self.search_var.set("")
        self.filtered_data = self.history_data.copy()
        self._update_tree_view()
        self._update_stats()
    
    def _delete_selected_record(self) -> None:
        """
        删除选中的记录
        """
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的记录")
            return
        
        # 从隐藏的sequence_id_data列获取正确的sequence_id
        sequence_id = self.tree.set(selection[0], "sequence_id_data")
        
        if not sequence_id:
            return
        
        # 获取文件名（第3列，索引为2）
        item = self.tree.item(selection[0])
        values = item['values']
        file_name = values[2] if len(values) > 2 else "未知文件"
        
        # 确认删除
        if messagebox.askyesno("确认删除", f"确定要删除记录 '{file_name}' (序列号: {sequence_id}) 吗？"):
            try:
                success = db.delete_analysis_result(sequence_id)
                if success:
                    messagebox.showinfo("成功", "记录删除成功")
                    self._load_history_data()  # 重新加载数据
                    
                    # 清空详情显示
                    self.seq_label.config(text="")
                    self.file_label.config(text="")
                    self.time_label.config(text="")
                    
                    self.prompt_text.config(state="normal")
                    self.prompt_text.delete(1.0, tk.END)
                    self.prompt_text.config(state="disabled")
                    
                    self.result_text.config(state="normal")
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.config(state="disabled")
                else:
                    messagebox.showerror("错误", "删除失败")
                    
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {str(e)}")
    
    def _copy_result(self) -> None:
        """
        复制分析结果到剪贴板
        """
        result_text = self.result_text.get(1.0, tk.END).strip()
        if result_text:
            self.history_window.clipboard_clear()
            self.history_window.clipboard_append(result_text)
            messagebox.showinfo("成功", "分析结果已复制到剪贴板")
        else:
            messagebox.showwarning("警告", "没有可复制的内容")
    
    def _save_result_as_text(self) -> None:
        """
        保存分析结果为文本文件
        """
        result_text = self.result_text.get(1.0, tk.END).strip()
        if not result_text:
            messagebox.showwarning("警告", "没有可保存的内容")
            return
        
        # 获取当前选中记录的信息
        sequence_id = self.seq_label.cget("text")
        file_name = self.file_label.cget("text").split(" (")[0]  # 去掉文件大小部分
        
        # 默认文件名
        default_filename = f"{sequence_id}_{file_name}_分析结果.txt"
        
        # 选择保存位置
        file_path = filedialog.asksaveasfilename(
            title="保存分析结果",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialvalue=default_filename
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"视频分析结果\n")
                    f.write(f"序列号: {sequence_id}\n")
                    f.write(f"文件名: {file_name}\n")
                    f.write(f"分析时间: {self.time_label.cget('text')}\n")
                    f.write(f"\n分析提示:\n{self.prompt_text.get(1.0, tk.END).strip()}\n")
                    f.write(f"\n分析结果:\n{result_text}\n")
                
                messagebox.showinfo("成功", f"分析结果已保存到: {file_path}")
                
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def _export_to_csv(self) -> None:
        """
        导出记录到CSV文件
        """
        if not self.filtered_data:
            messagebox.showwarning("警告", "没有可导出的数据")
            return
        
        # 选择保存位置
        file_path = filedialog.asksaveasfilename(
            title="导出CSV文件",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
            initialvalue="视频分析记录.csv"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    fieldnames = [
                        '序列号', '文件名', '文件路径', '文件大小(字节)', '文件类型',
                        '分析提示', '分析结果', 'OSS链接', 'OSS文件名', '创建时间', '更新时间'
                    ]
                    
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for record in self.filtered_data:
                        writer.writerow({
                            '序列号': record.get('sequence_id', ''),
                            '文件名': record.get('file_name', ''),
                            '文件路径': record.get('file_path', ''),
                            '文件大小(字节)': record.get('file_size', 0),
                            '文件类型': record.get('mime_type', ''),
                            '分析提示': record.get('analysis_prompt', ''),
                            '分析结果': record.get('analysis_result', ''),
                            '创建时间': record.get('created_at', ''),
                            '更新时间': record.get('updated_at', '')
                        })
                
                messagebox.showinfo("成功", f"数据已导出到: {file_path}")
                
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def _sync_all_to_feishu(self) -> None:
        """
        同步所有记录到飞书多维表格
        """
        try:
            # 检查飞书配置
            if not feishu_sync.test_connection():
                messagebox.showerror("错误", "飞书连接失败，请检查配置")
                return
            
            # 统计已同步和未同步记录数
            synced_count = sum(1 for record in self.history_data if record.get('feishu_record_id'))
            unsynced_count = len(self.history_data) - synced_count
            
            # 确认对话框
            confirm_message = f"确定要将所有 {len(self.history_data)} 条记录同步到飞书多维表格吗？\n\n"
            confirm_message += f"未同步记录: {unsynced_count} 条（将新建）\n"
            confirm_message += f"已同步记录: {synced_count} 条（将更新）"
            
            result = messagebox.askyesno("确认同步", confirm_message)
            
            if not result:
                return
            
            # 创建进度窗口
            progress_window = tk.Toplevel(self.history_window)
            progress_window.title("同步进度")
            progress_window.geometry("400x150")
            progress_window.resizable(False, False)
            progress_window.transient(self.history_window)
            progress_window.grab_set()
            
            # 居中显示
            progress_window.geometry("+%d+%d" % (
                self.history_window.winfo_rootx() + 400,
                self.history_window.winfo_rooty() + 300
            ))
            
            # 进度标签
            progress_label = tk.Label(
                progress_window,
                text="正在同步记录到飞书...",
                font=("Arial", 10)
            )
            progress_label.pack(pady=20)
            
            # 进度条
            progress_bar = ttk.Progressbar(
                progress_window,
                mode='determinate',
                length=300
            )
            progress_bar.pack(pady=10)
            
            # 状态标签
            status_label = tk.Label(
                progress_window,
                text="准备中...",
                font=("Arial", 9),
                fg="#666666"
            )
            status_label.pack()
            
            progress_window.update()
            
            # 执行同步 - 调用修改后的sync_all_records_to_feishu方法
            result = feishu_sync.sync_all_records_to_feishu(include_synced=True)
            
            progress_window.destroy()
            
            # 显示结果
            success_count = result.get('success', 0)
            failed_count = result.get('failed', 0)
            created_count = result.get('created', 0)
            updated_count = result.get('updated', 0)
            
            result_message = f"同步完成！\n\n"
            result_message += f"总计处理: {len(self.history_data)} 条\n"
            result_message += f"成功同步: {success_count} 条\n"
            result_message += f"  - 新建记录: {created_count} 条\n"
            result_message += f"  - 更新记录: {updated_count} 条\n"
            result_message += f"同步失败: {failed_count} 条"
            
            if failed_count > 0:
                messagebox.showwarning("同步完成", result_message)
            else:
                messagebox.showinfo("同步完成", result_message)
            
            # 刷新数据
            self._load_history_data()
            
        except Exception as e:
            messagebox.showerror("错误", f"同步失败: {str(e)}")
    
    def _sync_selected_to_feishu(self) -> None:
        """
        同步选中的记录到飞书多维表格
        """
        try:
            # 获取选中的记录
            selected_items = self.tree.selection()
            if not selected_items:
                messagebox.showwarning("提示", "请先选择要同步的记录")
                return
            
            # 检查飞书配置
            if not feishu_sync.test_connection():
                messagebox.showerror("错误", "飞书连接失败，请检查配置")
                return
            
            # 获取选中记录的数据
            selected_records = []
            for selected_item in selected_items:
                # 从隐藏的sequence_id_data列获取正确的sequence_id
                sequence_id = self.tree.set(selected_item, "sequence_id_data")
                
                # 查找对应的记录数据
                for record in self.history_data:
                    if record.get('sequence_id') == sequence_id:
                        selected_records.append(record)
                        break
            
            if not selected_records:
                messagebox.showerror("错误", "未找到选中的记录数据")
                return
            
            # 统计选中记录的同步状态
            synced_count = sum(1 for record in selected_records if record.get('feishu_record_id'))
            unsynced_count = len(selected_records) - synced_count
            
            # 确认同步
            if len(selected_records) == 1:
                file_name = selected_records[0].get('file_name', '未知文件')
                confirm_message = f"确定要将记录 '{file_name}' 同步到飞书多维表格吗？"
                if selected_records[0].get('feishu_record_id'):
                    confirm_message += "\n\n注意：此记录已同步，将执行更新操作。"
            else:
                confirm_message = f"确定要将选中的 {len(selected_records)} 条记录同步到飞书多维表格吗？\n\n"
                confirm_message += f"未同步记录: {unsynced_count} 条（将新建）\n"
                confirm_message += f"已同步记录: {synced_count} 条（将更新）"
            
            result = messagebox.askyesno("确认同步", confirm_message)
            
            if not result:
                return
            
            # 创建进度窗口（如果选中多条记录）
            progress_window = None
            progress_bar = None
            status_label = None
            
            if len(selected_records) > 1:
                progress_window = tk.Toplevel(self.history_window)
                progress_window.title("同步进度")
                progress_window.geometry("400x150")
                progress_window.resizable(False, False)
                progress_window.transient(self.history_window)
                progress_window.grab_set()
                
                # 居中显示
                progress_window.geometry("+%d+%d" % (
                    self.history_window.winfo_rootx() + 400,
                    self.history_window.winfo_rooty() + 300
                ))
                
                # 进度标签
                progress_label = tk.Label(
                    progress_window,
                    text="正在同步选中记录到飞书...",
                    font=("Arial", 10)
                )
                progress_label.pack(pady=20)
                
                # 进度条
                progress_bar = ttk.Progressbar(
                    progress_window,
                    mode='determinate',
                    length=300,
                    maximum=len(selected_records)
                )
                progress_bar.pack(pady=10)
                
                # 状态标签
                status_label = tk.Label(
                    progress_window,
                    text="准备中...",
                    font=("Arial", 9),
                    fg="#666666"
                )
                status_label.pack()
                
                progress_window.update()
            
            # 执行同步
            success_count = 0
            failed_count = 0
            updated_count = 0
            created_count = 0
            
            for i, record in enumerate(selected_records):
                sequence_id = record['sequence_id']
                file_name = record.get('file_name', '未知文件')
                
                # 更新进度
                if progress_bar:
                    progress_bar['value'] = i + 1
                    status_label.config(text=f"正在同步: {file_name} ({i+1}/{len(selected_records)})")
                    progress_window.update()
                
                try:
                    # 统一使用sync_record_to_feishu方法，支持重复同步
                    # 对于已同步的记录，使用force_resync=True强制重新同步
                    force_resync = bool(record.get('feishu_record_id'))
                    
                    if feishu_sync.sync_record_to_feishu(sequence_id, force_resync=force_resync):
                        success_count += 1
                        if force_resync:
                            updated_count += 1
                        else:
                            created_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    failed_count += 1
                    print(f"同步记录 {sequence_id} 失败: {e}")
                
                # 添加小延迟避免API限流
                if len(selected_records) > 1:
                    time.sleep(0.1)
            
            if progress_window:
                progress_window.destroy()
            
            # 显示结果
            if len(selected_records) == 1:
                if success_count > 0:
                    # 统一显示为"同步"，因为现在支持重复同步
                    messagebox.showinfo("成功", "记录已成功同步到飞书多维表格")
                else:
                    messagebox.showerror("错误", "同步失败，请检查网络连接和飞书配置")
            else:
                result_message = f"批量同步完成！\n\n"
                result_message += f"总计处理: {len(selected_records)} 条\n"
                result_message += f"成功同步: {success_count} 条\n"
                if created_count > 0:
                    result_message += f"  - 新建记录: {created_count} 条\n"
                if updated_count > 0:
                    result_message += f"  - 更新记录: {updated_count} 条\n"
                result_message += f"同步失败: {failed_count} 条"
                
                if failed_count > 0:
                    messagebox.showwarning("同步完成", result_message)
                else:
                    messagebox.showinfo("同步完成", result_message)
            
            # 刷新数据
            self._load_history_data()
            
            # 重新选中记录
            if len(selected_records) == 1:
                sequence_id = selected_records[0]['sequence_id']
                for item in self.tree.get_children():
                    if self.tree.item(item)['values'][0] == sequence_id:
                        self.tree.selection_set(item)
                        self.tree.focus(item)
                        break
                
        except Exception as e:
            messagebox.showerror("错误", f"同步失败: {str(e)}")
    
    def _sync_all_to_doc(self) -> None:
        """
        同步所有记录到飞书云文档
        """
        try:
            # 检查飞书云文档配置
            doc_sync = FeishuDocSyncService()
            if not doc_sync.is_available():
                messagebox.showerror("错误", "飞书云文档未配置或配置无效，请检查设置")
                return
            
            if not doc_sync.test_connection():
                messagebox.showerror("错误", "飞书云文档连接失败，请检查配置")
                return
            
            # 确认对话框
            confirm_message = f"确定要将所有 {len(self.history_data)} 条记录同步到飞书云文档吗？\n\n"
            confirm_message += "注意：记录将以追加方式添加到云文档中。"
            
            result = messagebox.askyesno("确认同步", confirm_message)
            
            if not result:
                return
            
            # 创建进度窗口
            progress_window = tk.Toplevel(self.history_window)
            progress_window.title("同步进度")
            progress_window.geometry("400x150")
            progress_window.resizable(False, False)
            progress_window.transient(self.history_window)
            progress_window.grab_set()
            
            # 居中显示
            progress_window.geometry("+%d+%d" % (
                self.history_window.winfo_rootx() + 400,
                self.history_window.winfo_rooty() + 300
            ))
            
            # 进度标签
            progress_label = tk.Label(
                progress_window,
                text="正在同步记录到飞书云文档...",
                font=("Arial", 10)
            )
            progress_label.pack(pady=20)
            
            # 进度条
            progress_bar = ttk.Progressbar(
                progress_window,
                mode='determinate',
                length=300
            )
            progress_bar.pack(pady=10)
            
            # 状态标签
            status_label = tk.Label(
                progress_window,
                text="准备中...",
                font=("Arial", 9),
                fg="#666666"
            )
            status_label.pack()
            
            progress_window.update()
            
            # 执行同步
            result = doc_sync.sync_history_data(self.history_data)
            
            progress_window.destroy()
            
            # 显示结果
            success_count = result.get('success', 0)
            failed_count = result.get('failed', 0)
            
            result_message = f"同步完成！\n\n"
            result_message += f"总计处理: {len(self.history_data)} 条\n"
            result_message += f"成功同步: {success_count} 条\n"
            result_message += f"同步失败: {failed_count} 条"
            
            if failed_count > 0:
                messagebox.showwarning("同步完成", result_message)
            else:
                messagebox.showinfo("同步完成", result_message)
            
        except Exception as e:
            messagebox.showerror("错误", f"同步失败: {str(e)}")
    
    def _sync_selected_to_doc(self) -> None:
        """
        同步选中的记录到飞书云文档
        """
        try:
            # 获取选中的记录
            selected_items = self.tree.selection()
            if not selected_items:
                messagebox.showwarning("提示", "请先选择要同步的记录")
                return
            
            # 检查飞书云文档配置
            doc_sync = FeishuDocSyncService()
            if not doc_sync.is_available():
                messagebox.showerror("错误", "飞书云文档未配置或配置无效，请检查设置")
                return
            
            if not doc_sync.test_connection():
                messagebox.showerror("错误", "飞书云文档连接失败，请检查配置")
                return
            
            # 获取选中记录的数据
            selected_records = []
            for selected_item in selected_items:
                # 从隐藏的sequence_id_data列获取正确的sequence_id
                sequence_id = self.tree.set(selected_item, "sequence_id_data")
                
                # 查找对应的记录数据
                for record in self.history_data:
                    if record.get('sequence_id') == sequence_id:
                        selected_records.append(record)
                        break
            
            if not selected_records:
                messagebox.showerror("错误", "未找到选中的记录数据")
                return
            
            # 确认同步
            if len(selected_records) == 1:
                file_name = selected_records[0].get('file_name', '未知文件')
                confirm_message = f"确定要将记录 '{file_name}' 同步到飞书云文档吗？"
            else:
                confirm_message = f"确定要将选中的 {len(selected_records)} 条记录同步到飞书云文档吗？\n\n"
                confirm_message += "注意：记录将以追加方式添加到云文档中。"
            
            result = messagebox.askyesno("确认同步", confirm_message)
            
            if not result:
                return
            
            # 创建进度窗口（如果选中多条记录）
            progress_window = None
            progress_bar = None
            status_label = None
            
            if len(selected_records) > 1:
                progress_window = tk.Toplevel(self.history_window)
                progress_window.title("同步进度")
                progress_window.geometry("400x150")
                progress_window.resizable(False, False)
                progress_window.transient(self.history_window)
                progress_window.grab_set()
                
                # 居中显示
                progress_window.geometry("+%d+%d" % (
                    self.history_window.winfo_rootx() + 400,
                    self.history_window.winfo_rooty() + 300
                ))
                
                # 进度标签
                progress_label = tk.Label(
                    progress_window,
                    text="正在同步选中记录到飞书云文档...",
                    font=("Arial", 10)
                )
                progress_label.pack(pady=20)
                
                # 进度条
                progress_bar = ttk.Progressbar(
                    progress_window,
                    mode='determinate',
                    length=300,
                    maximum=len(selected_records)
                )
                progress_bar.pack(pady=10)
                
                # 状态标签
                status_label = tk.Label(
                    progress_window,
                    text="准备中...",
                    font=("Arial", 9),
                    fg="#666666"
                )
                status_label.pack()
                
                progress_window.update()
            
            # 执行同步
            success_count = 0
            failed_count = 0
            
            for i, record in enumerate(selected_records):
                file_name = record.get('file_name', '未知文件')
                
                # 更新进度
                if progress_bar:
                    progress_bar['value'] = i + 1
                    status_label.config(text=f"正在同步: {file_name} ({i+1}/{len(selected_records)})")
                    progress_window.update()
                
                try:
                    if doc_sync.sync_record(record):
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    failed_count += 1
                    print(f"同步记录失败: {e}")
                
                # 添加小延迟避免API限流
                if len(selected_records) > 1:
                    time.sleep(0.1)
            
            if progress_window:
                progress_window.destroy()
            
            # 显示结果
            if len(selected_records) == 1:
                if success_count > 0:
                    messagebox.showinfo("成功", "记录已成功同步到飞书云文档")
                else:
                    messagebox.showerror("错误", "同步失败，请检查网络连接和飞书配置")
            else:
                result_message = f"批量同步完成！\n\n"
                result_message += f"总计处理: {len(selected_records)} 条\n"
                result_message += f"成功同步: {success_count} 条\n"
                result_message += f"同步失败: {failed_count} 条"
                
                if failed_count > 0:
                    messagebox.showwarning("同步完成", result_message)
                else:
                    messagebox.showinfo("同步完成", result_message)
            
        except Exception as e:
            messagebox.showerror("错误", f"同步失败: {str(e)}")
    
    def _generate_field_template(self) -> None:
        """
        基于选中的历史记录生成字段模板
        """
        try:
            # 获取选中的记录
            selected_items = self.tree.selection()
            if not selected_items:
                messagebox.showwarning("提示", "请先选择一条历史记录")
                return
            
            # 获取记录详情
            item = selected_items[0]
            sequence_id = self.tree.item(item, "values")[0]
            
            # 从数据库获取完整记录
            record = None
            for data in self.history_data:
                if data.get('sequence_id') == sequence_id:
                    record = data
                    break
            
            if not record:
                messagebox.showerror("错误", "未找到选中的记录")
                return
            
            # 确认操作
            result = messagebox.askyesno(
                "确认生成模板", 
                f"将基于记录 '{record.get('file_name', 'Unknown')}' 生成字段模板。\n\n"
                f"生成的模板将保持该记录中的原始表头字段。\n\n"
                f"是否继续？"
            )
            
            if not result:
                return
            
            # 创建智能字段设置器
            smart_setup = SmartFieldSetup(db, feishu_sync.feishu_client)
            
            # 基于单条记录生成模板
            template_result = smart_setup.generate_template_from_single_record(record)
            
            if template_result.get("status") == "success":
                template_info = template_result.get("template_summary", {})
                messagebox.showinfo(
                    "模板生成成功", 
                    f"字段模板生成完成！\n\n"
                    f"📊 基于记录：{record.get('file_name', 'Unknown')}\n"
                    f"📋 生成字段数：{template_info.get('total_fields', 0)}\n"
                    f"📄 模板文件：{template_result.get('template_file', 'N/A')}\n\n"
                    f"📝 下一步操作：\n"
                    f"1. 打开飞书多维表格\n"
                    f"2. 根据生成的模板手动创建字段\n"
                    f"3. 完成后即可正常同步数据"
                )
            else:
                messagebox.showerror(
                    "模板生成失败", 
                    f"生成失败：{template_result.get('message', '未知错误')}"
                )
                
        except Exception as e:
            messagebox.showerror("错误", f"生成字段模板失败: {str(e)}")
    
    def _edit_record_content(self) -> None:
        """
        编辑记录内容
        """
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要编辑的记录")
            return
        
        # 从隐藏的sequence_id_data列获取正确的sequence_id
        item = selected_items[0]
        sequence_id = self.tree.set(item, "sequence_id_data")
        
        # 从历史数据中找到对应记录
        record = None
        for r in self.history_data:
            if r.get('sequence_id') == sequence_id:
                record = r
                break
        
        if not record:
            messagebox.showerror("错误", "未找到对应的记录")
            return
        
        # 打开编辑对话框
        self._open_edit_dialog(record)
    
    def _open_edit_dialog(self, record: Dict) -> None:
        """
        打开编辑对话框
        
        Args:
            record (Dict): 要编辑的记录
        """
        # 创建编辑窗口
        edit_window = tk.Toplevel(self.history_window)
        edit_window.title(f"编辑记录 - {record.get('sequence_id', '')}")
        edit_window.geometry("800x600")
        edit_window.transient(self.history_window)
        edit_window.grab_set()
        
        # 主框架
        main_frame = tk.Frame(edit_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(
            main_frame,
            text=f"编辑记录内容 - {record.get('file_name', '')}",
            font=("Arial", 14, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 20))
        
        # 分析提示编辑区域
        prompt_label = tk.Label(main_frame, text="分析提示:", font=("Arial", 12, "bold"))
        prompt_label.pack(anchor="w", pady=(0, 5))
        
        prompt_text = scrolledtext.ScrolledText(
            main_frame,
            height=8,
            wrap=tk.WORD,
            font=("Arial", 10)
        )
        prompt_text.pack(fill="x", pady=(0, 15))
        prompt_text.insert(1.0, record.get('analysis_prompt', ''))
        
        # 分析结果编辑区域
        result_label = tk.Label(main_frame, text="分析结果:", font=("Arial", 12, "bold"))
        result_label.pack(anchor="w", pady=(0, 5))
        
        result_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Arial", 10)
        )
        result_text.pack(fill="both", expand=True, pady=(0, 20))
        result_text.insert(1.0, record.get('analysis_result', ''))
        
        # 按钮框架
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill="x")
        
        # 取消按钮
        cancel_btn = ttk.Button(
            btn_frame,
            text="取消",
            command=edit_window.destroy
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        # 保存按钮
        save_btn = ttk.Button(
            btn_frame,
            text="保存",
            command=lambda: self._save_edited_content(
                edit_window, record, prompt_text, result_text
            )
        )
        save_btn.pack(side="right")
        
        # 居中显示窗口
        edit_window.update_idletasks()
        x = (edit_window.winfo_screenwidth() // 2) - (edit_window.winfo_width() // 2)
        y = (edit_window.winfo_screenheight() // 2) - (edit_window.winfo_height() // 2)
        edit_window.geometry(f"+{x}+{y}")
    
    def _save_edited_content(self, edit_window: tk.Toplevel, record: Dict, 
                           prompt_text: scrolledtext.ScrolledText, 
                           result_text: scrolledtext.ScrolledText) -> None:
        """
        保存编辑的内容
        
        Args:
            edit_window (tk.Toplevel): 编辑窗口
            record (Dict): 原始记录
            prompt_text (scrolledtext.ScrolledText): 提示文本框
            result_text (scrolledtext.ScrolledText): 结果文本框
        """
        try:
            # 获取编辑后的内容
            new_prompt = prompt_text.get(1.0, tk.END).strip()
            new_result = result_text.get(1.0, tk.END).strip()
            
            # 检查是否有修改
            original_prompt = record.get('analysis_prompt', '').strip()
            original_result = record.get('analysis_result', '').strip()
            
            if new_prompt == original_prompt and new_result == original_result:
                messagebox.showinfo("提示", "内容没有修改")
                edit_window.destroy()
                return
            
            # 确认保存
            if not messagebox.askyesno("确认", "确定要保存修改吗？"):
                return
            
            # 准备更新数据
            update_fields = {}
            if new_prompt != original_prompt:
                update_fields['analysis_prompt'] = new_prompt
            if new_result != original_result:
                update_fields['analysis_result'] = new_result
            
            # 更新数据库
            success = db.update_analysis_fields(record['sequence_id'], update_fields)
            
            if success:
                messagebox.showinfo("成功", "记录已成功更新")
                
                # 更新本地数据
                for r in self.history_data:
                    if r.get('sequence_id') == record['sequence_id']:
                        if 'analysis_prompt' in update_fields:
                            r['analysis_prompt'] = new_prompt
                        if 'analysis_result' in update_fields:
                            r['analysis_result'] = new_result
                        break
                
                # 刷新界面显示
                self._display_record_details(record)
                
                # 关闭编辑窗口
                edit_window.destroy()
            else:
                messagebox.showerror("错误", "保存失败，请重试")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存时发生错误: {str(e)}")
    
    def _on_tree_click(self, event) -> None:
        """
        处理树形视图点击事件
        
        Args:
            event: 点击事件
        """
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#1":  # 选择列
                item = self.tree.identify_row(event.y)
                if item:
                    self._toggle_item_selection(item)
    
    def _toggle_item_selection(self, item_id: str) -> None:
        """
        切换单个项目的选择状态
        
        Args:
            item_id (str): 树形视图项目ID
        """
        values = self.tree.item(item_id, 'values')
        if not values:
            return
            
        sequence_id = values[1]  # 序列号在第二列
        
        if sequence_id in self.selected_items:
            # 取消选择
            del self.selected_items[sequence_id]
            self.tree.set(item_id, "选择", "☐")
        else:
            # 选择
            self.selected_items[sequence_id] = item_id
            self.tree.set(item_id, "选择", "☑")
        
        # 更新全选状态
        self._update_select_all_state()
    
    def _toggle_select_all(self) -> None:
        """
        切换全选状态
        """
        self.select_all_state = not self.select_all_state
        
        if self.select_all_state:
            # 全选
            self.selected_items.clear()
            for item_id in self.tree.get_children():
                values = self.tree.item(item_id, 'values')
                if values:
                    sequence_id = values[1]
                    self.selected_items[sequence_id] = item_id
                    self.tree.set(item_id, "选择", "☑")
            self.tree.heading("选择", text="☑")
        else:
            # 取消全选
            self.selected_items.clear()
            for item_id in self.tree.get_children():
                self.tree.set(item_id, "选择", "☐")
            self.tree.heading("选择", text="☐")
    
    def _update_select_all_state(self) -> None:
        """
        更新全选按钮状态
        """
        total_items = len(self.tree.get_children())
        selected_items = len(self.selected_items)
        
        if selected_items == 0:
            self.select_all_state = False
            self.tree.heading("选择", text="☐")
        elif selected_items == total_items:
            self.select_all_state = True
            self.tree.heading("选择", text="☑")
        else:
            self.select_all_state = False
            self.tree.heading("选择", text="☐")
    
    def _batch_delete_records(self) -> None:
        """
        批量删除选中的记录
        """
        if not self.selected_items:
            messagebox.showwarning("警告", "请先选择要删除的记录")
            return
        
        selected_count = len(self.selected_items)
        
        # 确认删除
        if messagebox.askyesno("确认批量删除", 
                              f"确定要删除选中的 {selected_count} 条记录吗？\n\n此操作不可撤销！"):
            try:
                # 获取选中的序列号列表
                sequence_ids = list(self.selected_items.keys())
                
                # 批量删除
                result = db.delete_multiple_analysis_results(sequence_ids)
                
                # 显示结果
                deleted_count = result['deleted']
                failed_count = result['failed']
                
                if failed_count == 0:
                    messagebox.showinfo("删除成功", f"成功删除 {deleted_count} 条记录")
                else:
                    messagebox.showwarning("部分删除失败", 
                                         f"成功删除 {deleted_count} 条记录\n删除失败 {failed_count} 条记录")
                
                # 清空选择状态
                self.selected_items.clear()
                self.select_all_state = False
                
                # 重新加载数据
                self._load_history_data()
                
                # 清空详情显示
                self._clear_details_display()
                
            except Exception as e:
                messagebox.showerror("错误", f"批量删除失败: {str(e)}")
    
    def _delete_all_records(self) -> None:
        """
        删除所有记录
        """
        # 获取总记录数
        total_count = len(self.history_data)
        
        if total_count == 0:
            messagebox.showinfo("提示", "没有记录可以删除")
            return
        
        # 确认删除
        if messagebox.askyesno("确认删除所有数据", 
                              f"确定要删除所有 {total_count} 条记录吗？\n\n此操作将清空所有历史数据，不可撤销！",
                              icon="warning"):
            
            # 二次确认
            if messagebox.askyesno("最终确认", 
                                  "这是最后一次确认！\n\n删除后所有分析历史将永久丢失！\n\n确定继续吗？",
                                  icon="warning"):
                try:
                    # 删除所有记录
                    result = db.delete_all_analysis_results()
                    deleted_count = result['deleted']
                    
                    messagebox.showinfo("删除完成", f"成功删除所有 {deleted_count} 条记录")
                    
                    # 清空选择状态
                    self.selected_items.clear()
                    self.select_all_state = False
                    
                    # 重新加载数据
                    self._load_history_data()
                    
                    # 清空详情显示
                    self._clear_details_display()
                    
                except Exception as e:
                    messagebox.showerror("错误", f"删除所有记录失败: {str(e)}")
    
    def _clear_details_display(self) -> None:
        """
        清空详情显示区域
        """
        self.seq_label.config(text="")
        self.file_label.config(text="")
        self.time_label.config(text="")
        
        self.prompt_text.config(state="normal")
        self.prompt_text.delete(1.0, tk.END)
        self.prompt_text.config(state="disabled")
        
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state="disabled")
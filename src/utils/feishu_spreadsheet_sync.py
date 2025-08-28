#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书电子表格同步服务模块
专门用于与飞书云文档中的电子表格进行数据同步
"""

import logging
import threading
import time
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import uuid

from ..api.feishu_client import FeishuClient
from .config import config
from .database import db
from .custom_field_mapper import CustomFieldMapper
from .ai_output_adapter import AIOutputAdapter

class FeishuSpreadsheetSync:
    """
    飞书电子表格同步服务类
    提供与飞书云文档电子表格的专门同步功能
    """
    
    def __init__(self):
        """
        初始化飞书电子表格同步服务
        """
        self.feishu_client = None
        self.sync_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        self.custom_mapper = CustomFieldMapper()
        self.ai_adapter = AIOutputAdapter()
        self.last_sync_time = None
        self.spreadsheet_token = None  # 电子表格token
        self.sheet_id = None  # 工作表ID
        self._init_client()
        
    def _init_client(self):
        """
        初始化飞书客户端
        """
        try:
            # 检查电子表格配置是否启用
            if config.is_feishu_spreadsheet_valid():
                self.feishu_client = FeishuClient(
                    app_id=config.feishu_app_id,
                    app_secret=config.feishu_app_secret
                )
                # 获取电子表格配置
                self.spreadsheet_token = config.feishu_spreadsheet_token
                self.sheet_id = config.feishu_sheet_id
                self.logger.info("飞书电子表格同步客户端初始化成功")
            else:
                self.logger.info("飞书电子表格同步未启用或配置不完整")
        except Exception as e:
            self.logger.error(f"初始化飞书电子表格客户端失败: {e}")
            self.feishu_client = None
    
    def test_connection(self) -> bool:
        """
        测试飞书电子表格连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            if not self.feishu_client:
                self._init_client()
                
            if not self.feishu_client:
                return False
                
            if not self.spreadsheet_token or not self.sheet_id:
                self.logger.error("电子表格配置不完整")
                return False
                
            # 测试获取电子表格信息
            # _make_request方法在成功时返回数据部分，失败时返回None
            response = self.feishu_client.get_spreadsheet_info(self.spreadsheet_token)
            if response is not None:
                self.logger.info("飞书电子表格连接测试成功")
                return True
            else:
                self.logger.error("飞书电子表格连接测试失败")
                return False
                
        except Exception as e:
            self.logger.error(f"测试飞书电子表格连接异常: {e}")
            return False
    
    def setup_spreadsheet_structure(self) -> bool:
        """
        设置电子表格结构
        
        Returns:
            bool: 设置是否成功
        """
        try:
            if not self.test_connection():
                return False
                
            # 定义表头结构
            headers = [
                "序列号",
                "文件名", 
                "视频内容摘要",
                "详细内容描述",
                "关键词标签",
                "主要对象",
                "分析时间",
                "同步时间",
                "状态"
            ]
            
            # 设置表头
            success = self.feishu_client.update_spreadsheet_range(
                spreadsheet_token=self.spreadsheet_token,
                sheet_id=self.sheet_id,
                range_str="A1:I1",
                values=[headers]
            )
            
            if success:
                self.logger.info("电子表格结构设置成功")
                return True
            else:
                self.logger.error("电子表格结构设置失败")
                return False
                
        except Exception as e:
            self.logger.error(f"设置电子表格结构异常: {e}")
            return False
    
    def sync_record_to_spreadsheet(self, sequence_id: str, force_update: bool = False) -> bool:
        """
        同步单条记录到电子表格
        
        Args:
            sequence_id (str): 记录序列号
            force_update (bool): 是否强制更新已存在的记录
            
        Returns:
            bool: 同步是否成功
        """
        with self.sync_lock:
            try:
                self.logger.info(f"开始同步记录 {sequence_id} 到电子表格")
                
                # 检查配置
                if not self.spreadsheet_token or not self.sheet_id:
                    self.logger.error(f"电子表格配置不完整: token={bool(self.spreadsheet_token)}, sheet_id={bool(self.sheet_id)}")
                    return False
                
                if not self.test_connection():
                    self.logger.error("飞书电子表格连接失败")
                    return False
                    
                # 获取记录数据
                record = db.get_analysis_by_sequence_id(sequence_id)
                if not record:
                    self.logger.error(f"未找到序列号为 {sequence_id} 的记录")
                    return False
                
                self.logger.info(f"获取到记录数据: {record.keys()}")
                
                # 检查是否已同步到电子表格
                spreadsheet_row = record.get('feishu_spreadsheet_row')
                if spreadsheet_row and not force_update:
                    self.logger.info(f"记录 {sequence_id} 已同步到电子表格第 {spreadsheet_row} 行")
                    return True
                
                # 准备同步数据
                sync_data = self._prepare_sync_data(record)
                self.logger.info(f"准备的同步数据: {sync_data}")
                
                # 查找或创建行
                if spreadsheet_row:
                    # 更新现有行
                    row_number = spreadsheet_row
                    self.logger.info(f"更新现有行: {row_number}")
                else:
                    # 查找下一个可用行
                    row_number = self._find_next_available_row()
                    if not row_number:
                        self.logger.error("无法找到可用行")
                        return False
                    self.logger.info(f"找到可用行: {row_number}")
                
                # 更新电子表格
                range_str = f"A{row_number}:I{row_number}"
                self.logger.info(f"准备更新电子表格范围: {range_str}")
                self.logger.info(f"电子表格token: {self.spreadsheet_token[:10]}...")
                self.logger.info(f"工作表ID: {self.sheet_id}")
                
                success = self.feishu_client.update_spreadsheet_range(
                    spreadsheet_token=self.spreadsheet_token,
                    sheet_id=self.sheet_id,
                    range_str=range_str,
                    values=[sync_data]
                )
                
                if success:
                    # 更新本地记录
                    db.update_feishu_spreadsheet_row(sequence_id, row_number)
                    self.last_sync_time = datetime.now()
                    self.logger.info(f"记录 {sequence_id} 成功同步到电子表格第 {row_number} 行")
                    return True
                else:
                    self.logger.error(f"记录 {sequence_id} 同步到电子表格失败")
                    return False
                    
            except Exception as e:
                self.logger.error(f"同步记录到电子表格异常: {e}")
                import traceback
                self.logger.error(f"异常堆栈: {traceback.format_exc()}")
                return False
    
    def sync_all_records_to_spreadsheet(self) -> Dict[str, int]:
        """
        批量同步所有未同步的记录到电子表格
        
        Returns:
            Dict[str, int]: 同步结果统计
        """
        result = {
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        
        try:
            # 获取所有未同步到电子表格的记录
            unsynced_records = db.get_unsynced_spreadsheet_records()
            
            if not unsynced_records:
                self.logger.info("没有需要同步到电子表格的记录")
                return result
            
            self.logger.info(f"开始批量同步 {len(unsynced_records)} 条记录到电子表格")
            
            for record in unsynced_records:
                sequence_id = record['sequence_id']
                
                try:
                    if self.sync_record_to_spreadsheet(sequence_id):
                        result['success'] += 1
                    else:
                        result['failed'] += 1
                        
                    # 添加延迟避免API限流
                    time.sleep(0.2)
                    
                except Exception as e:
                    self.logger.error(f"同步记录 {sequence_id} 到电子表格失败: {e}")
                    result['failed'] += 1
            
            self.logger.info(f"批量同步完成: 成功 {result['success']} 条, 失败 {result['failed']} 条")
            
        except Exception as e:
            self.logger.error(f"批量同步到电子表格异常: {e}")
            
        return result
    
    def sync_record(self, record: Dict) -> bool:
        """
        同步单条记录到电子表格（兼容历史记录查看器）
        
        Args:
            record (Dict): 记录数据字典
            
        Returns:
            bool: 同步是否成功
        """
        try:
            sequence_id = record.get('sequence_id')
            if not sequence_id:
                self.logger.error("记录缺少sequence_id")
                return False
                
            return self.sync_record_to_spreadsheet(sequence_id)
            
        except Exception as e:
            self.logger.error(f"同步记录到电子表格失败: {e}")
            return False
    
    def _prepare_sync_data(self, record: Dict) -> List[str]:
        """
        准备同步到电子表格的数据
        
        Args:
            record (Dict): 记录数据
            
        Returns:
            List[str]: 格式化的行数据
        """
        try:
            # 获取基本信息
            sequence_id = record.get('sequence_id', '')
            file_name = record.get('file_name', '')
            
            # 解析分析结果文本
            analysis_result = record.get('analysis_result', '')
            if not analysis_result:
                analysis_result = ''
            
            # 从文本中提取结构化数据
            video_content_summary = self._extract_field_from_text(analysis_result, '视频内容摘要')
            detailed_content_description = self._extract_field_from_text(analysis_result, '详细内容描述')
            keyword_tags = self._extract_field_from_text(analysis_result, '关键词标签')
            main_objects = self._extract_field_from_text(analysis_result, '主要对象')
            
            # 如果没有提取到摘要，使用分析结果的前200个字符
            if not video_content_summary and analysis_result:
                video_content_summary = analysis_result[:200] + ('...' if len(analysis_result) > 200 else '')
            
            # 格式化时间
            analysis_time = record.get('created_at', '')
            if analysis_time:
                try:
                    dt = datetime.fromisoformat(analysis_time.replace('Z', '+00:00'))
                    analysis_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            
            sync_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 记录提取的数据用于调试
            self.logger.info(f"提取的同步数据:")
            self.logger.info(f"  序列号: {sequence_id}")
            self.logger.info(f"  文件名: {file_name}")
            self.logger.info(f"  视频内容摘要: {video_content_summary[:100]}...")
            self.logger.info(f"  详细内容描述: {detailed_content_description[:100]}...")
            self.logger.info(f"  关键词标签: {keyword_tags}")
            self.logger.info(f"  主要对象: {main_objects}")
            
            # 构造行数据
            row_data = [
                str(sequence_id),
                str(file_name),
                str(video_content_summary),
                str(detailed_content_description),
                str(keyword_tags),
                str(main_objects),
                str(analysis_time),
                str(sync_time),
                "已同步"
            ]
            
            return row_data
            
        except Exception as e:
            self.logger.error(f"准备同步数据失败: {e}")
            import traceback
            self.logger.error(f"错误堆栈: {traceback.format_exc()}")
            return [str(record.get('sequence_id', '')), '数据处理失败', '', '', '', '', '', '', '错误']
    
    def _extract_field_from_text(self, text: str, field_name: str) -> str:
        """
        从文本中提取指定字段的值
        
        Args:
            text (str): 分析结果文本
            field_name (str): 字段名称
            
        Returns:
            str: 提取的字段值
        """
        if not text or not field_name:
            return ''
        
        try:
            # 构建正则表达式模式
            patterns = [
                rf'{field_name}[:\s]*([^\n]+)',  # 匹配字段名后的内容到换行符
                rf'{field_name}[：\s]*([^\n]+)',  # 中文冒号
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    # 清理可能的多余字符
                    value = re.sub(r'^[\s:：]+', '', value)  # 移除开头的空格和冒号
                    value = re.sub(r'[\s]+$', '', value)     # 移除结尾的空格
                    return value
            
            return ''
            
        except Exception as e:
            self.logger.error(f"提取字段 {field_name} 失败: {e}")
            return ''
    
    def _find_next_available_row(self) -> Optional[int]:
        """
        查找下一个可用的行号
        
        Returns:
            Optional[int]: 可用的行号，如果失败返回None
        """
        try:
            self.logger.info("开始查找下一个可用行")
            
            # 获取当前表格数据范围
            response = self.feishu_client.get_spreadsheet_range(
                spreadsheet_token=self.spreadsheet_token,
                sheet_id=self.sheet_id,
                range_str="A:A"  # 获取A列所有数据
            )
            
            self.logger.info(f"获取表格范围响应: {response}")
            
            if response:
                # 电子表格API直接返回数据，不包含code字段
                if isinstance(response, dict) and 'values' in response:
                    values = response.get('values', [])
                    self.logger.info(f"原始数据行数: {len(values)}")
                    
                    # 找到最后一个非空行
                    last_data_row = 1  # 默认从第2行开始（第1行是表头）
                    for i, row in enumerate(values):
                        # 检查这一行是否有数据（不是None或空字符串）
                        if row and len(row) > 0 and row[0] is not None and str(row[0]).strip():
                            last_data_row = i + 1
                    
                    next_row = last_data_row + 1
                    self.logger.info(f"最后有数据的行: {last_data_row}, 下一个可用行: {next_row}")
                    return next_row
                else:
                    self.logger.warning(f"响应格式异常: {response}")
                    # 如果获取失败，从第2行开始（第1行是表头）
                    return 2
            else:
                self.logger.warning("获取表格范围失败，使用默认行号")
                # 如果获取失败，从第2行开始（第1行是表头）
                return 2
                
        except Exception as e:
            self.logger.error(f"查找可用行失败: {e}")
            import traceback
            self.logger.error(f"异常堆栈: {traceback.format_exc()}")
            return 2  # 默认从第2行开始
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """
        获取同步统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            total_records = db.get_total_records_count()
            synced_to_spreadsheet = db.get_synced_spreadsheet_records_count()
            unsynced_to_spreadsheet = total_records - synced_to_spreadsheet
            
            return {
                'total_records': total_records,
                'synced_to_spreadsheet': synced_to_spreadsheet,
                'unsynced_to_spreadsheet': unsynced_to_spreadsheet,
                'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
                'spreadsheet_enabled': bool(self.spreadsheet_token and self.sheet_id)
            }
            
        except Exception as e:
            self.logger.error(f"获取同步统计信息失败: {e}")
            return {
                'total_records': 0,
                'synced_to_spreadsheet': 0,
                'unsynced_to_spreadsheet': 0,
                'last_sync_time': None,
                'spreadsheet_enabled': False
            }

# 全局实例
feishu_spreadsheet_sync = FeishuSpreadsheetSync()
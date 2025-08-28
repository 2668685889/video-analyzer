#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书字段修复模块
用于处理字段类型不匹配问题并生成正确的数据格式
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

class FeishuFieldFixer:
    """
    飞书字段修复器
    处理字段类型不匹配问题
    """
    
    def __init__(self):
        """
        初始化字段修复器
        """
        self.logger = logging.getLogger(__name__)
        
        # 飞书字段类型映射
        self.field_type_map = {
            1: "文本",
            2: "数字", 
            3: "单选",
            4: "多选",
            5: "日期",
            7: "复选框",
            11: "人员",
            13: "电话号码",
            15: "超链接",
            17: "附件",
            18: "单向关联",
            19: "查找引用",
            20: "公式",
            21: "双向关联",
            22: "地理位置",
            23: "群组",
            1001: "创建时间",
            1002: "最后更新时间",
            1003: "创建人",
            1004: "修改人",
            1005: "自动编号"
        }
        
        # 当前表格的字段配置（从实际API获取）
        self.current_field_config = {
            "视频序列号": {"type": 1, "field_id": "flde3uW61x"},  # 文本
            "视频内容摘要": {"type": 1, "field_id": "fldfefkPtj"},  # 文本
            "详细内容描述": {"type": 1, "field_id": "fldNl7gCfM"},  # 文本
            "关键词标签": {"type": 1, "field_id": "fldH1IYS7n"},  # 文本
            "主要人物对象": {"type": 1, "field_id": "fldm9PZiIG"},  # 文本
            "视频源路径": {"type": 1, "field_id": "fldyUJVT8n"}   # 文本
        }
    
    def convert_data_for_feishu_field(self, field_name: str, value: Any) -> Any:
        """
        根据飞书字段类型转换数据格式
        
        Args:
            field_name (str): 字段名称
            value (Any): 原始值
            
        Returns:
            Any: 转换后的值，如果字段不支持则返回None
        """
        if field_name not in self.current_field_config:
            self.logger.warning(f"未知字段: {field_name}")
            return None
        
        field_config = self.current_field_config[field_name]
        field_type = field_config["type"]
        
        try:
            if field_type == 1:  # 文本类型
                return str(value) if value is not None else ""
            
            elif field_type == 2:  # 数字类型
                if isinstance(value, (int, float)):
                    return value
                elif isinstance(value, str) and value.isdigit():
                    return int(value)
                else:
                    self.logger.warning(f"无法将 '{value}' 转换为数字类型")
                    return None
            
            elif field_type == 3:  # 单选类型
                # 强制转换为文本，因为飞书字段配置错误
                self.logger.warning(f"字段 '{field_name}' 配置为单选类型，强制转换为文本")
                return str(value) if value is not None else ""
            
            elif field_type == 4:  # 多选类型
                if isinstance(value, list):
                    return value
                elif isinstance(value, str):
                    # 尝试按逗号分割
                    return [item.strip() for item in value.split(',') if item.strip()]
                else:
                    return [str(value)]
            
            elif field_type == 5:  # 日期类型
                # 强制转换为文本，因为飞书字段配置错误
                self.logger.warning(f"字段 '{field_name}' 配置为日期类型，强制转换为文本")
                return str(value) if value is not None else ""
            
            elif field_type == 7:  # 复选框类型
                return bool(value)
            
            elif field_type == 17:  # 附件类型
                # 强制转换为文本，因为飞书字段配置错误
                self.logger.warning(f"字段 '{field_name}' 配置为附件类型，强制转换为文本")
                return str(value) if value is not None else ""
            
            else:
                self.logger.warning(f"不支持的字段类型: {field_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"转换字段 '{field_name}' 的值 '{value}' 时出错: {str(e)}")
            return None
    
    def get_field_mapping(self) -> Dict[str, str]:
        """
        获取数据库字段到飞书字段的映射关系
        
        Returns:
            Dict[str, str]: 数据库字段名 -> 飞书字段名的映射
        """
        return {
            # 基础字段映射
            "sequence_id": "视频序列号",
            "video_source_path": "视频源路径",
            
            # analysis_result中的字段映射
            "video_content_summary": "视频内容摘要",
            "detailed_content_description": "详细内容描述", 
            "keywords_tags": "关键词标签",
            "main_characters_objects": "主要人物对象"
        }
    
    def prepare_record_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备飞书记录数据
        
        Args:
            raw_data (Dict[str, Any]): 原始数据
            
        Returns:
            Dict[str, Any]: 准备好的飞书记录数据
        """
        prepared_data = {}
        field_mapping = self.get_field_mapping()
        
        # 临时解决方案：跳过已知的问题字段，避免 AttachFieldConvFail 错误
        # 这些字段在飞书表格中被错误配置为非文本类型
        problem_fields = {
            '视频内容摘要': '单选类型，无法接受文本数据',
            '详细内容描述': '日期类型，无法接受文本数据', 
            '关键词标签': '附件类型，无法接受文本数据',
            '主要人物对象': '可能配置错误的字段类型'
        }
        
        for raw_field, feishu_field in field_mapping.items():
            if raw_field in raw_data:
                value = raw_data[raw_field]
                
                # 检查是否为问题字段
                if feishu_field in problem_fields:
                    self.logger.warning(f"⚠️  跳过问题字段: {raw_field} -> {feishu_field} ({problem_fields[feishu_field]})")
                    self.logger.warning(f"    建议在飞书表格中将 '{feishu_field}' 字段类型修改为'单行文本'")
                    continue
                
                # 将数据转换为字符串格式（适用于文本字段）
                if value is not None:
                    # 处理特殊数据类型
                    if isinstance(value, (dict, list)):
                        converted_value = json.dumps(value, ensure_ascii=False)
                    else:
                        converted_value = str(value)
                else:
                    converted_value = ""
                
                prepared_data[feishu_field] = converted_value
                self.logger.info(f"✅ 处理字段: {raw_field} -> {feishu_field} = {converted_value[:100]}{'...' if len(str(converted_value)) > 100 else ''}")
        
        self.logger.info(f"📋 准备的飞书数据字段: {list(prepared_data.keys())}")
        if len(prepared_data) == 0:
            self.logger.error("❌ 没有可同步的字段！所有字段都被跳过了。")
            self.logger.error("   请在飞书表格中修改字段类型为'单行文本'，然后重新同步。")
        
        return prepared_data
    
    def get_supported_fields(self) -> List[str]:
        """
        获取当前支持的字段列表
        
        Returns:
            List[str]: 支持的字段名称列表
        """
        supported_fields = []
        
        for field_name, config in self.current_field_config.items():
            field_type = config["type"]
            
            # 只包含文本类型的字段
            if field_type == 1:  # 文本类型
                supported_fields.append(field_name)
        
        return supported_fields
    
    def generate_field_fix_report(self) -> str:
        """
        生成字段修复报告
        
        Returns:
            str: 修复报告
        """
        report = []
        report.append("=== 飞书字段修复报告 ===")
        report.append("")
        
        supported_fields = []
        problematic_fields = []
        
        for field_name, config in self.current_field_config.items():
            field_type = config["type"]
            field_type_name = self.field_type_map.get(field_type, f"未知({field_type})")
            
            if field_type == 1:  # 文本类型 - 支持
                supported_fields.append(f"✅ {field_name} ({field_type_name})")
            else:
                problematic_fields.append(f"❌ {field_name} ({field_type_name}) - 类型不匹配")
        
        report.append("支持的字段:")
        for field in supported_fields:
            report.append(f"  {field}")
        
        report.append("")
        report.append("有问题的字段:")
        for field in problematic_fields:
            report.append(f"  {field}")
        
        report.append("")
        report.append("建议:")
        report.append("1. 将 '视频内容摘要' 字段类型改为文本类型")
        report.append("2. 将 '详细内容描述' 字段类型改为文本类型")
        report.append("3. 将 '关键词标签' 字段类型改为文本类型或多选类型")
        report.append("4. 或者在代码中只使用支持的字段")
        
        return "\n".join(report)
    
    def create_minimal_test_record(self) -> Dict[str, Any]:
        """
        创建最小化的测试记录（只包含支持的字段）
        
        Returns:
            Dict[str, Any]: 测试记录数据
        """
        test_data = {
            "视频序列号": f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "主要人物对象": "测试人员",
            "视频源路径": "/test/path/video.mp4"
        }
        
        return test_data

# 创建全局实例
feishu_field_fixer = FeishuFieldFixer()
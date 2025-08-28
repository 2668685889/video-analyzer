#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI输出格式适配器
用于处理不同AI模型输出格式的转换和标准化
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class AIOutputAdapter:
    """
    AI输出格式适配器
    负责将不同格式的AI模型输出转换为标准格式
    """
    
    def __init__(self):
        """
        初始化AI输出格式适配器
        """
        self.logger = logging.getLogger(__name__)
        
        # 定义字段映射关系（中文字段名 -> 英文字段名）
        self.field_mapping = {
            "视频序列号": "video_serial_number",
            "视频内容摘要": "video_content_summary",
            "详细内容描述": "detailed_content_description",
            "关键词标签": "keywords_tags",
            "主要对象": "main_characters_objects",
            "主要人物对象": "main_characters_objects",  # 兼容旧格式
            "视频源路径": "video_source_path"
        }
        
        # 定义标准字段列表
        self.standard_fields = [
            "video_serial_number",
            "video_content_summary", 
            "detailed_content_description",
            "keywords_tags",
            "main_characters_objects",
            "video_source_path"
        ]
    
    def detect_format(self, ai_output: Dict[str, Any]) -> str:
        """
        检测AI输出格式类型
        
        Args:
            ai_output (Dict[str, Any]): AI模型输出数据
            
        Returns:
            str: 格式类型 ('chinese_fields', 'english_fields', 'mixed', 'unknown')
        """
        try:
            chinese_fields = set(ai_output.keys()) & set(self.field_mapping.keys())
            english_fields = set(ai_output.keys()) & set(self.standard_fields)
            
            # 优先检测混合格式
            if len(chinese_fields) > 0 and len(english_fields) > 0:
                return 'mixed'
            elif len(chinese_fields) > len(english_fields):
                return 'chinese_fields'
            elif len(english_fields) > len(chinese_fields):
                return 'english_fields'
            else:
                return 'unknown'
                
        except Exception as e:
            self.logger.error(f"检测AI输出格式失败: {str(e)}")
            return 'unknown'
    
    def convert_to_standard_format(self, ai_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        将AI输出转换为标准格式（保持中文字段名）
        
        Args:
            ai_output (Dict[str, Any]): 原始AI输出
            
        Returns:
            Dict[str, Any]: 标准格式的输出
        """
        standard_output = {}
        
        # 定义标准中文字段列表
        standard_chinese_fields = [
            "视频序列号",
            "视频内容摘要", 
            "详细内容描述",
            "关键词标签",
            "主要对象",
            "视频源路径"
        ]
        
        # 创建英文字段名到中文字段名的反向映射
        english_to_chinese = {
            "video_serial_number": "视频序列号",
            "video_content_summary": "视频内容摘要",
            "detailed_content_description": "详细内容描述",
            "keywords_tags": "关键词标签",
            "main_characters_objects": "主要对象",
            "video_source_path": "视频源路径"
        }
        
        # 字段名兼容性映射（处理旧格式）
        field_compatibility = {
            "主要人物对象": "主要对象"
        }
        
        # 处理输入字段
        for input_field, value in ai_output.items():
            target_field = None
            
            # 1. 检查是否是英文字段名，需要转换为中文
            if input_field in english_to_chinese:
                target_field = english_to_chinese[input_field]
                self.logger.debug(f"英文字段转换: {input_field} -> {target_field}")
            
            # 2. 检查是否是中文字段名，直接使用或转换
            elif input_field in standard_chinese_fields:
                target_field = input_field
            
            # 3. 检查兼容性映射
            elif input_field in field_compatibility:
                target_field = field_compatibility[input_field]
                self.logger.debug(f"兼容性转换: {input_field} -> {target_field}")
            
            # 4. 如果找到了目标字段，保存数据
            if target_field and target_field in standard_chinese_fields:
                if value is not None and str(value).strip():
                    standard_output[target_field] = str(value).strip()
                    self.logger.debug(f"字段映射成功: {input_field} -> {target_field} = '{str(value)[:50]}...'")
                else:
                    standard_output[target_field] = ""
            else:
                self.logger.debug(f"未识别的字段: {input_field}")
        
        # 确保所有标准字段都存在
        for field in standard_chinese_fields:
            if field not in standard_output:
                standard_output[field] = ""
        
        return standard_output
    
    def _smart_field_matching(self, ai_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        智能字段匹配（用于处理未知格式）
        
        Args:
            ai_output (Dict[str, Any]): AI模型输出数据
            
        Returns:
            Dict[str, Any]: 匹配后的标准格式数据
        """
        standard_output = {}
        
        # 定义关键词匹配规则
        keyword_rules = {
            "video_serial_number": ["序列号", "serial", "id", "编号"],
            "video_content_summary": ["摘要", "summary", "概要", "简介"],
            "detailed_content_description": ["描述", "description", "详细", "内容"],
            "keywords_tags": ["关键词", "标签", "keywords", "tags"],
            "main_characters_objects": ["对象", "人物", "主要", "characters", "objects"],
            "video_source_path": ["路径", "path", "源", "文件"]
        }
        
        for standard_field, keywords in keyword_rules.items():
            for ai_field, value in ai_output.items():
                if any(keyword in ai_field.lower() for keyword in keywords):
                    standard_output[standard_field] = value
                    self.logger.debug(f"智能匹配: {ai_field} -> {standard_field}")
                    break
        
        return standard_output
    
    def validate_output(self, standard_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证和清理标准输出
        
        Args:
            standard_output (Dict[str, Any]): 标准格式的输出数据
            
        Returns:
            Dict[str, Any]: 验证后的数据和验证报告
        """
        try:
            # 定义标准中文字段列表
            standard_chinese_fields = [
                "视频序列号",
                "视频内容摘要", 
                "详细内容描述",
                "关键词标签",
                "主要对象",
                "视频源路径"
            ]
            
            validation_report = {
                "valid_fields": [],
                "empty_fields": [],
                "invalid_fields": [],
                "total_fields": len(standard_chinese_fields),
                "valid_count": 0
            }
            
            cleaned_output = {}
            
            for field in standard_chinese_fields:
                value = standard_output.get(field, '')
                
                if isinstance(value, str):
                    # 清理字符串值
                    cleaned_value = value.strip()
                    cleaned_output[field] = cleaned_value
                    
                    if cleaned_value:
                        validation_report["valid_fields"].append(field)
                        validation_report["valid_count"] += 1
                    else:
                        validation_report["empty_fields"].append(field)
                else:
                    # 非字符串值转换为字符串
                    cleaned_output[field] = str(value) if value is not None else ''
                    if cleaned_output[field]:
                        validation_report["valid_fields"].append(field)
                        validation_report["valid_count"] += 1
                    else:
                        validation_report["empty_fields"].append(field)
            
            validation_report["success_rate"] = validation_report["valid_count"] / validation_report["total_fields"]
            
            self.logger.info(f"输出验证完成，成功率: {validation_report['success_rate']:.2%}")
            
            return {
                "output": cleaned_output,
                "validation": validation_report
            }
            
        except Exception as e:
            self.logger.error(f"输出验证失败: {str(e)}")
            # 定义标准中文字段列表
            standard_chinese_fields = [
                "视频序列号",
                "视频内容摘要", 
                "详细内容描述",
                "关键词标签",
                "主要对象",
                "视频源路径"
            ]
            return {
                "output": {field: '' for field in standard_chinese_fields},
                "validation": {
                    "valid_fields": [],
                    "empty_fields": standard_chinese_fields,
                    "invalid_fields": [],
                    "total_fields": len(standard_chinese_fields),
                    "valid_count": 0,
                    "success_rate": 0.0
                }
            }
    
    def process_ai_output(self, ai_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理AI输出的完整流程
        
        Args:
            ai_output (Dict[str, Any]): AI模型输出数据
            
        Returns:
            Dict[str, Any]: 处理结果，包含标准输出和验证报告
        """
        try:
            self.logger.info("开始处理AI输出")
            
            # 步骤1: 转换为标准格式
            standard_output = self.convert_to_standard_format(ai_output)
            
            # 步骤2: 验证和清理
            result = self.validate_output(standard_output)
            
            # 添加处理信息
            result["processing_info"] = {
                "timestamp": datetime.now().isoformat(),
                "input_fields": list(ai_output.keys()),
                "format_type": self.detect_format(ai_output),
                "processed_successfully": True
            }
            
            self.logger.info("AI输出处理完成")
            return result
            
        except Exception as e:
            self.logger.error(f"AI输出处理失败: {str(e)}")
            return {
                "output": {field: '' for field in self.standard_fields},
                "validation": {
                    "valid_fields": [],
                    "empty_fields": self.standard_fields,
                    "invalid_fields": [],
                    "total_fields": len(self.standard_fields),
                    "valid_count": 0,
                    "success_rate": 0.0
                },
                "processing_info": {
                    "timestamp": datetime.now().isoformat(),
                    "input_fields": list(ai_output.keys()) if isinstance(ai_output, dict) else [],
                    "format_type": "error",
                    "processed_successfully": False,
                    "error": str(e)
                }
            }

# 创建全局实例
ai_output_adapter = AIOutputAdapter()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字段映射模块
用于自动分析大模型返回内容并生成飞书多维表格字段模板
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging

class FieldMapper:
    """
    字段映射器
    自动分析内容并生成字段映射模板
    """
    
    def __init__(self):
        """
        初始化字段映射器
        """
        self.logger = logging.getLogger(__name__)
        
        # 飞书字段类型映射
        self.feishu_field_types = {
            'text': 1,          # 单行文本
            'multiline_text': 1, # 多行文本
            'number': 2,        # 数字
            'select': 3,        # 单选
            'multiselect': 4,   # 多选
            'datetime': 5,      # 日期时间
            'checkbox': 7,      # 复选框
            'user': 11,         # 人员
            'phone': 13,        # 电话号码
            'url': 15,          # 超链接
            'attachment': 17,   # 附件
            'barcode': 20,      # 条码
            'progress': 21,     # 进度
            'currency': 22,     # 货币
            'rating': 23,       # 评分
            'location': 1001,   # 地理位置
        }
        
        # 基础字段模板
        self.base_fields = {
            "video_serial_number": {
                "chinese_name": "视频序列号",
                "field_type": "text",
                "description": "视频的唯一序列标识",
                "required": True
            },
            "video_content_summary": {
                "chinese_name": "视频内容摘要",
                "field_type": "multiline_text",
                "description": "视频内容的详细摘要",
                "required": True
            },
            "detailed_content_description": {
                "chinese_name": "详细内容描述",
                "field_type": "multiline_text",
                "description": "视频的详细内容描述",
                "required": False
            },
            "keywords_tags": {
                "chinese_name": "关键词标签",
                "field_type": "text",
                "description": "从视频中提取的关键词",
                "required": False
            },
            "main_characters_objects": {
                "chinese_name": "主要人物对象",
                "field_type": "text",
                "description": "视频中的主要人物或对象",
                "required": False
            },
            "video_source_path": {
                "chinese_name": "视频源路径",
                "field_type": "text",
                "description": "视频文件的源路径",
                "required": True
            },
            "file_name": {
                "chinese_name": "文件名称",
                "field_type": "text",
                "description": "视频文件名称",
                "required": True
            },
            "file_size": {
                "chinese_name": "文件大小",
                "field_type": "number",
                "description": "视频文件大小（字节）",
                "required": False
            },
            "file_format": {
                "chinese_name": "文件格式",
                "field_type": "text",
                "description": "视频文件格式",
                "required": False
            },
            "analysis_prompt": {
                "chinese_name": "分析提示词",
                "field_type": "multiline_text",
                "description": "用于分析的提示词",
                "required": False
            },
            "created_time": {
                "chinese_name": "创建时间",
                "field_type": "datetime",
                "description": "记录创建时间",
                "required": True
            }
        }
    
    def analyze_content_structure(self, content: Any) -> Dict[str, Any]:
        """
        分析内容结构，提取可能的字段信息
        
        Args:
            content (Any): 要分析的内容，可以是字符串、字典或其他类型
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        analysis_result = {
            "detected_fields": [],
            "content_type": "unknown",
            "structure_complexity": "simple",
            "suggested_fields": []
        }
        
        try:
            if isinstance(content, dict):
                analysis_result.update(self._analyze_dict_structure(content))
            elif isinstance(content, str):
                # 尝试解析为JSON
                if self._is_json_content(content):
                    analysis_result.update(self._analyze_json_structure(content))
                else:
                    analysis_result.update(self._analyze_text_structure(content))
            else:
                # 处理其他类型的内容
                analysis_result.update(self._analyze_text_structure(str(content)))
                
        except Exception as e:
            self.logger.error(f"内容结构分析失败: {str(e)}")
            
        return analysis_result
    
    def _is_json_content(self, content: str) -> bool:
        """
        判断内容是否为JSON格式
        
        Args:
            content (str): 内容字符串
            
        Returns:
            bool: 是否为JSON格式
        """
        try:
            json.loads(content)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
    
    def _analyze_dict_structure(self, data: dict) -> Dict[str, Any]:
        """
        分析字典结构内容
        
        Args:
            data (dict): 字典数据
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        try:
            detected_fields = []
            
            for key, value in data.items():
                # 保持原始字段名，特别是带空格的字段名
                field_info = self._infer_field_type(key, value)
                detected_fields.append(field_info)
            
            return {
                "detected_fields": detected_fields,
                "content_type": "dict",
                "structure_complexity": "structured"
            }
            
        except Exception as e:
            self.logger.error(f"字典结构分析失败: {str(e)}")
            return {"detected_fields": [], "content_type": "dict_error"}
    
    def _analyze_json_structure(self, content: str) -> Dict[str, Any]:
        """
        分析JSON结构内容
        
        Args:
            content (str): JSON内容
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        try:
            data = json.loads(content)
            
            if isinstance(data, dict):
                return self._analyze_dict_structure(data)
            else:
                return {
                    "detected_fields": [],
                    "content_type": "json",
                    "structure_complexity": "simple"
                }
            
        except Exception as e:
            self.logger.error(f"JSON结构分析失败: {str(e)}")
            return {"detected_fields": [], "content_type": "json_error"}
    
    def _analyze_text_structure(self, content: str) -> Dict[str, Any]:
        """
        分析文本结构内容
        
        Args:
            content (str): 文本内容
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        detected_fields = []
        
        # 检测关键词模式
        keyword_patterns = [
            (r'关键词[：:](.*?)(?=\n|$)', '关键词', 'text'),
            (r'标签[：:](.*?)(?=\n|$)', '标签', 'text'),
            (r'主要内容[：:](.*?)(?=\n|$)', '主要内容', 'multiline_text'),
            (r'摘要[：:](.*?)(?=\n|$)', '内容摘要', 'multiline_text'),
            (r'人物[：:](.*?)(?=\n|$)', '主要人物', 'text'),
            (r'时间[：:](.*?)(?=\n|$)', '时间信息', 'text'),
            (r'地点[：:](.*?)(?=\n|$)', '地点信息', 'text'),
        ]
        
        for pattern, field_name, field_type in keyword_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                detected_fields.append({
                    "field_name": field_name,
                    "field_type": field_type,
                    "sample_value": matches[0][:100] if matches[0] else "",
                    "confidence": 0.8
                })
        
        return {
            "detected_fields": detected_fields,
            "content_type": "text",
            "structure_complexity": "unstructured"
        }
    
    def _infer_field_type(self, key: str, value: Any) -> Dict[str, Any]:
        """
        推断字段类型
        
        Args:
            key (str): 字段名
            value (Any): 字段值
            
        Returns:
            Dict[str, Any]: 字段信息
        """
        # 字段名到描述的映射 - 使用与飞书表格匹配的字段名
        field_descriptions = {
            "video serial number": "视频的唯一序列标识",
            "video_serial_number": "视频的唯一序列标识",
            "videocontentSumary": "视频内容摘要",
            "videgcontedtSumary": "视频内容摘要",  # 处理拼写错误的情况
            "video_content_summary": "视频内容的简要摘要",
            "detailed_content_description": "视频内容的详细描述",
            "keywords_tags": "从视频中提取的关键词和标签",
            "main characters objects": "视频中的主要人物或对象",
            "main_characters_objects": "视频中的主要人物或对象",
            "video source path": "视频文件的源路径",
            "video_source_path": "视频文件的源路径",
            "file_name": "视频文件名称",
            "created_at": "记录创建时间",
            "created_time": "记录创建时间"
        }
        
        # 保持原始字段名，只做基本的清理
        # 对于飞书表格，我们需要保持与用户表格中字段名的一致性
        normalized_name = key.strip()
        
        field_info = {
            "field_name": normalized_name,
            "sample_value": str(value)[:100] if value else "",
            "confidence": 0.9,
            "description": field_descriptions.get(key, f"字段: {key}")
        }
        
        # 根据值类型推断字段类型
        if isinstance(value, bool):
            field_info["field_type"] = "checkbox"
        elif isinstance(value, int):
            field_info["field_type"] = "number"
        elif isinstance(value, float):
            field_info["field_type"] = "number"
        elif isinstance(value, list):
            if len(value) > 0 and isinstance(value[0], str):
                field_info["field_type"] = "multiselect"
            else:
                field_info["field_type"] = "text"
        elif isinstance(value, str):
            # 根据内容长度和关键词判断
            if len(value) > 100:
                field_info["field_type"] = "multiline_text"
            elif self._is_url(value):
                field_info["field_type"] = "url"
            elif self._is_phone(value):
                field_info["field_type"] = "phone"
            elif self._is_datetime(value):
                field_info["field_type"] = "datetime"
            else:
                field_info["field_type"] = "text"
        else:
            field_info["field_type"] = "text"
        
        return field_info
    
    def _is_url(self, value: str) -> bool:
        """
        判断是否为URL
        
        Args:
            value (str): 值
            
        Returns:
            bool: 是否为URL
        """
        url_pattern = r'^https?://'
        return bool(re.match(url_pattern, value))
    
    def _is_phone(self, value: str) -> bool:
        """
        判断是否为电话号码
        
        Args:
            value (str): 值
            
        Returns:
            bool: 是否为电话号码
        """
        phone_pattern = r'^[\d\-\+\(\)\s]{10,}$'
        return bool(re.match(phone_pattern, value))
    
    def _is_datetime(self, value: str) -> bool:
        """
        判断是否为日期时间
        
        Args:
            value (str): 值
            
        Returns:
            bool: 是否为日期时间
        """
        datetime_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{4}/\d{2}/\d{2}',
            r'\d{2}:\d{2}:\d{2}',
            r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}'
        ]
        
        for pattern in datetime_patterns:
            if re.search(pattern, value):
                return True
        return False
    
    def generate_feishu_field_template(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        根据分析结果生成飞书字段模板
        
        Args:
            analysis_result (Dict[str, Any]): 内容分析结果
            
        Returns:
            List[Dict[str, Any]]: 飞书字段模板
        """
        feishu_fields = []
        detected_fields = analysis_result.get("detected_fields", [])
        
        # 如果检测到了字段，使用检测到的字段
        if detected_fields:
            for detected_field in detected_fields:
                field_name = detected_field.get("field_name", "")
                field_type = detected_field.get("field_type", "text")
                
                # 使用原始字段名作为飞书字段名
                feishu_field = {
                    "field_name": detected_field.get("field_name", field_name),
                    "type": self.feishu_field_types.get(field_type, 1),
                    "property": {},
                    "description": detected_field.get("description", f"字段: {field_name}")
                }
                feishu_fields.append(feishu_field)
        else:
            # 如果没有检测到字段，使用基础字段模板
            base_required_fields = [
                "video_serial_number",
                "video_content_summary", 
                "video_source_path",
                "file_name"
            ]
            
            for field_key in base_required_fields:
                if field_key in self.base_fields:
                    field_config = self.base_fields[field_key]
                    feishu_field = {
                        "field_name": field_key,  # 使用英文字段名
                        "type": self.feishu_field_types[field_config["field_type"]],
                        "property": {},
                        "description": field_config["description"]
                    }
                    feishu_fields.append(feishu_field)
        
        return feishu_fields
    
    def create_field_mapping_config(self, 
                                   database_fields: List[str], 
                                   feishu_fields: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        创建数据库字段到飞书字段的映射配置
        
        Args:
            database_fields (List[str]): 数据库字段列表
            feishu_fields (List[Dict[str, Any]]): 飞书字段列表
            
        Returns:
            Dict[str, str]: 字段映射配置
        """
        mapping = {}
        
        # 预定义的映射关系
        predefined_mapping = {
            "sequence_id": "video_serial_number",
            "file_name": "file_name", 
            "file_path": "video_source_path",
            "file_size": "file_size",
            "mime_type": "file_format",
            "analysis_prompt": "analysis_prompt",
            "analysis_result": "video_content_summary",
            "created_at": "created_time",
            "coze_call_id": "coze_call_id",
            "video_serial_number": "video_serial_number",
            "video_content_summary": "video_content_summary",
            "detailed_content_description": "detailed_content_description",
            "keywords_tags": "keywords_tags",
            "main_characters_objects": "main_characters_objects",
            "video_source_path": "video_source_path"
        }
        
        # 应用预定义映射
        for db_field, feishu_field_name in predefined_mapping.items():
            if db_field in database_fields:
                mapping[db_field] = feishu_field_name
        
        return mapping
    
    def generate_mapping_template_file(self, 
                                     analysis_result: Dict[str, Any], 
                                     output_path: str) -> bool:
        """
        生成字段映射模板文件
        
        Args:
            analysis_result (Dict[str, Any]): 内容分析结果
            output_path (str): 输出文件路径
            
        Returns:
            bool: 是否生成成功
        """
        try:
            feishu_fields = self.generate_feishu_field_template(analysis_result)
            
            template_config = {
                "template_version": "1.0",
                "created_at": datetime.now().isoformat(),
                "analysis_result": analysis_result,
                "feishu_fields": feishu_fields,
                "field_mapping": self.create_field_mapping_config(
                    ["sequence_id", "file_name", "file_path", "file_size", 
                     "mime_type", "analysis_prompt", "analysis_result", 
                     "created_at", "coze_call_id"],
                    feishu_fields
                ),
                "usage_instructions": {
                    "description": "此模板用于配置飞书多维表格字段结构",
                    "steps": [
                        "1. 在飞书多维表格中按照feishu_fields创建对应字段",
                        "2. 确保字段名称和类型完全匹配",
                        "3. 使用field_mapping配置数据同步映射关系",
                        "4. 测试数据同步功能"
                    ]
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(template_config, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"字段映射模板已生成: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"生成映射模板文件失败: {str(e)}")
            return False

# 创建全局实例
field_mapper = FieldMapper()
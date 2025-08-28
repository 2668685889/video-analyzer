#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义字段映射模块
允许用户手动配置大模型返回内容与飞书字段的映射关系
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging
from pathlib import Path

class CustomFieldMapper:
    """
    自定义字段映射器
    提供可配置的字段映射功能
    """
    
    def __init__(self, config_dir: str = None):
        """
        初始化自定义字段映射器
        
        Args:
            config_dir (str): 配置文件目录，如果为None则自动查找
        """
        self.logger = logging.getLogger(__name__)
        
        # 自动查找配置文件
        if config_dir is None:
            # 首先检查项目根目录
            root_config = Path("custom_field_mapping.json")
            shuoming_config = Path("shuoming") / "custom_field_mapping.json"
            
            if root_config.exists():
                self.config_file = root_config
                self.config_dir = Path(".")
            elif shuoming_config.exists():
                self.config_file = shuoming_config
                self.config_dir = Path("shuoming")
            else:
                # 默认使用根目录
                self.config_dir = Path(".")
                self.config_file = self.config_dir / "custom_field_mapping.json"
        else:
            self.config_dir = Path(config_dir)
            self.config_dir.mkdir(exist_ok=True)
            self.config_file = self.config_dir / "custom_field_mapping.json"
        
        # 加载或创建默认配置
        self.mapping_config = self._load_or_create_default_config()
        
    def _load_or_create_default_config(self) -> Dict[str, Any]:
        """
        加载或创建默认映射配置
        
        Returns:
            Dict[str, Any]: 映射配置
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"加载映射配置失败: {str(e)}")
        
        # 创建默认配置
        default_config = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "description": "自定义字段映射配置",
            "ai_model_output_structure": {
                "description": "大模型返回内容的结构定义",
                "fields": {
                    "video_serial_number": {
                        "type": "string",
                        "description": "视频序列号",
                        "example": "202508221643173370D7A9"
                    },
                    "video_content_summary": {
                        "type": "string",
                        "description": "视频内容摘要",
                        "example": "这是一个关于...的视频"
                    },
                    "detailed_content_description": {
                        "type": "string",
                        "description": "详细内容描述",
                        "example": "视频详细描述了..."
                    },
                    "keywords_tags": {
                        "type": "string",
                        "description": "关键词标签",
                        "example": "教育,技术,演示"
                    },
                    "main_characters_objects": {
                        "type": "string",
                        "description": "主要人物对象",
                        "example": "讲师,学生"
                    },
                    "video_source_path": {
                        "type": "string",
                        "description": "视频源路径",
                        "example": "/path/to/video.mp4"
                    }
                }
            },
            "feishu_fields": {
                "description": "飞书多维表格字段定义",
                "fields": {
                    "视频序列号": {
                        "field_type": "text",
                        "required": True,
                        "description": "视频的唯一序列标识"
                    },
                    "视频内容摘要": {
                        "field_type": "text",
                        "required": True,
                        "description": "视频内容的详细摘要"
                    },
                    "详细内容描述": {
                        "field_type": "text",
                        "required": False,
                        "description": "视频的详细内容描述"
                    },
                    "关键词标签": {
                        "field_type": "text",
                        "required": False,
                        "description": "从视频中提取的关键词"
                    },
                    "主要人物对象": {
                        "field_type": "text",
                        "required": False,
                        "description": "视频中的主要人物或对象"
                    },
                    "视频源路径": {
                        "field_type": "text",
                        "required": True,
                        "description": "视频文件的源路径"
                    }
                }
            },
            "field_mapping": {
                "description": "AI模型输出字段到飞书字段的映射关系",
                "mappings": {
                    "video_serial_number": "视频序列号",
                    "video_content_summary": "视频内容摘要",
                    "detailed_content_description": "详细内容描述",
                    "keywords_tags": "关键词标签",
                    "main_characters_objects": "主要人物对象",
                    "video_source_path": "视频源路径"
                }
            },
            "data_transformation": {
                "description": "数据转换规则",
                "rules": {
                    "keywords_tags": {
                        "type": "split_and_join",
                        "separator": ",",
                        "max_length": 200
                    },
                    "video_content_summary": {
                        "type": "text_limit",
                        "max_length": 1000
                    }
                }
            }
        }
        
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """
        保存配置到文件
        
        Args:
            config (Dict[str, Any]): 配置数据
            
        Returns:
            bool: 是否保存成功
        """
        try:
            config["updated_at"] = datetime.now().isoformat()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.logger.info(f"映射配置已保存: {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"保存映射配置失败: {str(e)}")
            return False
    
    def get_ai_model_fields(self) -> Dict[str, Any]:
        """
        获取AI模型输出字段定义
        
        Returns:
            Dict[str, Any]: AI模型字段定义
        """
        return self.mapping_config.get("ai_model_output_structure", {}).get("fields", {})
    
    def get_feishu_fields(self) -> Dict[str, Any]:
        """
        获取飞书字段定义
        
        Returns:
            Dict[str, Any]: 飞书字段定义
        """
        return self.mapping_config.get("feishu_fields", {}).get("fields", {})
    
    def get_field_mappings(self) -> Dict[str, str]:
        """
        获取字段映射关系
        
        Returns:
            Dict[str, str]: 字段映射关系
        """
        return self.mapping_config.get("field_mapping", {}).get("mappings", {})
    
    def add_ai_model_field(self, field_name: str, field_config: Dict[str, Any]) -> bool:
        """
        添加AI模型输出字段
        
        Args:
            field_name (str): 字段名称
            field_config (Dict[str, Any]): 字段配置
            
        Returns:
            bool: 是否添加成功
        """
        try:
            if "ai_model_output_structure" not in self.mapping_config:
                self.mapping_config["ai_model_output_structure"] = {"fields": {}}
            
            self.mapping_config["ai_model_output_structure"]["fields"][field_name] = field_config
            return self._save_config(self.mapping_config)
        except Exception as e:
            self.logger.error(f"添加AI模型字段失败: {str(e)}")
            return False
    
    def add_feishu_field(self, field_name: str, field_config: Dict[str, Any]) -> bool:
        """
        添加飞书字段
        
        Args:
            field_name (str): 字段名称
            field_config (Dict[str, Any]): 字段配置
            
        Returns:
            bool: 是否添加成功
        """
        try:
            if "feishu_fields" not in self.mapping_config:
                self.mapping_config["feishu_fields"] = {"fields": {}}
            
            self.mapping_config["feishu_fields"]["fields"][field_name] = field_config
            return self._save_config(self.mapping_config)
        except Exception as e:
            self.logger.error(f"添加飞书字段失败: {str(e)}")
            return False
    
    def add_field_mapping(self, ai_field: str, feishu_field: str) -> bool:
        """
        添加字段映射关系
        
        Args:
            ai_field (str): AI模型字段名
            feishu_field (str): 飞书字段名
            
        Returns:
            bool: 是否添加成功
        """
        try:
            if "field_mapping" not in self.mapping_config:
                self.mapping_config["field_mapping"] = {"mappings": {}}
            
            self.mapping_config["field_mapping"]["mappings"][ai_field] = feishu_field
            return self._save_config(self.mapping_config)
        except Exception as e:
            self.logger.error(f"添加字段映射失败: {str(e)}")
            return False
    
    def remove_field_mapping(self, ai_field: str) -> bool:
        """
        删除字段映射关系
        
        Args:
            ai_field (str): AI模型字段名
            
        Returns:
            bool: 是否删除成功
        """
        try:
            mappings = self.mapping_config.get("field_mapping", {}).get("mappings", {})
            if ai_field in mappings:
                del mappings[ai_field]
                return self._save_config(self.mapping_config)
            return True
        except Exception as e:
            self.logger.error(f"删除字段映射失败: {str(e)}")
            return False
    
    def transform_ai_data_to_feishu(self, ai_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        将AI模型数据转换为飞书格式
        
        Args:
            ai_data (Dict[str, Any]): AI模型返回的数据
            
        Returns:
            Dict[str, Any]: 转换后的飞书数据
        """
        feishu_data = {}
        mappings = self.get_field_mappings()
        transformation_rules = self.mapping_config.get("data_transformation", {}).get("rules", {})
        
        for ai_field, feishu_field in mappings.items():
            if ai_field in ai_data:
                value = ai_data[ai_field]
                
                # 应用数据转换规则
                if ai_field in transformation_rules:
                    value = self._apply_transformation_rule(value, transformation_rules[ai_field])
                
                feishu_data[feishu_field] = value
        
        return feishu_data
    
    def _apply_transformation_rule(self, value: Any, rule: Dict[str, Any]) -> Any:
        """
        应用数据转换规则
        
        Args:
            value (Any): 原始值
            rule (Dict[str, Any]): 转换规则
            
        Returns:
            Any: 转换后的值
        """
        try:
            rule_type = rule.get("type")
            
            if rule_type == "split_and_join":
                if isinstance(value, str):
                    separator = rule.get("separator", ",")
                    max_length = rule.get("max_length", 200)
                    items = [item.strip() for item in value.split(separator)]
                    result = separator.join(items)
                    if len(result) > max_length:
                        result = result[:max_length] + "..."
                    return result
            
            elif rule_type == "text_limit":
                if isinstance(value, str):
                    max_length = rule.get("max_length", 1000)
                    if len(value) > max_length:
                        return value[:max_length] + "..."
                    return value
            
            return value
            
        except Exception as e:
            self.logger.error(f"应用转换规则失败: {str(e)}")
            return value
    
    def export_config(self, export_path: str) -> bool:
        """
        导出配置到指定路径
        
        Args:
            export_path (str): 导出路径
            
        Returns:
            bool: 是否导出成功
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.mapping_config, f, ensure_ascii=False, indent=2)
            self.logger.info(f"配置已导出到: {export_path}")
            return True
        except Exception as e:
            self.logger.error(f"导出配置失败: {str(e)}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """
        从指定路径导入配置
        
        Args:
            import_path (str): 导入路径
            
        Returns:
            bool: 是否导入成功
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # 验证配置格式
            if self._validate_config(imported_config):
                self.mapping_config = imported_config
                return self._save_config(self.mapping_config)
            else:
                self.logger.error("导入的配置格式不正确")
                return False
                
        except Exception as e:
            self.logger.error(f"导入配置失败: {str(e)}")
            return False
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置格式
        
        Args:
            config (Dict[str, Any]): 配置数据
            
        Returns:
            bool: 配置是否有效
        """
        required_keys = ["ai_model_output_structure", "feishu_fields", "field_mapping"]
        return all(key in config for key in required_keys)
    
    def load_config_from_dict(self, config: Dict[str, Any]) -> bool:
        """
        从字典加载配置
        
        Args:
            config (Dict[str, Any]): 配置字典
            
        Returns:
            bool: 是否加载成功
        """
        try:
            # 验证配置格式
            if self._validate_config_dict(config):
                self.mapping_config = config
                return True
            else:
                self.logger.error("配置格式不正确")
                return False
        except Exception as e:
            self.logger.error(f"从字典加载配置失败: {str(e)}")
            return False
    
    def _validate_config_dict(self, config: Dict[str, Any]) -> bool:
        """
        验证配置字典格式
        
        Args:
            config (Dict[str, Any]): 配置字典
            
        Returns:
            bool: 配置是否有效
        """
        # 检查是否包含ai_fields字段（用于测试映射）
        if "ai_fields" in config:
            return True
        
        # 检查标准配置格式
        required_keys = ["ai_model_output_structure", "feishu_fields", "field_mapping"]
        return all(key in config for key in required_keys)
    
    def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换数据（用于测试映射）
        
        Args:
            data (Dict[str, Any]): 输入数据
            
        Returns:
            Dict[str, Any]: 转换后的数据
        """
        try:
            # 如果配置中有ai_fields，使用简单的字段映射
            if "ai_fields" in self.mapping_config:
                result = {}
                ai_fields = self.mapping_config.get("ai_fields", {})
                feishu_mappings = self.mapping_config.get("feishu_mappings", {})
                
                for field_name, field_value in data.items():
                    if field_name in ai_fields and field_name in feishu_mappings:
                        # 从feishu_mappings中获取field_name
                        feishu_mapping = feishu_mappings[field_name]
                        if isinstance(feishu_mapping, dict):
                            feishu_field_name = feishu_mapping.get("field_name", field_name)
                        else:
                            feishu_field_name = str(feishu_mapping)
                        result[feishu_field_name] = field_value
                    else:
                        result[field_name] = field_value
                
                return result
            else:
                # 使用标准的转换方法
                return self.transform_ai_data_to_feishu(data)
                
        except Exception as e:
            self.logger.error(f"数据转换失败: {str(e)}")
            return data
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        获取配置摘要信息
        
        Returns:
            Dict[str, Any]: 配置摘要
        """
        ai_fields = self.get_ai_model_fields()
        feishu_fields = self.get_feishu_fields()
        mappings = self.get_field_mappings()
        
        return {
            "version": self.mapping_config.get("version", "unknown"),
            "created_at": self.mapping_config.get("created_at"),
            "updated_at": self.mapping_config.get("updated_at"),
            "ai_fields_count": len(ai_fields),
            "feishu_fields_count": len(feishu_fields),
            "mappings_count": len(mappings),
            "ai_fields": list(ai_fields.keys()),
            "feishu_fields": list(feishu_fields.keys()),
            "unmapped_ai_fields": [f for f in ai_fields.keys() if f not in mappings],
            "unmapped_feishu_fields": [f for f in feishu_fields.keys() if f not in mappings.values()]
        }

# 创建全局实例
custom_field_mapper = CustomFieldMapper()
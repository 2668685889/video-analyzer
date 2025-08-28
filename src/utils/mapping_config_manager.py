#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
映射配置管理器
用于管理自定义字段映射配置的存储、加载和验证
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class MappingConfigManager:
    """映射配置管理器类"""
    
    def __init__(self, config_dir: str = "config/mappings"):
        """
        初始化映射配置管理器
        
        Args:
            config_dir: 配置文件存储目录
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.default_config_file = self.config_dir / "default_mapping.json"
        self.custom_configs_dir = self.config_dir / "custom"
        self.custom_configs_dir.mkdir(parents=True, exist_ok=True)
    
    def create_default_config(self) -> Dict[str, Any]:
        """
        创建默认映射配置
        
        Returns:
            默认配置字典
        """
        default_config = {
            "config_name": "默认映射配置",
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "description": "系统默认的字段映射配置",
            "ai_fields": {
                "video_serial_id": {
                    "type": "text",
                    "description": "视频序列号",
                    "required": True
                },
                "video_content_summary": {
                    "type": "text",
                    "description": "视频内容摘要",
                    "required": True
                },
                "video_highlights": {
                    "type": "text",
                    "description": "视频亮点",
                    "required": False
                },
                "video_tags": {
                    "type": "text",
                    "description": "视频标签",
                    "required": False
                },
                "video_category": {
                    "type": "text",
                    "description": "视频分类",
                    "required": False
                }
            },
            "feishu_mappings": {
                "video_serial_id": {
                    "field_name": "视频序列号",
                    "field_type": "text",
                    "field_id": "fld_video_serial_id"
                },
                "video_content_summary": {
                    "field_name": "内容摘要",
                    "field_type": "text",
                    "field_id": "fld_content_summary"
                },
                "video_highlights": {
                    "field_name": "视频亮点",
                    "field_type": "text",
                    "field_id": "fld_video_highlights"
                },
                "video_tags": {
                    "field_name": "标签",
                    "field_type": "text",
                    "field_id": "fld_video_tags"
                },
                "video_category": {
                    "field_name": "分类",
                    "field_type": "text",
                    "field_id": "fld_video_category"
                }
            },
            "transformation_rules": {
                "video_tags": {
                    "type": "split",
                    "separator": ",",
                    "max_items": 10
                }
            }
        }
        return default_config
    
    def save_config(self, config: Dict[str, Any], config_name: str = None) -> str:
        """
        保存映射配置
        
        Args:
            config: 配置字典
            config_name: 配置名称，如果为None则使用配置中的名称
            
        Returns:
            保存的配置文件路径
        """
        if config_name is None:
            config_name = config.get("config_name", "unnamed_config")
        
        # 清理文件名
        safe_name = self._sanitize_filename(config_name)
        config_file = self.custom_configs_dir / f"{safe_name}.json"
        
        # 添加保存时间戳
        config["saved_at"] = datetime.now().isoformat()
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return str(config_file)
    
    def load_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """
        加载映射配置
        
        Args:
            config_name: 配置名称
            
        Returns:
            配置字典，如果不存在则返回None
        """
        safe_name = self._sanitize_filename(config_name)
        config_file = self.custom_configs_dir / f"{safe_name}.json"
        
        if not config_file.exists():
            return None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"加载配置失败: {e}")
            return None
    
    def list_configs(self) -> List[Dict[str, Any]]:
        """
        列出所有可用的配置
        
        Returns:
            配置信息列表
        """
        configs = []
        
        # 添加默认配置
        if self.default_config_file.exists():
            try:
                with open(self.default_config_file, 'r', encoding='utf-8') as f:
                    default_config = json.load(f)
                    configs.append({
                        "name": "default",
                        "display_name": default_config.get("config_name", "默认配置"),
                        "description": default_config.get("description", ""),
                        "created_at": default_config.get("created_at", ""),
                        "is_default": True
                    })
            except (json.JSONDecodeError, IOError):
                pass
        
        # 添加自定义配置
        for config_file in self.custom_configs_dir.glob("*.json"):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    configs.append({
                        "name": config_file.stem,
                        "display_name": config.get("config_name", config_file.stem),
                        "description": config.get("description", ""),
                        "created_at": config.get("created_at", ""),
                        "saved_at": config.get("saved_at", ""),
                        "is_default": False
                    })
            except (json.JSONDecodeError, IOError):
                continue
        
        return configs
    
    def delete_config(self, config_name: str) -> bool:
        """
        删除配置
        
        Args:
            config_name: 配置名称
            
        Returns:
            是否删除成功
        """
        if config_name == "default":
            return False  # 不允许删除默认配置
        
        safe_name = self._sanitize_filename(config_name)
        config_file = self.custom_configs_dir / f"{safe_name}.json"
        
        if config_file.exists():
            try:
                config_file.unlink()
                return True
            except OSError:
                return False
        return False
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        验证配置的有效性
        
        Args:
            config: 配置字典
            
        Returns:
            错误信息列表，空列表表示验证通过
        """
        errors = []
        
        # 检查必需字段
        required_fields = ["config_name", "ai_fields", "feishu_mappings"]
        for field in required_fields:
            if field not in config:
                errors.append(f"缺少必需字段: {field}")
        
        if "ai_fields" in config and "feishu_mappings" in config:
            ai_fields = set(config["ai_fields"].keys())
            feishu_fields = set(config["feishu_mappings"].keys())
            
            # 检查字段映射一致性
            if ai_fields != feishu_fields:
                missing_in_feishu = ai_fields - feishu_fields
                missing_in_ai = feishu_fields - ai_fields
                
                if missing_in_feishu:
                    errors.append(f"AI字段在飞书映射中缺失: {', '.join(missing_in_feishu)}")
                if missing_in_ai:
                    errors.append(f"飞书字段在AI字段中缺失: {', '.join(missing_in_ai)}")
        
        return errors
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，移除不安全字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的文件名
        """
        # 移除或替换不安全字符
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        
        # 限制长度
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename
    
    def initialize_default_config(self):
        """
        初始化默认配置文件
        """
        if not self.default_config_file.exists():
            default_config = self.create_default_config()
            with open(self.default_config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
    
    def export_config(self, config_name: str, export_path: str) -> bool:
        """
        导出配置到指定路径
        
        Args:
            config_name: 配置名称
            export_path: 导出路径
            
        Returns:
            是否导出成功
        """
        config = self.load_config(config_name)
        if config is None:
            return False
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except IOError:
            return False
    
    def import_config(self, import_path: str) -> Optional[str]:
        """
        从文件导入配置
        
        Args:
            import_path: 导入文件路径
            
        Returns:
            导入的配置名称，失败返回None
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 验证配置
            errors = self.validate_config(config)
            if errors:
                print(f"配置验证失败: {'; '.join(errors)}")
                return None
            
            # 保存配置
            config_name = config.get("config_name", "imported_config")
            self.save_config(config, config_name)
            return config_name
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"导入配置失败: {e}")
            return None
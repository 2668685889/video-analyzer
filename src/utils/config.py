#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
用于管理应用程序的配置信息，包括API密钥、文件大小限制等
"""

import os
from dotenv import load_dotenv
from typing import List, Dict, Any
from pathlib import Path

# 加载环境变量
load_dotenv()

class Config:
    """
    应用程序配置类
    管理所有配置参数
    """
    
    def __init__(self):
        """初始化配置"""
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', '')
        self.max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', '100'))
        self.supported_video_formats = os.getenv(
            'SUPPORTED_VIDEO_FORMATS', 
            'mp4,avi,mov,mkv,webm'
        ).split(',')
        self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        
        # 飞书相关配置
        self.feishu_app_id = os.getenv('FEISHU_APP_ID', '')
        self.feishu_app_secret = os.getenv('FEISHU_APP_SECRET', '')
        self.feishu_app_token = os.getenv('FEISHU_APP_TOKEN', '')
        self.feishu_table_id = os.getenv('FEISHU_TABLE_ID', '')
        self.feishu_enabled = os.getenv('FEISHU_ENABLED', 'false').lower() == 'true'
        self.feishu_auto_sync = os.getenv('FEISHU_AUTO_SYNC', 'true').lower() == 'true'
        
        # 飞书电子表格相关配置
        self.feishu_spreadsheet_enabled = os.getenv('FEISHU_SPREADSHEET_ENABLED', 'false').lower() == 'true'
        self.feishu_spreadsheet_token = os.getenv('FEISHU_SPREADSHEET_TOKEN', '')
        self.feishu_sheet_id = os.getenv('FEISHU_SHEET_ID', '')
        self.feishu_spreadsheet_auto_sync = os.getenv('FEISHU_SPREADSHEET_AUTO_SYNC', 'false').lower() == 'true'
        
        # 飞书云文档相关配置
        self.feishu_doc_enabled = os.getenv('FEISHU_DOC_ENABLED', 'false').lower() == 'true'
        self.feishu_doc_token = os.getenv('FEISHU_DOC_TOKEN', '')
        self.feishu_doc_auto_sync = os.getenv('FEISHU_DOC_AUTO_SYNC', 'false').lower() == 'true'
        
        # 支持的模型列表
        self.available_models = {
            'gemini-2.5-flash': 'Gemini 2.5 Flash (推荐)',
            'gemini-2.5-pro': 'Gemini 2.5 Pro (高级推理)',
            'gemini-2.0-flash': 'Gemini 2.0 Flash (新一代)',
            'gemini-1.5-flash': 'Gemini 1.5 Flash (快速)',
            'gemini-1.5-pro': 'Gemini 1.5 Pro (专业版)'
        }
    
    def is_valid(self) -> bool:
        """
        检查配置是否有效
        
        Returns:
            bool: 配置是否有效
        """
        return bool(self.gemini_api_key.strip())
    
    def is_feishu_valid(self) -> bool:
        """
        检查飞书配置是否有效
        
        Returns:
            bool: 飞书配置是否有效
        """
        return bool(
            self.feishu_app_id.strip() and 
            self.feishu_app_secret.strip() and 
            self.feishu_app_token.strip() and 
            self.feishu_table_id.strip()
        )
    
    def get_supported_formats(self) -> List[str]:
        """
        获取支持的视频格式列表
        
        Returns:
            List[str]: 支持的格式列表
        """
        return self.supported_video_formats
    
    def get_available_models(self) -> Dict[str, str]:
        """
        获取可用的模型列表
        
        Returns:
            Dict[str, str]: 模型ID到显示名称的映射
        """
        return self.available_models
    
    def get_current_model(self) -> str:
        """
        获取当前选择的模型
        
        Returns:
            str: 当前模型ID
        """
        return self.gemini_model
    
    def set_model(self, model_id: str) -> bool:
        """
        设置当前模型
        
        Args:
            model_id (str): 模型ID
            
        Returns:
            bool: 是否设置成功
        """
        if model_id in self.available_models:
            self.gemini_model = model_id
            # 这里可以添加保存到配置文件的逻辑
            return True
        return False
    
    def get_max_file_size_bytes(self) -> int:
        """
        获取最大文件大小（字节）
        
        Returns:
            int: 最大文件大小
        """
        return self.max_file_size_mb * 1024 * 1024
    
    def reload(self):
        """
        重新加载配置
        """
        load_dotenv(override=True)
        self.__init__()
    
    def get_feishu_config(self) -> Dict[str, Any]:
        """
        获取飞书配置信息
        
        Returns:
            Dict[str, Any]: 飞书配置字典
        """
        return {
            'app_id': self.feishu_app_id,
            'app_secret': self.feishu_app_secret,
            'app_token': self.feishu_app_token,
            'table_id': self.feishu_table_id,
            'enabled': self.feishu_enabled,
            'auto_sync': self.feishu_auto_sync
        }
    
    def get_feishu_spreadsheet_config(self) -> Dict[str, Any]:
        """
        获取飞书电子表格配置信息
        
        Returns:
            Dict[str, Any]: 飞书电子表格配置字典
        """
        return {
            'app_id': self.feishu_app_id,
            'app_secret': self.feishu_app_secret,
            'spreadsheet_token': self.feishu_spreadsheet_token,
            'sheet_id': self.feishu_sheet_id,
            'enabled': self.feishu_spreadsheet_enabled,
            'auto_sync': self.feishu_spreadsheet_auto_sync
        }
    
    def is_feishu_spreadsheet_valid(self) -> bool:
        """
        检查飞书电子表格配置是否有效
        
        Returns:
            bool: 配置是否有效
        """
        return (
            bool(self.feishu_app_id.strip()) and
            bool(self.feishu_app_secret.strip()) and
            bool(self.feishu_spreadsheet_token.strip()) and
            bool(self.feishu_sheet_id.strip()) and
            self.feishu_spreadsheet_enabled
        )
    
    def get_feishu_doc_config(self) -> Dict[str, Any]:
        """
        获取飞书云文档配置信息
        
        Returns:
            Dict[str, Any]: 飞书云文档配置字典
        """
        return {
            'app_id': self.feishu_app_id,
            'app_secret': self.feishu_app_secret,
            'doc_token': self.feishu_doc_token,
            'enabled': self.feishu_doc_enabled,
            'auto_sync': self.feishu_doc_auto_sync
        }
    
    def is_feishu_doc_valid(self) -> bool:
        """
        检查飞书云文档配置是否有效
        
        Returns:
            bool: 配置是否有效
        """
        return (
            bool(self.feishu_app_id.strip()) and
            bool(self.feishu_app_secret.strip()) and
            bool(self.feishu_doc_token.strip()) and
            self.feishu_doc_enabled
        )
    
    def update_feishu_config(self, config_dict: Dict[str, Any]) -> bool:
        """
        更新飞书配置
        
        Args:
            config_dict (Dict[str, Any]): 配置字典
            
        Returns:
            bool: 是否更新成功
        """
        try:
            # 更新环境变量文件
            env_file = Path(__file__).parent.parent.parent / '.env'
            
            # 读取现有配置
            env_vars = {}
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key] = value
            
            # 更新飞书相关配置
            if 'app_id' in config_dict:
                env_vars['FEISHU_APP_ID'] = config_dict['app_id']
            if 'app_secret' in config_dict:
                env_vars['FEISHU_APP_SECRET'] = config_dict['app_secret']
            if 'app_token' in config_dict:
                env_vars['FEISHU_APP_TOKEN'] = config_dict['app_token']
            if 'table_id' in config_dict:
                env_vars['FEISHU_TABLE_ID'] = config_dict['table_id']
            if 'enabled' in config_dict:
                env_vars['FEISHU_ENABLED'] = str(config_dict['enabled']).lower()
            if 'auto_sync' in config_dict:
                env_vars['FEISHU_AUTO_SYNC'] = str(config_dict['auto_sync']).lower()
            
            # 更新飞书电子表格配置
            if 'spreadsheet_enabled' in config_dict:
                env_vars['FEISHU_SPREADSHEET_ENABLED'] = str(config_dict['spreadsheet_enabled']).lower()
            if 'spreadsheet_token' in config_dict:
                env_vars['FEISHU_SPREADSHEET_TOKEN'] = config_dict['spreadsheet_token']
            if 'sheet_id' in config_dict:
                env_vars['FEISHU_SHEET_ID'] = config_dict['sheet_id']
            if 'spreadsheet_auto_sync' in config_dict:
                env_vars['FEISHU_SPREADSHEET_AUTO_SYNC'] = str(config_dict['spreadsheet_auto_sync']).lower()
            
            # 更新飞书云文档配置
            if 'doc_enabled' in config_dict:
                env_vars['FEISHU_DOC_ENABLED'] = str(config_dict['doc_enabled']).lower()
            if 'doc_token' in config_dict:
                env_vars['FEISHU_DOC_TOKEN'] = config_dict['doc_token']
            if 'doc_auto_sync' in config_dict:
                env_vars['FEISHU_DOC_AUTO_SYNC'] = str(config_dict['doc_auto_sync']).lower()
            
            # 写入配置文件
            with open(env_file, 'w', encoding='utf-8') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            
            # 重新加载配置
            self.reload()
            return True
            
        except Exception as e:
            print(f"更新飞书配置失败: {str(e)}")
            return False

# 创建全局配置实例
config = Config()
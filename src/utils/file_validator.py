#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件验证模块
用于验证上传文件的格式、大小等属性
"""

import os
import mimetypes
from typing import Tuple, Optional
from .config import config

class FileValidator:
    """
    文件验证器类
    负责验证文件的有效性
    """
    
    @staticmethod
    def validate_file(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        验证文件是否符合要求
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return False, "文件不存在"
        
        # 检查是否为文件
        if not os.path.isfile(file_path):
            return False, "路径不是一个文件"
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        max_size = config.get_max_file_size_bytes()
        if file_size > max_size:
            return False, f"文件大小超过限制 ({config.max_file_size_mb}MB)"
        
        # 检查文件格式
        is_valid_format, format_error = FileValidator._validate_format(file_path)
        if not is_valid_format:
            return False, format_error
        
        return True, None
    
    @staticmethod
    def _validate_format(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        验证文件格式
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        # 获取文件扩展名
        _, ext = os.path.splitext(file_path)
        ext = ext.lower().lstrip('.')
        
        # 检查扩展名是否在支持列表中
        supported_formats = config.get_supported_formats()
        if ext not in supported_formats:
            return False, f"不支持的文件格式: {ext}。支持的格式: {', '.join(supported_formats)}"
        
        # 验证MIME类型
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and not mime_type.startswith('video/'):
            return False, f"文件类型不是视频文件: {mime_type}"
        
        return True, None
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """
        获取文件信息
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            dict: 文件信息字典
        """
        if not os.path.exists(file_path):
            return {}
        
        file_size = os.path.getsize(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        _, ext = os.path.splitext(file_path)
        
        return {
            'name': os.path.basename(file_path),
            'size': file_size,
            'size_mb': round(file_size / (1024 * 1024), 2),
            'extension': ext.lower().lstrip('.'),
            'mime_type': mime_type,
            'path': file_path
        }
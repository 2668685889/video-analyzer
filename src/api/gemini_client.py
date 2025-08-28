#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini API客户端模块
用于与Google Gemini API进行交互，支持视频文件上传和内容分析
"""

import os
import time
from typing import Optional, Dict, Any
from google import genai
from ..utils.config import config
from ..utils.aliyun_oss_uploader import create_oss_uploader_from_config

class GeminiClient:
    """
    Gemini API客户端类
    负责与Gemini API的所有交互
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        初始化Gemini客户端
        
        Args:
            model_name (str, optional): 指定使用的模型名称，如果不指定则使用配置中的默认模型
        """
        if not config.is_valid():
            raise ValueError("Gemini API密钥未配置，请检查.env文件")
        
        # 初始化客户端
        self.client = genai.Client(api_key=config.gemini_api_key)
        self.model_name = model_name or config.get_current_model()
    
    def set_model(self, model_name: str) -> bool:
        """
        设置使用的模型
        
        Args:
            model_name (str): 模型名称
            
        Returns:
            bool: 设置是否成功
        """
        available_models = config.get_available_models()
        if model_name in available_models:
            self.model_name = model_name
            return True
        return False
    
    def get_current_model(self) -> str:
        """
        获取当前使用的模型
        
        Returns:
            str: 当前模型名称
        """
        return self.model_name
    
    def upload_file(self, file_path: str, display_name: Optional[str] = None) -> Dict[str, Any]:
        """
        上传文件到Gemini API
        
        Args:
            file_path (str): 文件路径
            display_name (str, optional): 显示名称
            
        Returns:
            Dict[str, Any]: 上传结果信息
            
        Raises:
            Exception: 上传失败时抛出异常
        """
        max_retries = 3
        base_delay = 2  # 基础延迟时间（秒）
        
        for attempt in range(max_retries):
            try:
                if display_name is None:
                    display_name = os.path.basename(file_path)
                
                # 上传文件
                uploaded_file = self.client.files.upload(
                    file=file_path,
                    config={
                        'display_name': display_name
                    }
                )
                
                # 等待文件处理完成
                self._wait_for_file_processing(uploaded_file.name)
                
                return {
                    'success': True,
                    'file_name': uploaded_file.name,
                    'file_uri': uploaded_file.uri,
                    'display_name': uploaded_file.display_name,
                    'mime_type': uploaded_file.mime_type,
                    'size_bytes': uploaded_file.size_bytes
                }
                
            except Exception as e:
                error_str = str(e)
                
                # 检查是否是503错误或服务器过载错误
                if ('503' in error_str or 
                    'overloaded' in error_str.lower() or 
                    'unavailable' in error_str.lower() or
                    'rate limit' in error_str.lower()):
                    
                    if attempt < max_retries - 1:  # 不是最后一次尝试
                        # 指数退避：每次重试延迟时间翻倍
                        delay = base_delay * (2 ** attempt)
                        print(f"上传服务器过载，{delay}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        return {
                            'success': False,
                            'error': f"上传服务器持续过载，已重试{max_retries}次。请稍后再试。原始错误: {error_str}"
                        }
                else:
                    # 其他类型的错误，直接返回
                    return {
                        'success': False,
                        'error': error_str
                    }
        
        # 理论上不会到达这里
        return {
            'success': False,
            'error': '未知错误'
        }
    
    def _wait_for_file_processing(self, file_name: str, max_wait_time: int = 300) -> None:
        """
        等待文件处理完成
        
        Args:
            file_name (str): 文件名
            max_wait_time (int): 最大等待时间（秒）
            
        Raises:
            TimeoutError: 处理超时
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                file_info = self.client.files.get(name=file_name)
                if file_info.state == 'ACTIVE':
                    return
                elif file_info.state == 'FAILED':
                    raise Exception(f"文件处理失败: {file_info.error}")
                
                time.sleep(2)  # 等待2秒后重试
                
            except Exception as e:
                if "not found" in str(e).lower():
                    time.sleep(2)
                    continue
                raise e
        
        raise TimeoutError("文件处理超时")
    
    def analyze_video(self, file_uri: str, prompt: str) -> Dict[str, Any]:
        """
        分析视频内容
        
        Args:
            file_uri (str): 文件URI
            prompt (str): 分析提示
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        max_retries = 3
        base_delay = 2  # 基础延迟时间（秒）
        
        for attempt in range(max_retries):
            try:
                # 构建请求内容
                contents = [
                    {
                        'role': 'user',
                        'parts': [
                            {
                                'file_data': {
                                    'file_uri': file_uri,
                                    'mime_type': 'video/*'
                                }
                            },
                            {
                                'text': prompt
                            }
                        ]
                    }
                ]
                
                # 生成内容
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=contents
                )
                
                return {
                    'success': True,
                    'result': response.text,
                    'usage': getattr(response, 'usage_metadata', None)
                }
                
            except Exception as e:
                error_str = str(e)
                
                # 检查是否是503错误或服务器过载错误
                if ('503' in error_str or 
                    'overloaded' in error_str.lower() or 
                    'unavailable' in error_str.lower() or
                    'rate limit' in error_str.lower()):
                    
                    if attempt < max_retries - 1:  # 不是最后一次尝试
                        # 指数退避：每次重试延迟时间翻倍
                        delay = base_delay * (2 ** attempt)
                        print(f"服务器过载，{delay}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        return {
                            'success': False,
                            'error': f"服务器持续过载，已重试{max_retries}次。请稍后再试。原始错误: {error_str}"
                        }
                else:
                    # 其他类型的错误，直接返回
                    return {
                        'success': False,
                        'error': error_str
                    }
        
        # 理论上不会到达这里
        return {
            'success': False,
            'error': '未知错误'
        }
    
    def analyze_video_with_file(self, file_path: str, prompt: str) -> Dict[str, Any]:
        """
        上传并分析视频文件，同时上传到OSS
        
        Args:
            file_path (str): 视频文件路径
            prompt (str): 分析提示
            
        Returns:
            Dict[str, Any]: 分析结果，包含OSS链接信息
        """
        # 上传文件到Gemini
        upload_result = self.upload_file(file_path)
        
        if not upload_result['success']:
            return upload_result
        
        # 同时上传到OSS
        oss_result = self._upload_to_oss(file_path)
        
        # 分析视频
        analysis_result = self.analyze_video(
            upload_result['file_uri'], 
            prompt
        )
        
        # 合并结果
        if analysis_result['success']:
            analysis_result['file_info'] = {
                'name': upload_result['file_name'],
                'display_name': upload_result['display_name'],
                'size_bytes': upload_result['size_bytes']
            }
            
            # 添加OSS信息
            if oss_result['success']:
                analysis_result['oss_info'] = {
                    'url': oss_result['url'],
                    'file_name': oss_result['file_name']
                }
            else:
                analysis_result['oss_info'] = {
                    'error': oss_result.get('error', 'OSS上传失败')
                }
        
        return analysis_result
    
    def _upload_to_oss(self, file_path: str) -> Dict[str, Any]:
        """
        上传文件到OSS
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            Dict[str, Any]: 上传结果
        """
        try:
            # 创建OSS上传器，使用配置文件
            config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'oss_config.json')
            uploader = create_oss_uploader_from_config(config_file)
            if not uploader:
                return {
                    'success': False,
                    'error': 'OSS配置未找到或无效'
                }
            
            # 生成OSS存储路径（不包含文件名）
            import datetime
            file_name = os.path.basename(file_path)
            name, ext = os.path.splitext(file_name)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # 只设置目录路径，让uploader自己处理文件名
            custom_path = "videos"
            
            # 上传文件
            result = uploader.upload_file(
                file_path=file_path,
                custom_path=custom_path,
                use_timestamp=True  # 让uploader添加时间戳
            )
            
            if result['success']:
                return {
                    'success': True,
                    'url': result['file_url'],
                    'file_name': result.get('object_key', 'unknown')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', '上传失败')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'OSS上传异常: {str(e)}'
            }
    
    def list_files(self) -> Dict[str, Any]:
        """
        列出已上传的文件
        
        Returns:
            Dict[str, Any]: 文件列表
        """
        try:
            files = list(self.client.files.list())
            
            file_list = []
            for file in files:
                file_list.append({
                    'name': file.name,
                    'display_name': file.display_name,
                    'uri': file.uri,
                    'mime_type': file.mime_type,
                    'size_bytes': file.size_bytes,
                    'create_time': file.create_time,
                    'state': file.state
                })
            
            return {
                'success': True,
                'files': file_list
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_file(self, file_name: str) -> Dict[str, Any]:
        """
        删除已上传的文件
        
        Args:
            file_name (str): 文件名
            
        Returns:
            Dict[str, Any]: 删除结果
        """
        try:
            self.client.files.delete(file_name)
            return {
                'success': True,
                'message': f"文件 {file_name} 已删除"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
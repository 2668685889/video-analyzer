#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件处理模块
负责文件上传、处理和管理的业务逻辑
"""

import os
import shutil
import time
from typing import Dict, Any, Optional, List, Callable
from .file_validator import FileValidator
from ..api.gemini_client import GeminiClient

class FileHandler:
    """
    文件处理器类
    负责文件的上传、验证和处理
    """
    
    def __init__(self):
        """初始化文件处理器"""
        self.validator = FileValidator()
        self.gemini_client = None
        
    def _get_gemini_client(self) -> GeminiClient:
        """
        获取Gemini客户端实例（懒加载）
        
        Returns:
            GeminiClient: Gemini客户端实例
        """
        if self.gemini_client is None:
            self.gemini_client = GeminiClient()
        return self.gemini_client
    
    def validate_and_prepare_file(self, file_path: str) -> Dict[str, Any]:
        """
        验证并准备文件
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            Dict[str, Any]: 验证结果和文件信息
        """
        # 验证文件
        is_valid, error_message = self.validator.validate_file(file_path)
        
        if not is_valid:
            return {
                'success': False,
                'error': error_message
            }
        
        # 获取文件信息
        file_info = self.validator.get_file_info(file_path)
        
        return {
            'success': True,
            'file_info': file_info
        }
    
    def upload_file_to_gemini(self, file_path: str, display_name: Optional[str] = None) -> Dict[str, Any]:
        """
        上传文件到Gemini API
        
        Args:
            file_path (str): 文件路径
            display_name (str, optional): 显示名称
            
        Returns:
            Dict[str, Any]: 上传结果
        """
        # 首先验证文件
        validation_result = self.validate_and_prepare_file(file_path)
        if not validation_result['success']:
            return validation_result
        
        try:
            # 获取Gemini客户端并上传文件
            client = self._get_gemini_client()
            upload_result = client.upload_file(file_path, display_name)
            
            if upload_result['success']:
                # 添加本地文件信息
                upload_result['local_file_info'] = validation_result['file_info']
            
            return upload_result
            
        except Exception as e:
            return {
                'success': False,
                'error': f"上传文件时发生错误: {str(e)}"
            }
    
    def process_video_analysis(self, file_path: str, prompt: str, display_name: Optional[str] = None) -> Dict[str, Any]:
        """
        处理视频分析请求
        
        Args:
            file_path (str): 视频文件路径
            prompt (str): 分析提示
            display_name (str, optional): 显示名称
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        # 验证文件
        validation_result = self.validate_and_prepare_file(file_path)
        if not validation_result['success']:
            return validation_result
        
        try:
            # 获取Gemini客户端并分析视频
            client = self._get_gemini_client()
            analysis_result = client.analyze_video_with_file(file_path, prompt)
            
            if analysis_result['success']:
                # 添加本地文件信息
                analysis_result['local_file_info'] = validation_result['file_info']
            
            return analysis_result
            
        except Exception as e:
            return {                'success': False,                'error': f"分析视频时发生错误: {str(e)}"            }    
    def validate_multiple_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        批量验证多个文件
        
        Args:
            file_paths (List[str]): 文件路径列表
            
        Returns:
            Dict[str, Any]: 批量验证结果
        """
        results = []
        valid_files = []
        invalid_files = []
        
        for file_path in file_paths:
            validation_result = self.validate_and_prepare_file(file_path)
            results.append({
                'file_path': file_path,
                'validation_result': validation_result
            })
            
            if validation_result['success']:
                valid_files.append(file_path)
            else:
                invalid_files.append({
                    'file_path': file_path,
                    'error': validation_result['error']
                })
        
        return {
            'success': len(invalid_files) == 0,
            'total_files': len(file_paths),
            'valid_files': valid_files,
            'invalid_files': invalid_files,
            'detailed_results': results
        }
    
    def process_batch_video_analysis(self, file_paths: List[str], prompt: str, 
                                   progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        批量处理视频分析请求
        
        Args:
            file_paths (List[str]): 视频文件路径列表
            prompt (str): 分析提示
            progress_callback (Callable, optional): 进度回调函数
            
        Returns:
            Dict[str, Any]: 批量分析结果
        """
        # 首先批量验证文件
        validation_result = self.validate_multiple_files(file_paths)
        
        if not validation_result['success']:
            return {
                'success': False,
                'error': f"文件验证失败，{len(validation_result['invalid_files'])} 个文件无效",
                'validation_result': validation_result
            }
        
        # 处理每个文件
        results = []
        successful_analyses = 0
        failed_analyses = 0
        
        for index, file_path in enumerate(file_paths):
            try:
                # 调用进度回调（开始处理）
                if progress_callback:
                    progress_callback({
                        'current_file': index + 1,
                        'total_files': len(file_paths),
                        'file_path': file_path,
                        'status': 'processing'
                    })
                
                # 分析单个文件
                analysis_result = self.process_video_analysis(file_path, prompt)
                
                results.append({
                    'file_path': file_path,
                    'file_name': os.path.basename(file_path),
                    'analysis_result': analysis_result
                })
                
                if analysis_result['success']:
                    successful_analyses += 1
                else:
                    failed_analyses += 1
                
                # 调用进度回调（完成）
                if progress_callback:
                    progress_callback({
                        'current_file': index + 1,
                        'total_files': len(file_paths),
                        'file_path': file_path,
                        'status': 'completed' if analysis_result['success'] else 'failed',
                        'result': analysis_result
                    })
                
                # 如果不是最后一个文件，等待5秒再处理下一个
                if index < len(file_paths) - 1:
                    if progress_callback:
                        progress_callback({
                            'current_file': index + 1,
                            'total_files': len(file_paths),
                            'file_path': file_path,
                            'status': 'waiting',
                            'message': '等待5秒后处理下一个文件...'
                        })
                    time.sleep(5)  # 等待5秒
                    
            except Exception as e:
                error_result = {
                    'success': False,
                    'error': f"处理文件时发生错误: {str(e)}"
                }
                
                results.append({
                    'file_path': file_path,
                    'file_name': os.path.basename(file_path),
                    'analysis_result': error_result
                })
                
                failed_analyses += 1
                
                # 调用进度回调（失败）
                if progress_callback:
                    progress_callback({
                        'current_file': index + 1,
                        'total_files': len(file_paths),
                        'file_path': file_path,
                        'status': 'failed',
                        'result': error_result
                    })
                
                # 即使失败也要等待5秒再处理下一个文件（如果不是最后一个）
                if index < len(file_paths) - 1:
                    if progress_callback:
                        progress_callback({
                            'current_file': index + 1,
                            'total_files': len(file_paths),
                            'file_path': file_path,
                            'status': 'waiting',
                            'message': '等待5秒后处理下一个文件...'
                        })
                    time.sleep(5)  # 等待5秒
        
        return {
            'success': failed_analyses == 0,
            'total_files': len(file_paths),
            'successful_analyses': successful_analyses,
            'failed_analyses': failed_analyses,
            'results': results
        }
    
    def copy_file_to_temp(self, source_path: str, temp_dir: str = "/tmp") -> Dict[str, Any]:
        """
        将文件复制到临时目录
        
        Args:
            source_path (str): 源文件路径
            temp_dir (str): 临时目录路径
            
        Returns:
            Dict[str, Any]: 复制结果
        """
        try:
            # 确保临时目录存在
            os.makedirs(temp_dir, exist_ok=True)
            
            # 生成临时文件路径
            filename = os.path.basename(source_path)
            temp_path = os.path.join(temp_dir, filename)
            
            # 如果文件已存在，添加序号
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(temp_path):
                new_filename = f"{base_name}_{counter}{ext}"
                temp_path = os.path.join(temp_dir, new_filename)
                counter += 1
            
            # 复制文件
            shutil.copy2(source_path, temp_path)
            
            return {
                'success': True,
                'temp_path': temp_path,
                'original_path': source_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"复制文件时发生错误: {str(e)}"
            }
    
    def cleanup_temp_file(self, temp_path: str) -> Dict[str, Any]:
        """
        清理临时文件
        
        Args:
            temp_path (str): 临时文件路径
            
        Returns:
            Dict[str, Any]: 清理结果
        """
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                return {
                    'success': True,
                    'message': f"临时文件已删除: {temp_path}"
                }
            else:
                return {
                    'success': True,
                    'message': "临时文件不存在，无需删除"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"删除临时文件时发生错误: {str(e)}"
            }
    
    def get_supported_formats_info(self) -> Dict[str, Any]:
        """
        获取支持的文件格式信息
        
        Returns:
            Dict[str, Any]: 格式信息
        """
        from .config import config
        
        return {
            'supported_formats': config.get_supported_formats(),
            'max_file_size_mb': config.max_file_size_mb,
            'max_file_size_bytes': config.get_max_file_size_bytes()
        }
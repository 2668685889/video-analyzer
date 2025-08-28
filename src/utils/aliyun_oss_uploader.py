#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云对象存储（OSS）文件上传工具

功能：
- 支持单文件和批量文件上传到阿里云OSS
- 支持进度回调和错误处理
- 支持自定义存储路径和文件名
- 支持多种文件类型验证

作者：AI Assistant
创建时间：2025-01-25
"""

import os
import hashlib
import mimetypes
import base64
from typing import Optional, Callable, List, Dict, Any
from datetime import datetime
import logging

try:
    import oss2
except ImportError:
    oss2 = None
    print("警告：未安装阿里云OSS SDK，请运行：pip install oss2")


class AliyunOSSUploader:
    """阿里云OSS文件上传器"""
    
    def __init__(self, access_key_id: str, access_key_secret: str, 
                 endpoint: str, bucket_name: str):
        """
        初始化OSS上传器
        
        Args:
            access_key_id: 阿里云AccessKey ID
            access_key_secret: 阿里云AccessKey Secret
            endpoint: OSS服务端点（如：oss-cn-hangzhou.aliyuncs.com）
            bucket_name: OSS存储桶名称
        """
        if not oss2:
            raise ImportError("请先安装阿里云OSS SDK：pip install oss2")
            
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        
        # 初始化OSS客户端
        try:
            auth = oss2.Auth(access_key_id, access_key_secret)
            self.bucket = oss2.Bucket(auth, endpoint, bucket_name)
            
        except Exception as e:
            raise ConnectionError(f"OSS客户端初始化失败：{str(e)}")
    
    def _test_connection(self) -> bool:
        """
        测试OSS连接是否正常
        
        Returns:
            bool: 连接是否成功
        """
        try:
            # 尝试获取存储桶信息
            bucket_info = self.bucket.get_bucket_info()
            logging.info(f"OSS连接成功，存储桶：{bucket_info.name}")
            return True
        except Exception as e:
            logging.error(f"OSS连接测试失败：{str(e)}")
            raise
    
    def _generate_object_key(self, file_path: str, custom_path: Optional[str] = None,
                           use_timestamp: bool = True) -> str:
        """
        生成OSS对象键（文件路径）
        
        Args:
            file_path: 本地文件路径
            custom_path: 自定义存储路径
            use_timestamp: 是否在文件名中添加时间戳
            
        Returns:
            str: OSS对象键
        """
        filename = os.path.basename(file_path)
        
        if use_timestamp:
            # 添加时间戳避免文件名冲突
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}{ext}"
        
        if custom_path:
            # 确保路径格式正确
            custom_path = custom_path.strip('/')
            return f"{custom_path}/{filename}"
        else:
            # 默认按日期分组
            date_path = datetime.now().strftime("%Y/%m/%d")
            return f"uploads/{date_path}/{filename}"
    
    def _calculate_file_md5(self, file_path: str) -> str:
        """
        计算文件MD5值（Base64编码）
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: Base64编码的MD5值
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        # OSS需要Base64编码的MD5值
        return base64.b64encode(hash_md5.digest()).decode('utf-8')
    
    def _get_content_type(self, file_path: str) -> str:
        """
        获取文件MIME类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: MIME类型
        """
        content_type, _ = mimetypes.guess_type(file_path)
        return content_type or 'application/octet-stream'
    
    def upload_file(self, file_path: str, 
                   custom_path: Optional[str] = None,
                   use_timestamp: bool = True,
                   progress_callback: Optional[Callable[[int, int], None]] = None,
                   overwrite: bool = False,
                   permission: str = 'private') -> Dict[str, Any]:
        """
        上传单个文件到OSS
        
        Args:
            file_path: 本地文件路径
            custom_path: 自定义存储路径
            use_timestamp: 是否在文件名中添加时间戳
            progress_callback: 进度回调函数 (已上传字节数, 总字节数)
            overwrite: 是否覆盖已存在的文件
            permission: 文件权限 ('private', 'public-read', 'public-read-write')
            
        Returns:
            Dict[str, Any]: 上传结果信息
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在：{file_path}")
        
        if not os.path.isfile(file_path):
            raise ValueError(f"路径不是文件：{file_path}")
        
        # 生成对象键
        object_key = self._generate_object_key(file_path, custom_path, use_timestamp)
        
        # 检查文件是否已存在
        if not overwrite and self.bucket.object_exists(object_key):
            raise FileExistsError(f"文件已存在：{object_key}")
        
        try:
            # 获取文件信息
            file_size = os.path.getsize(file_path)
            content_type = self._get_content_type(file_path)
            file_md5 = self._calculate_file_md5(file_path)
            
            # 设置上传参数
            headers = {
                'Content-Type': content_type,
                'Content-MD5': file_md5
            }
            
            # 进度回调包装器
            def progress_wrapper(bytes_consumed, total_bytes):
                if progress_callback:
                    progress_callback(bytes_consumed, total_bytes)
            
            # 执行上传
            if file_size > 100 * 1024 * 1024:  # 大于100MB使用分片上传
                result = self._multipart_upload(file_path, object_key, headers, progress_wrapper)
            else:
                result = self.bucket.put_object_from_file(
                    object_key, file_path, 
                    headers=headers,
                    progress_callback=progress_wrapper
                )
            
            # 设置文件权限
            if permission and permission != 'private':
                try:
                    # 将权限映射到OSS ACL
                    acl_mapping = {
                        'public-read': oss2.OBJECT_ACL_PUBLIC_READ,
                        'public-read-write': oss2.OBJECT_ACL_PUBLIC_READ_WRITE,
                        'private': oss2.OBJECT_ACL_PRIVATE
                    }
                    if permission in acl_mapping:
                        self.bucket.put_object_acl(object_key, acl_mapping[permission])
                except Exception as acl_error:
                    logging.warning(f"设置文件权限失败：{str(acl_error)}")
            
            # 生成访问URL
            file_url = f"https://{self.bucket_name}.{self.endpoint}/{object_key}"
            
            upload_info = {
                'success': True,
                'object_key': object_key,
                'file_url': file_url,
                'file_size': file_size,
                'content_type': content_type,
                'md5': file_md5,
                'etag': result.etag,
                'upload_time': datetime.now().isoformat()
            }
            
            logging.info(f"文件上传成功：{file_path} -> {object_key}")
            return upload_info
            
        except Exception as e:
            error_info = {
                'success': False,
                'error': str(e),
                'file_path': file_path,
                'object_key': object_key
            }
            logging.error(f"文件上传失败：{file_path} - {str(e)}")
            return error_info
    
    def _multipart_upload(self, file_path: str, object_key: str, 
                         headers: Dict[str, str],
                         progress_callback: Optional[Callable[[int, int], None]] = None):
        """
        分片上传大文件
        
        Args:
            file_path: 本地文件路径
            object_key: OSS对象键
            headers: 请求头
            progress_callback: 进度回调函数
            
        Returns:
            上传结果
        """
        # 初始化分片上传
        upload_id = self.bucket.init_multipart_upload(object_key, headers=headers).upload_id
        
        parts = []
        part_size = 10 * 1024 * 1024  # 10MB per part
        file_size = os.path.getsize(file_path)
        uploaded_bytes = 0
        
        try:
            with open(file_path, 'rb') as f:
                part_number = 1
                while True:
                    data = f.read(part_size)
                    if not data:
                        break
                    
                    # 上传分片
                    result = self.bucket.upload_part(
                        object_key, upload_id, part_number, data
                    )
                    parts.append(oss2.models.PartInfo(part_number, result.etag))
                    
                    # 更新进度
                    uploaded_bytes += len(data)
                    if progress_callback:
                        progress_callback(uploaded_bytes, file_size)
                    
                    part_number += 1
            
            # 完成分片上传
            result = self.bucket.complete_multipart_upload(object_key, upload_id, parts)
            return result
            
        except Exception as e:
            # 取消分片上传
            self.bucket.abort_multipart_upload(object_key, upload_id)
            raise e
    
    def upload_files(self, file_paths: List[str],
                    custom_path: Optional[str] = None,
                    use_timestamp: bool = True,
                    progress_callback: Optional[Callable[[int, int, str], None]] = None,
                    overwrite: bool = False) -> List[Dict[str, Any]]:
        """
        批量上传文件到OSS
        
        Args:
            file_paths: 文件路径列表
            custom_path: 自定义存储路径
            use_timestamp: 是否在文件名中添加时间戳
            progress_callback: 进度回调函数 (当前文件索引, 总文件数, 当前文件名)
            overwrite: 是否覆盖已存在的文件
            
        Returns:
            List[Dict[str, Any]]: 上传结果列表
        """
        results = []
        total_files = len(file_paths)
        
        for i, file_path in enumerate(file_paths):
            if progress_callback:
                progress_callback(i + 1, total_files, os.path.basename(file_path))
            
            result = self.upload_file(
                file_path, custom_path, use_timestamp, 
                overwrite=overwrite
            )
            results.append(result)
        
        return results
    
    def delete_file(self, object_key: str) -> bool:
        """
        删除OSS中的文件
        
        Args:
            object_key: OSS对象键
            
        Returns:
            bool: 删除是否成功
        """
        try:
            self.bucket.delete_object(object_key)
            logging.info(f"文件删除成功：{object_key}")
            return True
        except Exception as e:
            logging.error(f"文件删除失败：{object_key} - {str(e)}")
            return False
    
    def list_files(self, prefix: str = '', max_keys: int = 100) -> List[Dict[str, Any]]:
        """
        列出OSS中的文件
        
        Args:
            prefix: 文件前缀过滤
            max_keys: 最大返回数量
            
        Returns:
            List[Dict[str, Any]]: 文件信息列表
        """
        try:
            files = []
            for obj in oss2.ObjectIterator(self.bucket, prefix=prefix, max_keys=max_keys):
                file_info = {
                    'key': obj.key,
                    'size': obj.size,
                    'last_modified': obj.last_modified,
                    'etag': obj.etag,
                    'url': f"https://{self.bucket_name}.{self.endpoint}/{obj.key}"
                }
                files.append(file_info)
            return files
        except Exception as e:
            logging.error(f"列出文件失败：{str(e)}")
            return []
    
    def get_file_url(self, object_key: str, expires: int = 3600) -> str:
        """
        生成文件的临时访问URL
        
        Args:
            object_key: OSS对象键
            expires: 过期时间（秒）
            
        Returns:
            str: 临时访问URL
        """
        try:
            url = self.bucket.sign_url('GET', object_key, expires)
            return url
        except Exception as e:
            logging.error(f"生成URL失败：{object_key} - {str(e)}")
            return ""


def create_oss_uploader_from_config(config_file: str = None) -> AliyunOSSUploader:
    """
    从配置文件创建OSS上传器
    
    Args:
        config_file: 配置文件路径，默认从环境变量读取
        
    Returns:
        AliyunOSSUploader: OSS上传器实例
    """
    if config_file:
        # 从配置文件读取
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return AliyunOSSUploader(
            access_key_id=config['access_key_id'],
            access_key_secret=config['access_key_secret'],
            endpoint=config['endpoint'],
            bucket_name=config['bucket_name']
        )
    else:
        # 从环境变量读取
        access_key_id = os.getenv('ALIYUN_ACCESS_KEY_ID')
        access_key_secret = os.getenv('ALIYUN_ACCESS_KEY_SECRET')
        endpoint = os.getenv('ALIYUN_OSS_ENDPOINT')
        bucket_name = os.getenv('ALIYUN_OSS_BUCKET')
        
        if not all([access_key_id, access_key_secret, endpoint, bucket_name]):
            raise ValueError("请设置阿里云OSS相关环境变量")
        
        return AliyunOSSUploader(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            endpoint=endpoint,
            bucket_name=bucket_name
        )


if __name__ == "__main__":
    # 测试代码
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python aliyun_oss_uploader.py <文件路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        # 创建上传器
        uploader = create_oss_uploader_from_config()
        
        # 上传文件
        def progress_callback(bytes_consumed, total_bytes):
            percent = (bytes_consumed / total_bytes) * 100
            print(f"\r上传进度：{percent:.1f}%", end="")
        
        result = uploader.upload_file(file_path, progress_callback=progress_callback)
        print(f"\n上传结果：{result}")
        
    except Exception as e:
        print(f"上传失败：{str(e)}")
        sys.exit(1)
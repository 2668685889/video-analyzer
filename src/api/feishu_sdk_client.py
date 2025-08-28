#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书官方SDK客户端
使用飞书官方Python SDK实现云文档操作
"""

import json
import logging
from typing import Optional, Dict, Any

import lark_oapi as lark
from lark_oapi.api.docx.v1 import *


class FeishuSDKClient:
    """
    飞书官方SDK客户端
    使用飞书官方Python SDK实现云文档操作
    """
    
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化飞书SDK客户端
        
        Args:
            app_id (str): 飞书应用ID
            app_secret (str): 飞书应用密钥
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.logger = logging.getLogger(__name__)
        
        # 创建飞书客户端
        self.client = lark.Client.builder() \
            .app_id(app_id) \
            .app_secret(app_secret) \
            .log_level(lark.LogLevel.INFO) \
            .build()
    
    def test_doc_connection(self, doc_token: str) -> bool:
        """
        测试云文档连接
        
        Args:
            doc_token (str): 云文档token
            
        Returns:
            bool: 连接是否成功
        """
        try:
            doc_info = self.get_doc_info(doc_token)
            return doc_info is not None
        except Exception as e:
            self.logger.error(f"测试云文档连接失败: {str(e)}")
            return False
    
    def get_doc_info(self, doc_token: str) -> Optional[Dict[str, Any]]:
        """
        获取云文档信息
        
        Args:
            doc_token (str): 云文档token
            
        Returns:
            Optional[Dict[str, Any]]: 云文档信息
        """
        try:
            # 构造请求对象
            request = GetDocumentRequest.builder() \
                .document_id(doc_token) \
                .build()
            
            # 发起请求
            response = self.client.docx.v1.document.get(request)
            
            # 处理失败返回
            if not response.success():
                self.logger.error(
                    f"获取文档信息失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
                return None
            
            # 返回文档信息
            return response.data.__dict__ if response.data else None
            
        except Exception as e:
            self.logger.error(f"获取云文档信息异常: {str(e)}")
            return None
    
    def get_doc_blocks(self, doc_token: str, page_size: int = 500) -> Optional[Dict[str, Any]]:
        """
        获取文档块信息
        
        Args:
            doc_token (str): 云文档token
            page_size (int): 页面大小
            
        Returns:
            Optional[Dict[str, Any]]: 文档块信息
        """
        try:
            # 构造请求对象
            request = ListDocumentBlockRequest.builder() \
                .document_id(doc_token) \
                .page_size(page_size) \
                .document_revision_id(-1) \
                .build()
            
            # 发起请求
            response = self.client.docx.v1.document_block.list(request)
            
            # 处理失败返回
            if not response.success():
                self.logger.error(
                    f"获取文档块失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
                return None
            
            # 返回块信息
            return response.data.__dict__ if response.data else None
            
        except Exception as e:
            self.logger.error(f"获取文档块异常: {str(e)}")
            return None
    
    def append_doc_content(self, doc_token: str, content: str) -> bool:
        """
        向云文档追加内容
        
        Args:
            doc_token (str): 云文档token
            content (str): 要追加的内容
            
        Returns:
            bool: 是否成功
        """
        try:
            # 首先测试文档连接
            if not self.test_doc_connection(doc_token):
                self.logger.error(f"文档连接测试失败，doc_token: {doc_token}")
                return False
            
            # 获取文档块信息，找到根块
            blocks_info = self.get_doc_blocks(doc_token, page_size=1)
            if not blocks_info or not blocks_info.get('items'):
                self.logger.error("无法获取文档块信息")
                return False
            
            # 获取根块ID
            root_block = blocks_info['items'][0]
            # Block对象使用属性访问，不是字典
            root_block_id = getattr(root_block, 'block_id', None)
            if not root_block_id:
                self.logger.error("无法获取根块ID")
                return False
            
            self.logger.info(f"找到根块ID: {root_block_id}")
            
            # 将内容按行分割并构建块结构
            lines = content.split('\n')
            children = []
            
            for line in lines:
                if line.strip():  # 非空行
                    # 创建文本块
                    text_element = TextElement.builder() \
                        .text_run(TextRun.builder().content(line + "\n").build()) \
                        .build()
                    
                    text_block = Text.builder() \
                        .elements([text_element]) \
                        .build()
                    
                    block = Block.builder() \
                        .block_type(2) \
                        .text(text_block) \
                        .build()
                    
                    children.append(block)
            
            # 如果没有有效内容，添加一个包含原始内容的块
            if not children:
                text_element = TextElement.builder() \
                    .text_run(TextRun.builder().content(content + "\n").build()) \
                    .build()
                
                text_block = Text.builder() \
                    .elements([text_element]) \
                    .build()
                
                block = Block.builder() \
                    .block_type(2) \
                    .text(text_block) \
                    .build()
                
                children.append(block)
            
            # 构造请求对象
            request_body = CreateDocumentBlockChildrenRequestBody.builder() \
                .children(children) \
                .index(-1) \
                .document_revision_id(-1) \
                .build()
            
            request = CreateDocumentBlockChildrenRequest.builder() \
                .document_id(doc_token) \
                .block_id(root_block_id) \
                .request_body(request_body) \
                .build()
            
            # 发起请求
            response = self.client.docx.v1.document_block_children.create(request)
            
            # 处理失败返回
            if not response.success():
                self.logger.error(
                    f"追加文档内容失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
                
                # 提供更详细的错误信息
                if response.code == 99991663:
                    self.logger.error("权限不足：请确保应用已被添加为文档协作者")
                elif response.code == 99991400:
                    self.logger.error("文档不存在或token无效")
                
                return False
            
            self.logger.info("云文档内容追加成功")
            return True
            
        except Exception as e:
            self.logger.error(f"云文档内容追加异常: {str(e)}")
            return False
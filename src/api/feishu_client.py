#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书API客户端模块
用于与飞书多维表格进行交互，实现视频分析结果的云端存储和管理
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

class FeishuClient:
    """
    飞书API客户端类
    提供与飞书多维表格的交互功能
    """
    
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化飞书客户端
        
        Args:
            app_id (str): 飞书应用ID
            app_secret (str): 飞书应用密钥
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expires_at = 0
        self.base_url = "https://open.feishu.cn/open-apis"
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
    
    def _get_access_token(self) -> bool:
        """
        获取访问令牌
        
        Returns:
            bool: 是否成功获取令牌
        """
        try:
            # 检查当前令牌是否有效
            if self.access_token and time.time() < self.token_expires_at:
                return True
            
            url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
            headers = {
                "Content-Type": "application/json; charset=utf-8"
            }
            data = {
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0:
                self.access_token = result["tenant_access_token"]
                # 令牌有效期为2小时，提前5分钟刷新
                self.token_expires_at = time.time() + result["expire"] - 300
                self.logger.info("飞书访问令牌获取成功")
                return True
            else:
                self.logger.error(f"获取飞书访问令牌失败: {result.get('msg')}")
                return False
                
        except Exception as e:
            self.logger.error(f"获取飞书访问令牌异常: {str(e)}")
            return False
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Optional[Dict]:
        """
        发起API请求
        
        Args:
            method (str): HTTP方法
            endpoint (str): API端点
            data (Dict, optional): 请求数据
            params (Dict, optional): URL参数
            
        Returns:
            Optional[Dict]: 响应数据
        """
        if not self._get_access_token():
            self.logger.error("获取访问令牌失败")
            return None
        
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json; charset=utf-8"
            }
            
            # 记录请求详情
            self.logger.info(f"发起API请求: {method.upper()} {url}")
            if params:
                self.logger.info(f"请求参数: {params}")
            if data:
                self.logger.info(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params or data)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, params=params)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, params=params)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            # 记录响应状态
            self.logger.info(f"响应状态码: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            
            # 记录响应详情
            self.logger.info(f"响应结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get("code") == 0:
                self.logger.info("API请求成功")
                return result.get("data")
            else:
                error_code = result.get('code')
                error_msg = result.get('msg')
                self.logger.error(f"API请求失败: code={error_code}, msg={error_msg}")
                
                # 检查特定的错误类型
                if error_code == 1254005:  # 记录不存在
                    self.logger.error("错误类型: 记录不存在 (RecordIdNotFound)")
                elif error_code == 1254004:  # 表格不存在
                    self.logger.error("错误类型: 表格不存在")
                elif error_code == 1254001:  # 应用不存在
                    self.logger.error("错误类型: 应用不存在")
                
                return None
                
        except Exception as e:
            self.logger.error(f"API请求异常: {str(e)}")
            # 记录详细的错误信息
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"响应状态码: {e.response.status_code}")
                try:
                    error_detail = e.response.json()
                    self.logger.error(f"API错误详情: {json.dumps(error_detail, ensure_ascii=False, indent=2)}")
                except:
                    self.logger.error(f"API响应内容: {e.response.text}")
            return None
    
    def create_bitable(self, name: str, folder_token: str = None) -> Optional[str]:
        """
        创建多维表格
        
        Args:
            name (str): 表格名称
            folder_token (str, optional): 文件夹令牌
            
        Returns:
            Optional[str]: 表格令牌
        """
        data = {"name": name}
        if folder_token:
            data["folder_token"] = folder_token
        
        result = self._make_request("POST", "/bitable/v1/apps", data)
        if result:
            return result.get("app", {}).get("app_token")
        return None
    
    def create_table(self, app_token: str, table_name: str) -> Optional[str]:
        """
        在多维表格中创建数据表
        
        Args:
            app_token (str): 表格令牌
            table_name (str): 数据表名称
            
        Returns:
            Optional[str]: 数据表ID
        """
        data = {
            "table": {
                "name": table_name
            }
        }
        
        result = self._make_request("POST", f"/bitable/v1/apps/{app_token}/tables", data)
        if result:
            return result.get("table_id")
        return None
    
    def create_fields(self, app_token: str, table_id: str, fields: List[Dict]) -> bool:
        """
        创建数据表字段
        
        Args:
            app_token (str): 表格令牌
            table_id (str): 数据表ID
            fields (List[Dict]): 字段定义列表
            
        Returns:
            bool: 是否创建成功
        """
        success_count = 0
        for field in fields:
            # 修复API调用参数格式
            result = self._make_request("POST", f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields", field)
            if result:
                success_count += 1
        
        return success_count == len(fields)
    
    def _create_single_field(self, field_name: str, field_type: int, field_property: Dict = None) -> bool:
        """
        创建单个字段
        
        Args:
            field_name (str): 字段名称
            field_type (int): 字段类型
            field_property (Dict, optional): 字段属性
            
        Returns:
            bool: 是否创建成功
        """
        if not hasattr(self, 'app_token') or not hasattr(self, 'table_id'):
            self.logger.error("飞书表格配置不完整，无法创建字段")
            return False
        
        field_data = {
            "field_name": field_name,
            "type": field_type,
            "property": field_property or {}
        }
        
        try:
            result = self._make_request(
                "POST", 
                f"/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/fields", 
                field_data
            )
            
            if result:
                self.logger.info(f"成功创建字段: {field_name}")
                return True
            else:
                self.logger.error(f"创建字段失败: {field_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"创建字段 {field_name} 时发生错误: {str(e)}")
            return False
    
    def add_record(self, app_token: str, table_id: str, record_data: Dict) -> Optional[str]:
        """
        添加记录到多维表格
        
        Args:
            app_token (str): 表格令牌
            table_id (str): 数据表ID
            record_data (Dict): 记录数据
            
        Returns:
            Optional[str]: 记录ID
        """
        # 按照官方SDK格式构造请求体
        data = {
            "fields": record_data
        }
        
        # 添加必要的查询参数
        url = f"/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        params = {
            "user_id_type": "open_id"
        }
        
        result = self._make_request("POST", url, data, params)
        if result:
            return result.get("record", {}).get("record_id")
        return None
    
    def update_record(self, app_token: str, table_id: str, record_id: str, record_data: Dict) -> bool:
        """
        更新记录
        
        Args:
            app_token (str): 表格令牌
            table_id (str): 数据表ID
            record_id (str): 记录ID
            record_data (Dict): 更新的记录数据
            
        Returns:
            bool: 是否更新成功
        """
        data = {
            "fields": record_data
        }
        
        # 先检查记录是否存在
        try:
            # 尝试获取记录来验证其存在性
            get_result = self._make_request("GET", f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}")
            if get_result is None:
                self.logger.warning(f"记录 {record_id} 不存在，无法更新")
                return False
        except Exception as e:
            self.logger.warning(f"检查记录存在性时出错: {str(e)}")
            # 继续尝试更新，让API返回具体错误
        
        result = self._make_request("PUT", f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}", data)
        return result is not None
    
    def get_records(self, app_token: str, table_id: str, page_size: int = 100, page_token: str = None) -> Optional[Dict]:
        """
        获取记录列表
        
        Args:
            app_token (str): 表格令牌
            table_id (str): 数据表ID
            page_size (int): 每页记录数
            page_token (str, optional): 分页令牌
            
        Returns:
            Optional[Dict]: 记录列表和分页信息
        """
        params = {"page_size": page_size}
        if page_token:
            params["page_token"] = page_token
        
        return self._make_request("GET", f"/bitable/v1/apps/{app_token}/tables/{table_id}/records", params)
    
    def delete_record(self, app_token: str, table_id: str, record_id: str) -> bool:
        """
        删除记录
        
        Args:
            app_token (str): 表格令牌
            table_id (str): 数据表ID
            record_id (str): 记录ID
            
        Returns:
            bool: 是否删除成功
        """
        result = self._make_request("DELETE", f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}")
        return result is not None
    
    def test_connection(self) -> bool:
        """
        测试飞书连接
        
        Returns:
            bool: 连接是否成功
        """
        return self._get_access_token()
    
    def verify_table_exists(self, app_token: str, table_id: str) -> bool:
        """
        验证表格和数据表是否存在
        
        Args:
            app_token (str): 表格令牌
            table_id (str): 数据表ID
            
        Returns:
            bool: 表格是否存在
        """
        try:
            # 尝试获取表格信息
            result = self._make_request("GET", f"/bitable/v1/apps/{app_token}/tables/{table_id}")
            return result is not None
        except Exception as e:
            self.logger.error(f"验证表格存在性失败: {str(e)}")
            return False
    
    def get_field_config(self, app_token: str, table_id: str) -> Optional[Dict]:
        """
        获取表格字段配置
        
        Args:
            app_token (str): 表格令牌
            table_id (str): 数据表ID
            
        Returns:
            Optional[Dict]: 字段配置信息
        """
        try:
            result = self._make_request(
                "GET", 
                f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
            )
            
            if result:
                # 检查是否有items字段（直接在result中或在data中）
                items = result.get('items') or (result.get('data', {}).get('items') if 'data' in result else None)
                
                if items:
                    field_config = {}
                    for field in items:
                        field_name = field.get('field_name', '')
                        field_config[field_name] = {
                            'field_id': field.get('field_id', ''),
                            'type': field.get('type', 1),
                            'property': field.get('property', {}),
                            'ui_type': field.get('ui_type', '')
                        }
                    return field_config
                else:
                    self.logger.error(f"获取字段配置失败，响应格式不正确: {result}")
                    return None
            else:
                self.logger.error("获取字段配置失败，无响应")
                return None
                
        except Exception as e:
            self.logger.error(f"获取字段配置时发生错误: {str(e)}")
            return None
    
    def get_video_analysis_fields(self) -> List[Dict]:
        """
        获取视频分析表的字段定义
        
        Returns:
            List[Dict]: 字段定义列表
        """
        return [
            {
                "field_name": "文件名称",
                "type": 1,  # 文本类型
                "property": {}
            },
            {
                "field_name": "文件路径",
                "type": 1,  # 文本类型
                "property": {}
            },
            {
                "field_name": "文件大小",
                "type": 2,  # 数字类型
                "property": {}
            },
            {
                "field_name": "文件格式",
                "type": 1,  # 文本类型
                "property": {}
            },
            {
                "field_name": "分析提示词",
                "type": 1,  # 文本类型
                "property": {}
            },
            {
                "field_name": "分析结果",
                "type": 1,  # 文本类型
                "property": {}
            },
            {
                "field_name": "创建时间",
                "type": 5,  # 日期时间类型
                "property": {}
            },
            {
                "field_name": "序列ID",
                "type": 1,  # 文本类型
                "property": {}
            },
            {
                "field_name": "扣子调用ID",
                "type": 1,  # 文本类型
                "property": {}
            },
            {
                "field_name": "标签",
                "type": 1,  # 文本类型
                "property": {}
            }
        ]
    
    def get_spreadsheet_info(self, spreadsheet_token: str) -> Optional[Dict]:
        """
        获取电子表格信息
        
        Args:
            spreadsheet_token (str): 电子表格token
            
        Returns:
            Optional[Dict]: 电子表格信息
        """
        try:
            endpoint = f"/sheets/v3/spreadsheets/{spreadsheet_token}"
            response = self._make_request("GET", endpoint)
            # _make_request在成功时返回data部分，失败时返回None
            return response
        except Exception as e:
            self.logger.error(f"获取电子表格信息失败: {e}")
            return None
    
    def get_spreadsheet_range(self, spreadsheet_token: str, sheet_id: str, range_str: str) -> Optional[Dict]:
        """
        获取电子表格指定范围的数据
        
        Args:
            spreadsheet_token (str): 电子表格token
            sheet_id (str): 工作表ID
            range_str (str): 范围字符串，如"A1:C10"
            
        Returns:
            Optional[Dict]: 范围数据，格式为 {'values': [[...], [...]]}
        """
        try:
            endpoint = f"/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}!{range_str}"
            response = self._make_request("GET", endpoint)
            
            if response and 'valueRange' in response:
                # 提取valueRange中的values
                value_range = response['valueRange']
                return {
                    'values': value_range.get('values', [])
                }
            elif response:
                # 如果直接包含values，直接返回
                return response
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"获取电子表格范围数据失败: {e}")
            return None
    
    def update_spreadsheet_range(self, spreadsheet_token: str, sheet_id: str, range_str: str, values: List[List[str]]) -> bool:
        """
        更新电子表格指定范围的数据
        
        Args:
            spreadsheet_token (str): 电子表格token
            sheet_id (str): 工作表ID
            range_str (str): 范围字符串，如"A1:C10"
            values (List[List[str]]): 要更新的数据
            
        Returns:
            bool: 更新是否成功
        """
        try:
            endpoint = f"/sheets/v2/spreadsheets/{spreadsheet_token}/values"
            data = {
                "valueRange": {
                    "range": f"{sheet_id}!{range_str}",
                    "values": values
                }
            }
            
            self.logger.info(f"准备更新电子表格: {spreadsheet_token[:10]}...")
            self.logger.info(f"工作表ID: {sheet_id}")
            self.logger.info(f"范围: {range_str}")
            self.logger.info(f"数据: {values}")
            
            # 直接调用底层请求，不通过_make_request以获得更详细的控制
            if not self._get_access_token():
                self.logger.error("获取访问令牌失败")
                return False
            
            url = f"{self.base_url}{endpoint}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json; charset=utf-8"
            }
            
            self.logger.info(f"发起PUT请求: {url}")
            response = requests.put(url, headers=headers, json=data)
            
            self.logger.info(f"响应状态码: {response.status_code}")
            self.logger.info(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    self.logger.info(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    
                    # 检查是否有错误码
                    if 'code' in result and result['code'] != 0:
                        self.logger.error(f"API返回错误: code={result.get('code')}, msg={result.get('msg')}")
                        return False
                    
                    self.logger.info(f"成功更新电子表格范围 {range_str}")
                    return True
                except json.JSONDecodeError:
                    self.logger.info(f"响应不是JSON格式: {response.text}")
                    # 某些成功的响应可能不是JSON格式
                    return True
            else:
                self.logger.error(f"HTTP请求失败: {response.status_code}")
                self.logger.error(f"错误响应: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"更新电子表格范围异常: {e}")
            import traceback
            self.logger.error(f"异常堆栈: {traceback.format_exc()}")
            return False
    
    def append_spreadsheet_values(self, spreadsheet_token: str, sheet_id: str, values: List[List[str]]) -> bool:
        """
        向电子表格追加数据
        
        Args:
            spreadsheet_token (str): 电子表格token
            sheet_id (str): 工作表ID
            values (List[List[str]]): 要追加的数据
            
        Returns:
            bool: 追加是否成功
        """
        try:
            endpoint = f"/sheets/v2/spreadsheets/{spreadsheet_token}/values_append"
            data = {
                "valueRange": {
                    "range": f"{sheet_id}!A:A",
                    "values": values
                }
            }
            response = self._make_request("POST", endpoint, data=data)
            
            # 电子表格API成功时直接返回数据，不包含code字段
            if response is not None:
                self.logger.info(f"成功向电子表格追加 {len(values)} 行数据: {response}")
                return True
            else:
                self.logger.error(f"向电子表格追加数据失败: 响应为空")
                return False
                
        except Exception as e:
            self.logger.error(f"向电子表格追加数据异常: {e}")
            return False
    
    def create_spreadsheet_sheet(self, spreadsheet_token: str, sheet_name: str) -> Optional[str]:
        """
        在电子表格中创建新的工作表
        
        Args:
            spreadsheet_token (str): 电子表格token
            sheet_name (str): 工作表名称
            
        Returns:
            Optional[str]: 新创建的工作表ID
        """
        try:
            endpoint = f"/sheets/v3/spreadsheets/{spreadsheet_token}/sheets"
            data = {
                "properties": {
                    "title": sheet_name
                }
            }
            response = self._make_request("POST", endpoint, data=data)
            
            # 电子表格API成功时直接返回数据，不包含code字段
            if response is not None:
                sheet_id = response.get('sheet', {}).get('sheetId')
                self.logger.info(f"成功创建工作表: {sheet_name}, ID: {sheet_id}")
                return sheet_id
            else:
                self.logger.error(f"创建工作表失败: 响应为空")
                return None
                
        except Exception as e:
            self.logger.error(f"创建工作表异常: {e}")
            return None
    
    def test_spreadsheet_connection(self, spreadsheet_token: str) -> bool:
        """
        测试电子表格连接
        
        Args:
            spreadsheet_token (str): 电子表格token
            
        Returns:
            bool: 连接是否成功
        """
        try:
            response = self.get_spreadsheet_info(spreadsheet_token)
            # _make_request在成功时返回data部分，失败时返回None
            return response is not None
        except Exception as e:
            self.logger.error(f"测试电子表格连接失败: {e}")
            return False
    
    def get_doc_info(self, doc_token: str) -> Optional[Dict]:
        """
        获取云文档信息
        
        Args:
            doc_token (str): 云文档token
            
        Returns:
            Optional[Dict]: 云文档信息
        """
        endpoint = f"/docx/v1/documents/{doc_token}"
        
        # 直接调用API，不使用_make_request的简化版本
        if not self._get_access_token():
            self.logger.error("获取访问令牌失败")
            return None
        
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json; charset=utf-8"
            }
            
            self.logger.info(f"发起云文档API请求: GET {url}")
            response = requests.get(url, headers=headers)
            
            self.logger.info(f"云文档API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"云文档API响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if result.get("code") == 0:
                    return result.get("data", {})
                else:
                    error_code = result.get('code')
                    error_msg = result.get('msg')
                    self.logger.error(f"云文档API请求失败: code={error_code}, msg={error_msg}")
                    return None
            else:
                self.logger.error(f"云文档API请求HTTP错误: {response.status_code}")
                try:
                    error_detail = response.json()
                    self.logger.error(f"错误详情: {json.dumps(error_detail, ensure_ascii=False, indent=2)}")
                except:
                    self.logger.error(f"错误响应内容: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"云文档API请求异常: {str(e)}")
            return None
    
    def test_doc_connection(self, doc_token: str) -> bool:
        """
        测试云文档连接
        
        Args:
            doc_token (str): 云文档token
            
        Returns:
            bool: 连接是否成功
        """
        try:
            result = self.get_doc_info(doc_token)
            return result is not None
        except Exception as e:
            self.logger.error(f"测试云文档连接失败: {str(e)}")
            return False
    
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
            
            # 获取文档信息以确定插入位置
            doc_info = self.get_doc_info(doc_token)
            if not doc_info:
                self.logger.error(f"无法获取文档信息，doc_token: {doc_token}")
                return False
            
            # 获取文档的blocks信息，找到根block
            blocks_endpoint = f"/docx/v1/documents/{doc_token}/blocks"
            blocks_result = self._make_request("GET", blocks_endpoint, params={"document_revision_id": -1, "page_size": 1})
            
            if not blocks_result:
                self.logger.error("获取文档blocks失败: 请求返回空结果")
                return False
            
            # 获取根block ID - _make_request已经返回了data部分
            blocks = blocks_result.get("items", [])
            if not blocks:
                self.logger.error("文档中没有找到blocks")
                return False
            
            root_block_id = blocks[0].get("block_id")
            if not root_block_id:
                self.logger.error("无法获取根block ID")
                return False
            
            # 构建插入内容的请求 - 使用正确的端点格式
            endpoint = f"/docx/v1/documents/{doc_token}/blocks/{root_block_id}/children"
            
            # 将内容按行分割并构建块结构
            lines = content.split('\n')
            children = []
            
            for line in lines:
                if line.strip():  # 非空行
                    children.append({
                        "block_type": 2,  # 文本块
                        "text": {
                            "elements": [{
                                "text_run": {
                                    "content": line + "\n"
                                }
                            }]
                        }
                    })
            
            # 如果没有有效内容，添加一个空行
            if not children:
                children.append({
                    "block_type": 2,
                    "text": {
                        "elements": [{
                            "text_run": {
                                "content": content + "\n"
                            }
                        }]
                    }
                })
            
            data = {
                "children": children,
                "index": -1,  # 插入到末尾
                "document_revision_id": -1
            }
            
            result = self._make_request("POST", endpoint, data=data)
            
            if result is not None:
                self.logger.info("云文档内容追加成功")
                return True
            else:
                self.logger.error("云文档内容追加失败: API请求失败")
                return False
                
        except Exception as e:
            self.logger.error(f"云文档内容追加异常: {str(e)}")
            return False
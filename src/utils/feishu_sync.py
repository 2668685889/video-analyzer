#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书数据同步服务模块
负责本地数据库与飞书多维表格之间的数据同步
"""

import logging
import threading
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from ..api.feishu_client import FeishuClient
from .config import config
from .database import db
from .feishu_field_fixer import FeishuFieldFixer
from .custom_field_mapper import CustomFieldMapper
from .ai_output_adapter import AIOutputAdapter

class FeishuSyncService:
    """
    飞书数据同步服务类
    提供本地数据库与飞书多维表格的双向同步功能
    """
    
    def __init__(self):
        """
        初始化飞书同步服务
        """
        self.feishu_client = None
        self.sync_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        self.field_fixer = FeishuFieldFixer()
        self.custom_mapper = CustomFieldMapper()
        self.ai_adapter = AIOutputAdapter()
        self.last_sync_time = None
        self._init_client()
    
    def _init_client(self) -> bool:
        """
        初始化飞书客户端
        
        Returns:
            bool: 是否初始化成功
        """
        try:
            if config.is_feishu_valid():
                feishu_config = config.get_feishu_config()
                self.feishu_client = FeishuClient(
                    app_id=feishu_config['app_id'],
                    app_secret=feishu_config['app_secret']
                )
                return True
            else:
                self.logger.debug("飞书配置无效，无法初始化客户端")
                return False
        except Exception as e:
            self.logger.error(f"初始化飞书客户端失败: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """
        测试飞书连接
        
        Returns:
            bool: 连接是否正常
        """
        if not self.feishu_client:
            return False
        return self.feishu_client.test_connection()
    
    def sync_record_to_feishu(self, sequence_id: str, force_resync: bool = False) -> bool:
        """
        将单条记录同步到飞书
        
        Args:
            sequence_id (str): 记录的序列ID
            force_resync (bool): 是否强制重新同步已同步的记录
            
        Returns:
            bool: 是否同步成功
        """
        if not self.feishu_client or not config.feishu_enabled:
            self.logger.warning(f"飞书客户端未初始化或飞书功能未启用: client={self.feishu_client is not None}, enabled={config.feishu_enabled}")
            return False
        
        try:
            with self.sync_lock:
                self.logger.info(f"开始同步记录到飞书: sequence_id={sequence_id}")
                
                # 从本地数据库获取记录
                record = db.get_analysis_by_sequence_id(sequence_id)
                if not record:
                    self.logger.error(f"未找到序列ID为 {sequence_id} 的记录")
                    return False
                
                self.logger.info(f"获取到记录: 文件名={record.get('file_name', 'Unknown')}, 文件大小={record.get('file_size', 0)} bytes")
                
                # 检查是否已经同步过
                if record.get('feishu_record_id') and not force_resync:
                    self.logger.info(f"记录 {sequence_id} 已经同步到飞书，feishu_record_id={record.get('feishu_record_id')}")
                    return True
                elif record.get('feishu_record_id') and force_resync:
                    self.logger.info(f"记录 {sequence_id} 强制重新同步，清除现有飞书记录ID")
                    # 清除现有的飞书记录ID，强制创建新记录
                    db.update_feishu_record_id(sequence_id, None)
                
                self.logger.info("记录未同步，开始准备飞书数据...")
                
                # 准备飞书记录数据
                feishu_data = self._prepare_feishu_record(record)
                if not feishu_data:
                    self.logger.error(f"准备飞书数据失败: {sequence_id}")
                    return False
                
                self.logger.info(f"飞书数据准备完成，字段数量: {len(feishu_data)}")
                self.logger.info(f"准备发送的飞书数据: {json.dumps(feishu_data, ensure_ascii=False, indent=2)}")
                
                # 添加到飞书表格
                feishu_config = config.get_feishu_config()
                self.logger.info(f"飞书配置: app_token={feishu_config['app_token'][:10]}..., table_id={feishu_config['table_id']}")
                
                record_id = self.feishu_client.add_record(
                    app_token=feishu_config['app_token'],
                    table_id=feishu_config['table_id'],
                    record_data=feishu_data
                )
                
                if record_id:
                    # 更新本地记录的飞书ID
                    self.logger.info(f"飞书API返回记录ID: {record_id}")
                    db.update_feishu_record_id(sequence_id, record_id)
                    # 更新最后同步时间
                    self.last_sync_time = datetime.now()
                    self.logger.info(f"记录 {sequence_id} 成功同步到飞书，记录ID: {record_id}")
                    return True
                else:
                    self.logger.error(f"记录 {sequence_id} 同步到飞书失败，未返回记录ID")
                    return False
                    
        except Exception as e:
            error_msg = str(e)
            if "FieldNameNotFound" in error_msg:
                self.logger.error(f"飞书表格字段不存在错误: {error_msg}")
                self.logger.error("解决方案:")
                self.logger.error("1. 确保飞书应用已被添加为多维表格协作者")
                self.logger.error("2. 在应用程序中点击'设置表格结构'按钮")
                self.logger.error("3. 或参考 shuoming/FEISHU_FIELD_SETUP_GUIDE.md 手动创建字段")
            else:
                self.logger.error(f"同步记录到飞书异常: {error_msg}")
            return False
    
    def sync_all_records_to_feishu(self, include_synced: bool = False) -> Dict[str, int]:
        """
        将记录同步到飞书
        
        Args:
            include_synced (bool): 是否包含已同步的记录（执行更新操作）
        
        Returns:
            Dict[str, int]: 同步结果统计
        """
        if not self.feishu_client or not config.feishu_enabled:
            return {'success': 0, 'failed': 0, 'skipped': 0, 'created': 0, 'updated': 0}
        
        try:
            if include_synced:
                # 获取所有记录
                all_records = db.get_all_history_records()
            else:
                # 获取所有未同步的记录
                all_records = db.get_unsynced_records()
            
            success_count = 0
            failed_count = 0
            created_count = 0
            updated_count = 0
            
            for record in all_records:
                sequence_id = record['sequence_id']
                
                if record.get('feishu_record_id') and include_synced:
                    # 已同步记录，执行更新
                    if self.update_record_in_feishu(sequence_id):
                        success_count += 1
                        updated_count += 1
                    else:
                        failed_count += 1
                else:
                    # 未同步记录，执行新建
                    if self.sync_record_to_feishu(sequence_id):
                        success_count += 1
                        created_count += 1
                    else:
                        failed_count += 1
                
                # 添加小延迟避免API限流
                time.sleep(0.1)
            
            # 更新最后同步时间
            if success_count > 0:
                self.last_sync_time = datetime.now()
            
            self.logger.info(f"批量同步完成: 成功 {success_count} (新建 {created_count}, 更新 {updated_count}), 失败 {failed_count}")
            return {
                'success': success_count,
                'failed': failed_count,
                'skipped': 0,
                'created': created_count,
                'updated': updated_count
            }
            
        except Exception as e:
            self.logger.error(f"批量同步异常: {str(e)}")
            return {'success': 0, 'failed': 0, 'skipped': 0, 'created': 0, 'updated': 0}
    
    def update_record_in_feishu(self, sequence_id: str) -> bool:
        """
        更新飞书中的记录
        
        Args:
            sequence_id (str): 记录的序列ID
            
        Returns:
            bool: 是否更新成功
        """
        if not self.feishu_client or not config.feishu_enabled:
            return False
        
        try:
            with self.sync_lock:
                # 从本地数据库获取记录
                record = db.get_analysis_by_sequence_id(sequence_id)
                if not record or not record.get('feishu_record_id'):
                    self.logger.error(f"记录 {sequence_id} 不存在或未同步到飞书")
                    return False
                
                # 准备更新数据
                feishu_data = self._prepare_feishu_record(record)
                
                # 更新飞书记录
                feishu_config = config.get_feishu_config()
                success = self.feishu_client.update_record(
                    app_token=feishu_config['app_token'],
                    table_id=feishu_config['table_id'],
                    record_id=record['feishu_record_id'],
                    record_data=feishu_data
                )
                
                if success:
                    self.logger.info(f"记录 {sequence_id} 在飞书中更新成功")
                    return True
                else:
                    # 更新失败，可能是记录已被删除，尝试重新创建
                    self.logger.warning(f"记录 {sequence_id} 更新失败，可能已被删除，尝试重新创建")
                    
                    # 清除本地的飞书记录ID
                    db.update_feishu_record_id(sequence_id, None)
                    
                    # 直接创建新记录，避免sync_record_to_feishu的重复检查
                    return self._create_new_record(sequence_id)
                    
        except Exception as e:
            self.logger.error(f"更新飞书记录异常: {str(e)}")
            # 如果是网络或其他异常，也尝试重新创建
            try:
                self.logger.warning(f"更新异常，尝试清除记录ID并重新创建: {sequence_id}")
                db.update_feishu_record_id(sequence_id, None)
                return self._create_new_record(sequence_id)
            except Exception as retry_e:
                self.logger.error(f"重新创建记录也失败: {str(retry_e)}")
                return False
    
    def _create_new_record(self, sequence_id: str) -> bool:
        """
        直接创建新的飞书记录（不检查是否已存在）
        
        Args:
            sequence_id (str): 记录的序列ID
            
        Returns:
            bool: 是否创建成功
        """
        if not self.feishu_client or not config.feishu_enabled:
            return False
        
        try:
            # 从本地数据库获取记录
            record = db.get_analysis_by_sequence_id(sequence_id)
            if not record:
                self.logger.error(f"未找到序列ID为 {sequence_id} 的记录")
                return False
            
            self.logger.info(f"开始创建新的飞书记录: sequence_id={sequence_id}")
            
            # 准备飞书记录数据
            feishu_data = self._prepare_feishu_record(record)
            if not feishu_data:
                self.logger.error(f"准备飞书数据失败: {sequence_id}")
                return False
            
            # 添加到飞书表格
            feishu_config = config.get_feishu_config()
            record_id = self.feishu_client.add_record(
                app_token=feishu_config['app_token'],
                table_id=feishu_config['table_id'],
                record_data=feishu_data
            )
            
            if record_id:
                # 更新本地记录的飞书ID
                self.logger.info(f"飞书API返回记录ID: {record_id}")
                db.update_feishu_record_id(sequence_id, record_id)
                # 更新最后同步时间
                self.last_sync_time = datetime.now()
                self.logger.info(f"记录 {sequence_id} 成功创建到飞书，记录ID: {record_id}")
                return True
            else:
                self.logger.error(f"记录 {sequence_id} 创建到飞书失败，未返回记录ID")
                return False
                
        except Exception as e:
            self.logger.error(f"创建飞书记录异常: {str(e)}")
            return False
    
    def delete_record_from_feishu(self, sequence_id: str) -> bool:
        """
        从飞书中删除记录
        
        Args:
            sequence_id (str): 记录的序列ID
            
        Returns:
            bool: 是否删除成功
        """
        if not self.feishu_client or not config.feishu_enabled:
            return False
        
        try:
            with self.sync_lock:
                # 从本地数据库获取记录
                record = db.get_analysis_by_sequence_id(sequence_id)
                if not record or not record.get('feishu_record_id'):
                    self.logger.warning(f"记录 {sequence_id} 不存在或未同步到飞书")
                    return True
                
                # 从飞书删除记录
                feishu_config = config.get_feishu_config()
                success = self.feishu_client.delete_record(
                    app_token=feishu_config['app_token'],
                    table_id=feishu_config['table_id'],
                    record_id=record['feishu_record_id']
                )
                
                if success:
                    # 清除本地记录的飞书ID
                    db.update_feishu_record_id(sequence_id, None)
                    self.logger.info(f"记录 {sequence_id} 从飞书中删除成功")
                    return True
                else:
                    self.logger.error(f"记录 {sequence_id} 从飞书中删除失败")
                    return False
                    
        except Exception as e:
            self.logger.error(f"删除飞书记录异常: {str(e)}")
            return False
    
    def _prepare_feishu_record(self, record: Dict) -> Dict[str, Any]:
        """
        准备飞书记录数据
        严格按照自定义字段映射配置执行（不使用回退机制）
        
        Args:
            record (Dict): 本地数据库记录
            
        Returns:
            Dict[str, Any]: 飞书记录数据
        """
        try:
            # 解析analysis_result中的AI模型返回数据
            parsed_ai_data = self._parse_analysis_result(record.get('analysis_result', ''))
            
            # 使用AI输出格式适配器处理数据
            adapter_result = self.ai_adapter.process_ai_output(parsed_ai_data)
            adapted_ai_data = adapter_result['output']
            
            # 记录适配器处理信息
            validation_info = adapter_result['validation']
            processing_info = adapter_result['processing_info']
            self.logger.info(f"🤖 AI输出适配器处理完成: 格式={processing_info['format_type']}, 成功率={validation_info['success_rate']:.2%}")
            self.logger.debug(f"📊 有效字段: {validation_info['valid_fields']}")
            if validation_info['empty_fields']:
                self.logger.debug(f"⚠️  空字段: {validation_info['empty_fields']}")
            
            # 构建完整的AI模型数据结构（使用中文字段名）
            ai_model_data = {
                "视频序列号": record.get('sequence_id', ''),
                "视频源路径": record.get('file_path', ''),
            }
            
            # 合并解析出的AI分析结果（不覆盖重要的数据库字段）
            for key, value in adapted_ai_data.items():
                # 保护重要的数据库字段不被覆盖
                if key in ['视频序列号', '视频源路径'] and ai_model_data.get(key):
                    self.logger.debug(f"🛡️  保护字段 '{key}' 不被覆盖，保持原值: {ai_model_data[key]}")
                    continue
                ai_model_data[key] = value
            
            # 严格使用自定义字段映射配置
            field_mappings = self.custom_mapper.get_field_mappings()
            if not field_mappings:
                error_msg = "❌ 未找到自定义字段映射配置，无法继续处理"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            
            # 使用自定义字段映射器进行转换
            feishu_data = self.custom_mapper.transform_ai_data_to_feishu(ai_model_data)
            
            if not feishu_data:
                error_msg = "❌ 自定义字段映射转换失败，未产生有效数据"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            
            self.logger.info(f"✅ 严格按照自定义字段映射成功转换数据")
            self.logger.info(f"📋 转换后的飞书字段: {list(feishu_data.keys())}")
            
            # 记录详细的映射信息
            for ai_field, feishu_field in field_mappings.items():
                if ai_field in ai_model_data:
                    value = ai_model_data[ai_field]
                    self.logger.debug(f"🔄 字段映射: {ai_field} -> {feishu_field} = {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
            
            return feishu_data
            
        except Exception as e:
            self.logger.error(f"❌ 准备飞书记录数据失败: {str(e)}")
            # 返回最小化的安全数据
            return self.field_fixer.create_minimal_test_record()
    
    def _parse_analysis_result(self, analysis_result: str) -> Dict[str, Any]:
        """
        解析analysis_result字段中的AI模型返回数据
        支持多种格式：JSON、键值对、Markdown等
        
        Args:
            analysis_result (str): 分析结果字符串
            
        Returns:
            Dict[str, Any]: 解析后的数据字典
        """
        import json
        import re
        
        if not analysis_result or not analysis_result.strip():
            return {}
        
        try:
            # 方法1: 尝试直接解析JSON
            if analysis_result.strip().startswith('{') and analysis_result.strip().endswith('}'):
                parsed = json.loads(analysis_result)
                self.logger.debug("✅ 成功解析JSON格式的分析结果")
                return parsed
            
            # 方法2: 提取```json代码块中的JSON
            json_patterns = [
                r'```json\s*({.*?})\s*```',
                r'```\s*({.*?})\s*```',
                r'json\s*({.*?})'
            ]
            
            for pattern in json_patterns:
                json_match = re.search(pattern, analysis_result, re.DOTALL | re.IGNORECASE)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group(1))
                        self.logger.debug(f"✅ 成功从代码块中解析JSON: {pattern}")
                        return parsed
                    except json.JSONDecodeError:
                        continue
            
            # 方法3: 查找任何JSON对象
            json_match = re.search(r'{[^{}]*(?:{[^{}]*}[^{}]*)*}', analysis_result, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(0))
                    self.logger.debug("✅ 成功解析嵌入的JSON对象")
                    return parsed
                except json.JSONDecodeError:
                    pass
            
            # 方法4: 解析键值对格式（支持多种分隔符）
            result = {}
            lines = analysis_result.split('\n')
            
            # 常见的字段名映射
            field_mappings = {
                '视频序列号': 'video_serial_number',
                '序列号': 'video_serial_number',
                'sequence_id': 'video_serial_number',
                '视频内容摘要': 'video_content_summary',
                '内容摘要': 'video_content_summary',
                '摘要': 'video_content_summary',
                'summary': 'video_content_summary',
                '详细内容描述': 'detailed_content_description',
                '详细描述': 'detailed_content_description',
                '内容描述': 'detailed_content_description',
                'description': 'detailed_content_description',
                '主要人物对象': 'main_characters_objects',
                '人物对象': 'main_characters_objects',
                '主要人物': 'main_characters_objects',
                'characters': 'main_characters_objects',
                '关键词标签': 'keywords_tags',
                '关键词': 'keywords_tags',
                '标签': 'keywords_tags',
                'keywords': 'keywords_tags',
                'tags': 'keywords_tags',
                '视频源路径': 'video_source_path',
                '文件路径': 'video_source_path',
                '路径': 'video_source_path',
                'path': 'video_source_path',
                'file_path': 'video_source_path'
            }
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 尝试不同的分隔符
                separators = [':', '：', '=', '-', '|']
                for sep in separators:
                    if sep in line:
                        parts = line.split(sep, 1)
                        if len(parts) == 2:
                            key = parts[0].strip().strip('*').strip('#').strip()
                            value = parts[1].strip().strip('"').strip("'").strip()
                            
                            if key and value:
                                # 尝试映射到标准字段名
                                mapped_key = field_mappings.get(key.lower(), key)
                                if mapped_key not in result:  # 避免重复
                                    result[mapped_key] = value
                        break
            
            if result:
                self.logger.debug(f"✅ 成功解析键值对格式，提取到 {len(result)} 个字段")
                return result
            
            # 方法5: 尝试从自然语言中提取信息
            self.logger.warning("⚠️  无法解析结构化数据，尝试从文本中提取信息")
            
            # 简单的文本提取逻辑
            text_result = {
                'video_content_summary': analysis_result[:500] if len(analysis_result) > 500 else analysis_result,
                'detailed_content_description': analysis_result
            }
            
            return text_result
            
        except Exception as e:
            self.logger.error(f"❌ 解析analysis_result异常: {str(e)}")
            # 返回原始文本作为摘要
            return {
                'video_content_summary': analysis_result[:200] if analysis_result else '',
                'detailed_content_description': analysis_result if analysis_result else ''
            }
    
    def _analyze_and_adapt_ai_data(self, ai_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        严格按照自定义映射配置进行字段映射（不使用智能算法）
        
        Args:
            ai_data (Dict[str, Any]): AI模型返回的原始数据
            
        Returns:
            Dict[str, Any]: 严格按配置映射后的数据
        """
        try:
            # 获取当前的字段映射配置
            ai_model_fields = self.custom_mapper.get_ai_model_fields()
            field_mappings = self.custom_mapper.get_field_mappings()
            
            if not ai_model_fields or not field_mappings:
                self.logger.debug("📋 未找到字段映射配置，返回原始数据")
                return ai_data
            
            adapted_data = {}
            unmapped_fields = []
            
            # 严格按照配置进行字段映射（仅精确匹配）
            for key, value in ai_data.items():
                # 只进行精确匹配，不使用智能算法
                if key in field_mappings:
                    adapted_data[key] = value
                    self.logger.debug(f"✅ 精确匹配: {key} -> {field_mappings[key]}")
                else:
                    unmapped_fields.append(key)
                    self.logger.debug(f"⚠️  字段 '{key}' 未在映射配置中找到，跳过")
            
            if unmapped_fields:
                self.logger.warning(f"⚠️  以下字段未在映射配置中定义，已跳过: {unmapped_fields}")
            
            # 确保配置中定义的AI字段都存在（使用默认值，但不覆盖已有值）
            for ai_field in ai_model_fields.keys():
                if ai_field not in adapted_data:
                    adapted_data[ai_field] = ''
                    self.logger.debug(f"🔧 为配置字段 '{ai_field}' 设置默认值")
            
            self.logger.info(f"✅ 严格映射完成，成功映射字段数: {len([k for k in ai_data.keys() if k in field_mappings])}")
            return adapted_data
            
        except Exception as e:
            self.logger.error(f"❌ 严格映射失败: {str(e)}")
            return ai_data
    
    def _generate_tags(self, record: Dict) -> str:
        """
        基于记录内容生成标签
        
        Args:
            record (Dict): 数据库记录
            
        Returns:
            str: 逗号分隔的标签字符串
        """
        tags = []
        
        # 基于文件格式添加标签
        if record.get('mime_type'):
            file_format = record['mime_type'].split('/')[-1]
            tags.append(f"格式:{file_format}")
        
        # 基于文件大小添加标签
        file_size = record.get('file_size', 0)
        if file_size > 100 * 1024 * 1024:  # 大于100MB
            tags.append("大文件")
        elif file_size < 10 * 1024 * 1024:  # 小于10MB
            tags.append("小文件")
        
        # 基于分析提示词添加标签
        prompt = record.get('analysis_prompt', '').lower()
        if '摘要' in prompt:
            tags.append("摘要分析")
        if '分类' in prompt:
            tags.append("内容分类")
        if '情感' in prompt:
            tags.append("情感分析")
        if '关键词' in prompt:
            tags.append("关键词提取")
        
        # 添加时间标签
        created_at = record.get('created_at')
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                tags.append(f"日期:{dt.strftime('%Y-%m')}")
            except:
                pass
        
        return ",".join(tags)
    
    def _format_datetime(self, datetime_str: str) -> int:
        """
        格式化日期时间为飞书时间戳
        
        Args:
            datetime_str (str): 日期时间字符串
            
        Returns:
            int: 时间戳（毫秒）
        """
        try:
            if datetime_str:
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                return int(dt.timestamp() * 1000)
            return int(datetime.now().timestamp() * 1000)
        except:
            return int(datetime.now().timestamp() * 1000)
    
    def setup_feishu_table(self) -> bool:
        """
        设置飞书表格（创建表格和字段）
        
        Returns:
            bool: 是否设置成功
        """
        if not self.feishu_client:
            return False
        
        try:
            feishu_config = config.get_feishu_config()
            
            # 如果已有表格配置，验证是否真实存在
            if feishu_config['app_token'] and feishu_config['table_id']:
                if self.feishu_client.verify_table_exists(feishu_config['app_token'], feishu_config['table_id']):
                    self.logger.info("飞书表格已配置且存在")
                    return True
                else:
                    self.logger.warning("配置的飞书表格不存在，将重新创建")
                    # 清空无效配置
                    config.update_feishu_config({'app_token': '', 'table_id': ''})
                    feishu_config['app_token'] = ''
                    feishu_config['table_id'] = ''
            
            # 创建多维表格
            if not feishu_config['app_token']:
                app_token = self.feishu_client.create_bitable("视频分析结果")
                if not app_token:
                    self.logger.error("创建飞书多维表格失败")
                    return False
                
                # 更新配置
                config.update_feishu_config({'app_token': app_token})
                feishu_config['app_token'] = app_token
            
            # 创建数据表
            if not feishu_config['table_id']:
                table_id = self.feishu_client.create_table(
                    app_token=feishu_config['app_token'],
                    table_name="视频分析数据"
                )
                if not table_id:
                    self.logger.error("创建飞书数据表失败")
                    return False
                
                # 创建字段
                fields = self.feishu_client.get_video_analysis_fields()
                if not self.feishu_client.create_fields(
                    app_token=feishu_config['app_token'],
                    table_id=table_id,
                    fields=fields
                ):
                    self.logger.error("创建飞书表格字段失败")
                    return False
                
                # 更新配置
                config.update_feishu_config({'table_id': table_id})
            
            self.logger.info("飞书表格设置完成")
            return True
            
        except Exception as e:
            self.logger.error(f"设置飞书表格异常: {str(e)}")
            return False
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        获取同步状态信息
        
        Returns:
            Dict[str, Any]: 同步状态信息
        """
        try:
            total_records = db.get_total_analysis_count()
            synced_records = db.get_synced_records_count()
            unsynced_records = total_records - synced_records
            
            return {
                'enabled': config.feishu_enabled,
                'connected': self.test_connection(),
                'total_records': total_records,
                'synced_records': synced_records,
                'unsynced_records': unsynced_records,
                'sync_rate': (synced_records / total_records * 100) if total_records > 0 else 0,
                'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None
            }
        except Exception as e:
            self.logger.error(f"获取同步状态异常: {str(e)}")
            return {
                'enabled': False,
                'connected': False,
                'total_records': 0,
                'synced_records': 0,
                'unsynced_records': 0,
                'sync_rate': 0,
                'last_sync_time': None
            }

# 创建全局同步服务实例
feishu_sync = FeishuSyncService()
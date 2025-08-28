#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能字段设置模块
自动分析历史记录内容并设置飞书多维表格字段
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .field_mapper import field_mapper
from .database import VideoAnalysisDB

class SmartFieldSetup:
    """
    智能字段设置器
    自动分析内容并设置飞书字段
    """
    
    def __init__(self, db: VideoAnalysisDB, feishu_client):
        """
        初始化智能字段设置器
        
        Args:
            db (VideoAnalysisDB): 数据库实例
            feishu_client: 飞书客户端实例
        """
        self.db = db
        self.feishu_client = feishu_client
        self.logger = logging.getLogger(__name__)
        
        # 模板保存路径
        self.template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'shuoming')
        os.makedirs(self.template_dir, exist_ok=True)
    
    def analyze_historical_data(self, limit: int = 10) -> Dict[str, Any]:
        """
        分析历史数据，提取字段结构信息
        
        Args:
            limit (int): 分析的记录数量限制
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        try:
            # 获取最近的分析记录
            records = self.db.get_recent_records(limit)
            
            if not records:
                self.logger.warning("没有找到历史记录用于分析")
                return {
                    "status": "no_data",
                    "message": "没有历史记录可供分析",
                    "analysis_result": None
                }
            
            # 合并所有分析结果进行结构分析
            combined_content = ""
            sample_records = []
            
            for record in records:
                if record.get('analysis_result'):
                    combined_content += record['analysis_result'] + "\n\n"
                    sample_records.append({
                        "sequence_id": record.get('sequence_id'),
                        "file_name": record.get('file_name'),
                        "analysis_result": record.get('analysis_result', '')[:200] + "..."
                    })
            
            if not combined_content.strip():
                return {
                    "status": "no_analysis_data",
                    "message": "历史记录中没有分析结果数据",
                    "analysis_result": None
                }
            
            # 使用字段映射器分析内容结构
            analysis_result = field_mapper.analyze_content_structure(combined_content)
            
            return {
                "status": "success",
                "message": f"成功分析了 {len(records)} 条历史记录",
                "analysis_result": analysis_result,
                "sample_records": sample_records,
                "total_records": len(records)
            }
            
        except Exception as e:
            self.logger.error(f"历史数据分析失败: {str(e)}")
            return {
                "status": "error",
                "message": f"分析失败: {str(e)}",
                "analysis_result": None
            }
    
    def generate_smart_field_template(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于分析数据生成智能字段模板
        
        Args:
            analysis_data (Dict[str, Any]): 历史数据分析结果
            
        Returns:
            Dict[str, Any]: 字段模板生成结果
        """
        try:
            if analysis_data.get("status") != "success":
                return {
                    "status": "failed",
                    "message": "无法基于分析数据生成模板",
                    "template": None
                }
            
            analysis_result = analysis_data.get("analysis_result")
            if not analysis_result:
                return {
                    "status": "failed",
                    "message": "分析结果为空",
                    "template": None
                }
            
            # 使用现有的飞书字段结构，而不是生成新的字段
            existing_feishu_fields = self.feishu_client.get_video_analysis_fields()
            
            # 生成字段映射关系（将分析结果字段映射到现有飞书字段）
            field_mapping = self._create_field_mapping_to_existing_fields(analysis_result)
            
            # 创建完整的模板配置
            template_config = {
                "template_info": {
                    "name": "智能生成的飞书字段模板（兼容现有字段）",
                    "version": "1.0",
                    "created_at": datetime.now().isoformat(),
                    "based_on_records": analysis_data.get("total_records", 0),
                    "compatibility_mode": "existing_fields"
                },
                "analysis_summary": {
                    "content_type": analysis_result.get("content_type", "unknown"),
                    "structure_complexity": analysis_result.get("structure_complexity", "simple"),
                    "detected_fields_count": len(analysis_result.get("detected_fields", [])),
                    "confidence_level": self._calculate_confidence_level(analysis_result),
                    "existing_fields_count": len(existing_feishu_fields)
                },
                "feishu_fields": existing_feishu_fields,
                "field_mapping": field_mapping,
                "sample_data": analysis_data.get("sample_records", [])[:3],  # 只保留前3个样本
                "setup_instructions": self._generate_setup_instructions_for_existing_fields()
            }
            
            return {
                "status": "success",
                "message": f"成功生成包含 {len(existing_feishu_fields)} 个现有字段的兼容模板",
                "template": template_config
            }
            
        except Exception as e:
            self.logger.error(f"生成智能字段模板失败: {str(e)}")
            return {
                "status": "error",
                "message": f"模板生成失败: {str(e)}",
                "template": None
            }
    
    def _calculate_confidence_level(self, analysis_result: Dict[str, Any]) -> str:
        """
        计算模板置信度等级
        
        Args:
            analysis_result (Dict[str, Any]): 分析结果
            
        Returns:
            str: 置信度等级
        """
        detected_fields = analysis_result.get("detected_fields", [])
        
        if not detected_fields:
            return "low"
        
        # 计算平均置信度
        total_confidence = sum(field.get("confidence", 0) for field in detected_fields)
        avg_confidence = total_confidence / len(detected_fields)
        
        if avg_confidence >= 0.8:
            return "high"
        elif avg_confidence >= 0.6:
            return "medium"
        else:
            return "low"
    
    def _get_database_fields(self) -> List[str]:
        """
        获取数据库字段列表
        
        Returns:
            List[str]: 数据库字段列表
        """
        return [
            "sequence_id", "file_name", "file_path", "file_size",
            "mime_type", "analysis_prompt", "analysis_result",
            "created_at", "coze_call_id", "feishu_record_id", "sync_status"
        ]
    
    def _generate_setup_instructions(self, feishu_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成设置说明
        
        Args:
            feishu_fields (List[Dict[str, Any]]): 飞书字段列表
            
        Returns:
            Dict[str, Any]: 设置说明
        """
        return {
            "overview": "此模板基于历史记录自动生成，包含了应用程序所需的所有字段",
            "automatic_setup": {
                "description": "推荐使用自动设置功能",
                "steps": [
                    "1. 点击应用程序中的'设置表格结构'按钮",
                    "2. 系统将自动创建所有必需字段",
                    "3. 等待设置完成提示",
                    "4. 测试数据同步功能"
                ]
            },
            "manual_setup": {
                "description": "如果自动设置失败，可以手动创建字段",
                "steps": [
                    "1. 在飞书多维表格中逐个创建下列字段",
                    "2. 确保字段名称和类型完全匹配",
                    "3. 保存表格设置",
                    "4. 重新尝试数据同步"
                ]
            },
            "field_details": [
                {
                    "name": field["field_name"],
                    "type": self._get_field_type_name(field["type"]),
                    "description": field.get("description", "")
                }
                for field in feishu_fields
            ],
            "troubleshooting": {
                "common_issues": [
                    "字段名称不匹配：确保字段名称完全一致，包括中文字符",
                    "字段类型错误：检查字段类型是否正确设置",
                    "权限问题：确保飞书应用具有编辑表格的权限",
                    "网络问题：检查网络连接和飞书API访问"
                ]
            }
        }
    
    def _generate_setup_instructions_for_existing_fields(self) -> Dict[str, Any]:
        """
        为现有字段生成设置说明
        
        Returns:
            Dict[str, Any]: 设置说明
        """
        return {
            "overview": "此模板使用现有的飞书字段结构，确保与当前系统完全兼容",
            "compatibility_mode": {
                "description": "兼容模式说明",
                "benefits": [
                    "无需创建新字段，使用现有字段结构",
                    "确保与现有数据同步系统兼容",
                    "减少字段冲突和重复问题",
                    "保持数据一致性"
                ]
            },
            "field_mapping": {
                "description": "智能字段映射",
                "explanation": "系统会自动将分析结果中的字段映射到现有的飞书字段，确保数据正确同步"
            },
            "verification_steps": [
                "1. 检查飞书表格中是否已存在所需字段",
                "2. 验证字段映射关系是否正确",
                "3. 测试数据同步功能",
                "4. 确认数据显示正常"
            ],
            "troubleshooting": {
                "common_issues": [
                    "字段映射错误：检查字段映射配置是否正确",
                    "数据格式不匹配：确保分析结果格式与字段类型兼容",
                    "权限问题：确保飞书应用具有读写表格的权限",
                    "同步失败：检查网络连接和飞书API访问"
                ]
            }
        }
    
    def _create_field_mapping_to_existing_fields(self, analysis_result: Dict[str, Any]) -> Dict[str, str]:
        """
        创建分析结果字段到现有飞书字段的映射
        
        Args:
            analysis_result (Dict[str, Any]): 分析结果
            
        Returns:
            Dict[str, str]: 字段映射关系
        """
        try:
            # 获取现有飞书字段
            existing_fields = self.feishu_client.get_video_analysis_fields()
            existing_field_names = [field.get('field_name', '') for field in existing_fields]
            
            # 获取分析结果中的字段
            detected_fields = analysis_result.get("detected_fields", [])
            
            # 创建映射关系
            field_mapping = {}
            
            # 基本字段映射
            basic_mapping = {
                "sequence_id": "序号",
                "file_name": "文件名",
                "analysis_result": "分析结果",
                "created_at": "创建时间",
                "sync_status": "同步状态"
            }
            
            # 添加基本映射
            for db_field, feishu_field in basic_mapping.items():
                if feishu_field in existing_field_names:
                    field_mapping[db_field] = feishu_field
            
            # 智能映射检测到的字段
            for detected_field in detected_fields:
                field_name = detected_field.get("name", "")
                field_type = detected_field.get("type", "")
                
                # 尝试找到最匹配的现有字段
                matched_field = self._find_best_matching_field(field_name, field_type, existing_field_names)
                if matched_field:
                    field_mapping[field_name] = matched_field
            
            return field_mapping
            
        except Exception as e:
            self.logger.error(f"创建字段映射失败: {str(e)}")
            return {}
    
    def _find_best_matching_field(self, field_name: str, field_type: str, existing_fields: List[str]) -> Optional[str]:
        """
        找到最匹配的现有字段
        
        Args:
            field_name (str): 字段名
            field_type (str): 字段类型
            existing_fields (List[str]): 现有字段列表
            
        Returns:
            Optional[str]: 最匹配的字段名
        """
        try:
            # 直接匹配
            if field_name in existing_fields:
                return field_name
            
            # 模糊匹配
            field_name_lower = field_name.lower()
            for existing_field in existing_fields:
                if field_name_lower in existing_field.lower() or existing_field.lower() in field_name_lower:
                    return existing_field
            
            # 基于类型的匹配
            type_mapping = {
                "text": ["标题", "内容", "描述", "备注"],
                "number": ["数量", "评分", "时长"],
                "date": ["时间", "日期"],
                "url": ["链接", "地址"]
            }
            
            if field_type in type_mapping:
                for keyword in type_mapping[field_type]:
                    for existing_field in existing_fields:
                        if keyword in existing_field:
                            return existing_field
            
            return None
        
        except Exception as e:
            self.logger.error(f"字段匹配失败: {str(e)}")
            return None
     
    def _create_field_mapping_from_parsed_content(self, parsed_content: Dict[str, Any]) -> Dict[str, str]:
         """
         从解析的内容创建字段映射
         
         Args:
             parsed_content (Dict[str, Any]): 解析后的内容
             
         Returns:
             Dict[str, str]: 字段映射关系
         """
         try:
             # 获取现有飞书字段
             existing_fields = self.feishu_client.get_video_analysis_fields()
             existing_field_names = [field.get('field_name', '') for field in existing_fields]
             
             field_mapping = {}
             
             # 基本映射
             basic_mapping = self._create_basic_field_mapping()
             field_mapping.update(basic_mapping)
             
             # 智能映射解析出的字段
             for key, value in parsed_content.items():
                 # 尝试找到最匹配的现有字段
                 matched_field = self._find_best_matching_field(key, "text", existing_field_names)
                 if matched_field:
                     field_mapping[key] = matched_field
                 else:
                     # 如果没有找到匹配的字段，映射到"分析结果"字段
                     field_mapping[key] = "分析结果"
             
             return field_mapping
             
         except Exception as e:
             self.logger.error(f"创建字段映射失败: {str(e)}")
             return self._create_basic_field_mapping()
     
    def _create_basic_field_mapping(self) -> Dict[str, str]:
         """
         创建基本的字段映射关系
         
         Returns:
             Dict[str, str]: 基本字段映射
         """
         return {
             "sequence_id": "序列ID",
             "file_name": "文件名称",
             "file_path": "文件路径",
             "file_size": "文件大小",
             "mime_type": "文件格式",
             "analysis_prompt": "分析提示词",
             "analysis_result": "分析结果",
             "created_at": "创建时间",
             "coze_call_id": "扣子调用ID"
         }
     
    def _get_field_type_name(self, field_type: int) -> str:
        """
        获取字段类型名称
        
        Args:
            field_type (int): 字段类型编号
            
        Returns:
            str: 字段类型名称
        """
        type_mapping = {
            1: "单行文本",
            2: "数字",
            3: "单选",
            4: "多选",
            5: "日期时间",
            7: "复选框",
            11: "人员",
            13: "电话号码",
            15: "超链接",
            17: "附件",
            20: "条码",
            21: "进度",
            22: "货币",
            23: "评分",
            1001: "地理位置"
        }
        return type_mapping.get(field_type, "未知类型")
    
    def save_template_to_file(self, template_config: Dict[str, Any], filename: str = None) -> str:
        """
        保存模板配置到文件
        
        Args:
            template_config (Dict[str, Any]): 模板配置
            filename (str, optional): 文件名
            
        Returns:
            str: 保存的文件路径
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"smart_field_template_{timestamp}.json"
            
            file_path = os.path.join(self.template_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template_config, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"模板已保存到: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"保存模板文件失败: {str(e)}")
            raise
    
    def auto_setup_feishu_fields(self, template_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        自动设置飞书字段
        
        Args:
            template_config (Dict[str, Any]): 模板配置
            
        Returns:
            Dict[str, Any]: 设置结果
        """
        try:
            feishu_fields = template_config.get("feishu_fields", [])
            
            if not feishu_fields:
                return {
                    "status": "failed",
                    "message": "模板中没有字段定义",
                    "created_fields": []
                }
            
            # 检查飞书表格是否存在
            if not hasattr(self.feishu_client, 'app_token') or not self.feishu_client.app_token:
                return {
                    "status": "failed",
                    "message": "飞书表格未配置或不存在",
                    "created_fields": []
                }
            
            # 创建字段
            created_fields = []
            failed_fields = []
            
            for field_config in feishu_fields:
                try:
                    # 调用飞书客户端创建字段
                    success = self.feishu_client._create_single_field(
                        field_config["field_name"],
                        field_config["type"],
                        field_config.get("property", {})
                    )
                    
                    if success:
                        created_fields.append(field_config["field_name"])
                        self.logger.info(f"成功创建字段: {field_config['field_name']}")
                    else:
                        failed_fields.append(field_config["field_name"])
                        self.logger.warning(f"创建字段失败: {field_config['field_name']}")
                        
                except Exception as e:
                    failed_fields.append(field_config["field_name"])
                    self.logger.error(f"创建字段 {field_config['field_name']} 时出错: {str(e)}")
            
            # 更新字段映射配置
            if created_fields:
                self._update_field_mapping(template_config.get("field_mapping", {}))
            
            status = "success" if created_fields and not failed_fields else "partial" if created_fields else "failed"
            
            return {
                "status": status,
                "message": f"成功创建 {len(created_fields)} 个字段，失败 {len(failed_fields)} 个字段",
                "created_fields": created_fields,
                "failed_fields": failed_fields,
                "total_fields": len(feishu_fields)
            }
            
        except Exception as e:
            self.logger.error(f"自动设置飞书字段失败: {str(e)}")
            return {
                "status": "error",
                "message": f"设置过程中发生错误: {str(e)}",
                "created_fields": []
            }
    
    def _update_field_mapping(self, field_mapping: Dict[str, str]):
        """
        更新字段映射配置
        
        Args:
            field_mapping (Dict[str, str]): 字段映射配置
        """
        try:
            # 这里可以将映射配置保存到配置文件或数据库
            # 暂时只记录日志
            self.logger.info(f"字段映射配置已更新: {field_mapping}")
            
        except Exception as e:
            self.logger.error(f"更新字段映射配置失败: {str(e)}")
    
    def _get_field_type_summary(self, feishu_fields: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        获取字段类型统计摘要
        
        Args:
            feishu_fields (List[Dict[str, Any]]): 飞书字段列表
            
        Returns:
            Dict[str, int]: 字段类型统计
        """
        type_summary = {}
        for field in feishu_fields:
            field_type = field.get("type", 1)
            type_name = self._get_field_type_name(field_type)
            type_summary[type_name] = type_summary.get(type_name, 0) + 1
        return type_summary
    
    def run_smart_setup(self, save_template: bool = True) -> Dict[str, Any]:
        """
        运行智能字段模板生成流程
        
        Args:
            save_template (bool): 是否保存模板文件
            
        Returns:
            Dict[str, Any]: 模板生成结果
        """
        try:
            self.logger.info("开始智能字段模板生成流程")
            
            # 1. 分析历史数据
            self.logger.info("正在分析历史数据...")
            analysis_data = self.analyze_historical_data()
            
            if analysis_data.get("status") != "success":
                return {
                    "status": "failed",
                    "step": "analysis",
                    "message": analysis_data.get("message", "历史数据分析失败"),
                    "details": analysis_data
                }
            
            # 2. 生成字段模板
            self.logger.info("正在生成字段模板...")
            template_result = self.generate_smart_field_template(analysis_data)
            
            if template_result.get("status") != "success":
                return {
                    "status": "failed",
                    "step": "template_generation",
                    "message": template_result.get("message", "模板生成失败"),
                    "details": template_result
                }
            
            template_config = template_result["template"]
            
            # 3. 保存模板文件
            template_file_path = None
            if save_template:
                try:
                    template_file_path = self.save_template_to_file(template_config)
                    self.logger.info(f"模板已保存到: {template_file_path}")
                except Exception as e:
                    self.logger.warning(f"保存模板文件失败: {str(e)}")
                    return {
                        "status": "failed",
                        "step": "template_save",
                        "message": f"模板文件保存失败: {str(e)}",
                        "details": {"error": str(e)}
                    }
            
            # 4. 生成用户操作指南
            setup_instructions = self._generate_setup_instructions(template_config.get("feishu_fields", []))
            
            return {
                "status": "success",
                "step": "completed",
                "message": "智能字段模板生成完成",
                "analysis_summary": {
                    "analyzed_records": analysis_data.get("total_records", 0),
                    "detected_fields": len(analysis_data.get("analysis_result", {}).get("detected_fields", [])),
                    "confidence_level": template_config.get("analysis_summary", {}).get("confidence_level", "unknown")
                },
                "template_summary": {
                    "total_fields": len(template_config.get("feishu_fields", [])),
                    "field_types": self._get_field_type_summary(template_config.get("feishu_fields", [])),
                    "template_file": template_file_path
                },
                "template_config": template_config,
                "setup_instructions": setup_instructions,
                "next_steps": [
                    "根据生成的模板手动创建飞书字段",
                    "测试数据同步功能",
                    "根据需要调整字段配置"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"智能字段设置失败: {str(e)}")
            return {
                "status": "error",
                "step": "unknown",
                "message": f"设置失败: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def generate_template_from_single_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于单条记录生成字段模板（使用现有飞书字段结构）
        
        Args:
            record (Dict[str, Any]): 历史记录数据
            
        Returns:
            Dict[str, Any]: 模板生成结果
        """
        try:
            if not record:
                return {
                    "status": "failed",
                    "message": "记录数据为空",
                    "template": None
                }
            
            analysis_result = record.get('analysis_result')
            if not analysis_result:
                return {
                    "status": "failed",
                    "message": "记录中没有分析结果数据",
                    "template": None
                }
            
            # 使用现有的飞书字段结构
            existing_feishu_fields = self.feishu_client.get_video_analysis_fields()
            
            # 解析分析结果
            if isinstance(analysis_result, str):
                try:
                    analysis_data = json.loads(analysis_result)
                except json.JSONDecodeError:
                    # 如果不是JSON格式，尝试解析为键值对格式
                    analysis_data = self._parse_key_value_format(analysis_result)
            else:
                analysis_data = analysis_result
            
            # 分析单条记录的内容结构
            content_analysis = field_mapper.analyze_content_structure(analysis_data)
            
            # 创建到现有字段的映射
            field_mapping = self._create_field_mapping_to_existing_fields(content_analysis)
            
            # 创建模板配置
            template_config = {
                "template_info": {
                    "name": f"基于记录 {record.get('sequence_id', 'unknown')} 生成的字段模板（兼容现有字段）",
                    "version": "1.0",
                    "created_at": datetime.now().isoformat(),
                    "based_on_record": record.get('sequence_id', 'unknown'),
                    "source_file": record.get('file_name', 'unknown'),
                    "compatibility_mode": "existing_fields"
                },
                "analysis_summary": {
                    "content_type": content_analysis.get("content_type", "unknown"),
                    "structure_complexity": content_analysis.get("structure_complexity", "simple"),
                    "detected_fields_count": len(content_analysis.get("detected_fields", [])),
                    "confidence_level": self._calculate_confidence_level(content_analysis),
                    "existing_fields_count": len(existing_feishu_fields)
                },
                "feishu_fields": existing_feishu_fields,
                "field_mapping": field_mapping,
                "source_record": {
                    "sequence_id": record.get('sequence_id'),
                    "file_name": record.get('file_name'),
                    "created_at": record.get('created_at'),
                    "analysis_preview": str(analysis_result)[:300] + "..." if len(str(analysis_result)) > 300 else str(analysis_result)
                },
                "setup_instructions": self._generate_setup_instructions_for_existing_fields()
            }
            
            # 保存模板文件
            template_file_path = self.save_template_to_file(
                template_config, 
                f"single_record_template_{record.get('sequence_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            return {
                "status": "success",
                "message": f"成功基于记录 {record.get('sequence_id', 'unknown')} 生成兼容现有 {len(existing_feishu_fields)} 个字段的模板",
                "template": template_config,
                "template_file": template_file_path,
                "template_summary": {
                    "total_fields": len(existing_feishu_fields),
                    "field_types": self._get_field_type_summary(existing_feishu_fields)
                }
            }
            
        except Exception as e:
            self.logger.error(f"基于单条记录生成模板失败: {str(e)}")
            return {
                "status": "error",
                "message": f"模板生成失败: {str(e)}",
                "template": None
            }
    
    def _parse_key_value_format(self, content: str) -> Dict[str, Any]:
        """
        解析键值对格式的内容
        
        Args:
            content (str): 键值对格式的内容
            
        Returns:
            Dict[str, Any]: 解析后的字典数据
        """
        try:
            parsed_data = {}
            lines = content.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if ':' in line:
                    # 分割键值对
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        parsed_data[key] = value
            
            return parsed_data
            
        except Exception as e:
            self.logger.error(f"解析键值对格式失败: {str(e)}")
            return {"content": content}
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析结果解析器
用于从analysis_result字段中提取结构化数据
"""

import re
import json
import logging
from typing import Dict, Any, Optional

class AnalysisResultParser:
    """
    分析结果解析器类
    """
    
    def __init__(self):
        """
        初始化解析器
        """
        self.logger = logging.getLogger(__name__)
    
    def parse_analysis_result(self, analysis_result: str) -> Dict[str, Any]:
        """
        解析analysis_result字段，提取结构化数据
        
        Args:
            analysis_result (str): 原始分析结果文本
            
        Returns:
            Dict[str, Any]: 解析后的结构化数据
        """
        if not analysis_result or not isinstance(analysis_result, str):
            return {}
        
        # 尝试多种解析方法
        parsed_data = {}
        
        # 方法1: 尝试解析JSON块
        json_data = self._extract_json_block(analysis_result)
        if json_data:
            parsed_data.update(json_data)
        
        # 方法2: 使用正则表达式提取关键信息
        regex_data = self._extract_with_regex(analysis_result)
        if regex_data:
            parsed_data.update(regex_data)
        
        # 方法3: 如果没有提取到任何数据，将整个文本作为摘要
        if not parsed_data:
            parsed_data = {
                'summary': analysis_result[:500],  # 限制长度
                'detailed_description': analysis_result
            }
        
        return parsed_data
    
    def _extract_json_block(self, text: str) -> Optional[Dict[str, Any]]:
        """
        从文本中提取JSON块
        
        Args:
            text (str): 输入文本
            
        Returns:
            Optional[Dict[str, Any]]: 解析的JSON数据，如果失败则返回None
        """
        try:
            # 查找```json...```块
            json_match = re.search(r'```json\s*\n(.*?)\n```', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
                return json.loads(json_str)
            
            # 查找{...}块
            brace_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if brace_match:
                json_str = brace_match.group(0)
                return json.loads(json_str)
                
        except json.JSONDecodeError as e:
            self.logger.debug(f"JSON解析失败: {e}")
        
        return None
    
    def _extract_with_regex(self, text: str) -> Dict[str, Any]:
        """
        使用正则表达式从文本中提取关键信息
        
        Args:
            text (str): 输入文本
            
        Returns:
            Dict[str, Any]: 提取的数据
        """
        extracted_data = {}
        
        # 提取视频序列号
        sequence_patterns = [
            r'video serial number[:\s]*([\w\d]+)',
            r'序列号[:\s]*([\w\d]+)',
            r'编号[:\s]*([\w\d]+)'
        ]
        
        for pattern in sequence_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_data['sequence_id'] = match.group(1)
                break
        
        # 提取视频内容摘要
        summary_patterns = [
            r'videgcontedtSumary[:\s]*([^\n]+)',
            r'视频内容摘要[:\s]*([^\n]+)',
            r'内容摘要[:\s]*([^\n]+)',
            r'摘要[:\s]*([^\n]+)'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_data['summary'] = match.group(1).strip()
                break
        
        # 提取详细描述（如果没有找到摘要，使用前500字符作为摘要）
        if 'summary' not in extracted_data:
            # 取文本的前几句作为摘要
            sentences = re.split(r'[.。!！?？]', text)
            if sentences:
                summary = ''.join(sentences[:2]).strip()
                if len(summary) > 10:  # 确保摘要有意义
                    extracted_data['summary'] = summary[:200]
        
        # 将整个文本作为详细描述
        extracted_data['detailed_description'] = text
        
        # 尝试提取关键词（简单的关键词提取）
        keywords = self._extract_keywords(text)
        if keywords:
            extracted_data['keywords'] = ', '.join(keywords)
        
        # 尝试提取主要人物
        characters = self._extract_characters(text)
        if characters:
            extracted_data['main_characters'] = ', '.join(characters)
        
        return extracted_data
    
    def _extract_keywords(self, text: str) -> list:
        """
        从文本中提取关键词
        
        Args:
            text (str): 输入文本
            
        Returns:
            list: 关键词列表
        """
        keywords = []
        
        # 常见的视频相关关键词
        video_keywords = [
            '视频', '画面', '镜头', '场景', '背景', '前景',
            '人物', '角色', '主角', '配角',
            '动作', '行为', '表情', '姿态',
            '音乐', '声音', '对话', '旁白',
            '色彩', '光线', '明暗', '构图',
            '特效', '剪辑', '转场', '字幕'
        ]
        
        for keyword in video_keywords:
            if keyword in text:
                keywords.append(keyword)
        
        return keywords[:5]  # 限制关键词数量
    
    def _extract_characters(self, text: str) -> list:
        """
        从文本中提取主要人物
        
        Args:
            text (str): 输入文本
            
        Returns:
            list: 人物列表
        """
        characters = []
        
        # 查找人物相关的描述
        character_patterns = [
            r'(男性|女性|男人|女人|男孩|女孩|先生|女士|小姐)',
            r'(医生|护士|老师|学生|工人|司机|警察|军人)',
            r'(专业人士|工作人员|服务员|销售员|经理|主管)',
            r'身穿([^的]+)的(男性|女性|人)',
            r'(一位|一个|几位|多位)([^，。]+)(男性|女性|人)'
        ]
        
        for pattern in character_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    character = ''.join(match).strip()
                else:
                    character = match.strip()
                
                if character and len(character) < 20:  # 避免过长的描述
                    characters.append(character)
        
        return list(set(characters))[:3]  # 去重并限制数量

# 创建全局实例
analysis_parser = AnalysisResultParser()
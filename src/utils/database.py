#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模块
用于存储和管理视频分析结果
"""

import sqlite3
import os
import uuid
import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class VideoAnalysisDB:
    """
    视频分析结果数据库管理类
    """
    
    def __init__(self, db_path: str = None):
        """
        初始化数据库连接
        
        Args:
            db_path (str, optional): 数据库文件路径，默认为项目根目录下的data.db
        """
        if db_path is None:
            # 获取项目根目录
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "data.db"
        
        self.db_path = str(db_path)
        self._init_database()
    
    def _init_database(self) -> None:
        """
        初始化数据库表结构
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建视频分析结果表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS video_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sequence_id TEXT UNIQUE NOT NULL,
                    file_path TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_size INTEGER,
                    mime_type TEXT,
                    analysis_prompt TEXT NOT NULL,
                    analysis_result TEXT NOT NULL,
                    gemini_file_uri TEXT,
                    gemini_file_name TEXT,
                    oss_url TEXT,
                    oss_file_name TEXT,
                    feishu_record_id TEXT,
                    coze_call_id TEXT,
                    sync_status INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 添加飞书相关字段（如果不存在）
            self._add_feishu_columns(cursor)
            
            # 添加OSS相关字段（如果不存在）
            self._add_oss_columns(cursor)
            
            # 创建快速提示模板表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quick_prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    prompt_text TEXT NOT NULL,
                    description TEXT,
                    is_default BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 插入默认快速提示
            self._insert_default_prompts(cursor)
            
            conn.commit()
    
    def _insert_default_prompts(self, cursor) -> None:
        """
        插入默认的快速提示模板（仅在表为空时插入）
        
        Args:
            cursor: 数据库游标
        """
        # 检查表中是否已有数据
        cursor.execute("SELECT COUNT(*) FROM quick_prompts")
        count = cursor.fetchone()[0]
        
        # 只有在表为空时才插入默认提示词
        if count == 0:
            default_prompts = [
                {
                    'name': '视频摘要',
                    'prompt_text': '请分析这个视频的主要内容，包括：1. 视频主题和目的 2. 关键场景和动作 3. 重要对话或文字信息 4. 整体风格和特点',
                    'description': '生成视频的详细摘要分析',
                    'is_default': 1
                },
                {
                    'name': '内容分类',
                    'prompt_text': '请对这个视频进行分类，包括：1. 内容类型（教育、娱乐、新闻等） 2. 目标受众 3. 主要话题标签 4. 适用场景',
                    'description': '对视频内容进行分类和标签化',
                    'is_default': 1
                },
                {
                    'name': '关键信息提取',
                    'prompt_text': '请提取视频中的关键信息：1. 重要人物和角色 2. 关键时间点和事件 3. 重要数据和统计信息 4. 可操作的建议或指导',
                    'description': '提取视频中的核心信息点',
                    'is_default': 1
                },
                {
                    'name': '情感分析',
                    'prompt_text': '请分析视频的情感色彩：1. 整体情感倾向（积极、消极、中性） 2. 情感变化过程 3. 情感表达方式 4. 观众可能的情感反应',
                    'description': '分析视频的情感表达和影响',
                    'is_default': 1
                },
                {
                    'name': '技术质量评估',
                    'prompt_text': '请评估视频的技术质量：1. 画面清晰度和稳定性 2. 音频质量 3. 剪辑和制作水平 4. 技术改进建议',
                    'description': '评估视频的技术制作质量',
                    'is_default': 1
                }
            ]
            
            for prompt in default_prompts:
                cursor.execute("""
                    INSERT INTO quick_prompts (name, prompt_text, description, is_default)
                    VALUES (?, ?, ?, ?)
                """, (prompt['name'], prompt['prompt_text'], prompt['description'], prompt['is_default']))
    
    def _add_feishu_columns(self, cursor) -> None:
        """
        添加飞书相关字段（如果不存在）
        
        Args:
            cursor: 数据库游标
        """
        try:
            # 检查字段是否存在，如果不存在则添加
            cursor.execute("PRAGMA table_info(video_analysis)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'feishu_record_id' not in columns:
                cursor.execute("ALTER TABLE video_analysis ADD COLUMN feishu_record_id TEXT")
            
            if 'coze_call_id' not in columns:
                cursor.execute("ALTER TABLE video_analysis ADD COLUMN coze_call_id TEXT")
            
            if 'sync_status' not in columns:
                cursor.execute("ALTER TABLE video_analysis ADD COLUMN sync_status INTEGER DEFAULT 0")
            
            # 添加解析后的字段
            if 'video_content_summary' not in columns:
                cursor.execute("ALTER TABLE video_analysis ADD COLUMN video_content_summary TEXT")
            
            if 'detailed_content_description' not in columns:
                cursor.execute("ALTER TABLE video_analysis ADD COLUMN detailed_content_description TEXT")
            
            if 'keywords_tags' not in columns:
                cursor.execute("ALTER TABLE video_analysis ADD COLUMN keywords_tags TEXT")
            
            if 'main_characters_objects' not in columns:
                cursor.execute("ALTER TABLE video_analysis ADD COLUMN main_characters_objects TEXT")
            
            # 添加飞书电子表格相关字段
            if 'feishu_spreadsheet_row' not in columns:
                cursor.execute("ALTER TABLE video_analysis ADD COLUMN feishu_spreadsheet_row INTEGER")
            
            if 'spreadsheet_sync_status' not in columns:
                cursor.execute("ALTER TABLE video_analysis ADD COLUMN spreadsheet_sync_status INTEGER DEFAULT 0")
            
            if 'spreadsheet_sync_time' not in columns:
                cursor.execute("ALTER TABLE video_analysis ADD COLUMN spreadsheet_sync_time TIMESTAMP")
            
            # 添加飞书云文档相关字段
            if 'doc_sync_status' not in columns:
                cursor.execute("ALTER TABLE video_analysis ADD COLUMN doc_sync_status INTEGER DEFAULT 0")
            
            if 'doc_sync_time' not in columns:
                cursor.execute("ALTER TABLE video_analysis ADD COLUMN doc_sync_time TIMESTAMP")
                
        except Exception as e:
            # 如果字段已存在，忽略错误
            pass
    
    def _add_oss_columns(self, cursor) -> None:
        """
        添加OSS相关字段（如果不存在）
        
        Args:
            cursor: 数据库游标
        """
        try:
            # 检查字段是否存在，如果不存在则添加
            cursor.execute("PRAGMA table_info(video_analysis)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'oss_url' not in columns:
                cursor.execute("ALTER TABLE video_analysis ADD COLUMN oss_url TEXT")
            
            if 'oss_file_name' not in columns:
                cursor.execute("ALTER TABLE video_analysis ADD COLUMN oss_file_name TEXT")
                
        except Exception as e:
            # 如果字段已存在，忽略错误
            pass
    
    def generate_sequence_id(self) -> str:
        """
        生成22位唯一序列号
        格式：YYYYMMDDHHMMSS + 8位随机字符
        
        Returns:
            str: 22位序列号
        """
        # 获取当前时间戳（14位）
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        # 生成8位随机字符
        random_part = str(uuid.uuid4()).replace('-', '')[:8].upper()
        
        # 组合成22位序列号
        sequence_id = timestamp + random_part
        
        return sequence_id
    
    def save_analysis_result(self, file_path: str, file_name: str, file_size: int,
                           mime_type: str, analysis_prompt: str, analysis_result: str,
                           gemini_file_uri: str = None, gemini_file_name: str = None,
                           oss_url: str = None, oss_file_name: str = None,
                           feishu_record_id: str = None, coze_call_id: str = None) -> str:
        """
        保存视频分析结果
        
        Args:
            file_path (str): 文件路径
            file_name (str): 文件名
            file_size (int): 文件大小
            mime_type (str): 文件类型
            analysis_prompt (str): 分析提示
            analysis_result (str): 分析结果
            gemini_file_uri (str, optional): Gemini文件URI
            gemini_file_name (str, optional): Gemini文件名
            oss_url (str, optional): OSS文件访问链接
            oss_file_name (str, optional): OSS文件名
            feishu_record_id (str, optional): 飞书记录ID
            coze_call_id (str, optional): 扣子调用ID
            
        Returns:
            str: 生成的序列号
        """
        sequence_id = self.generate_sequence_id()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO video_analysis (
                    sequence_id, file_path, file_name, file_size, mime_type,
                    analysis_prompt, analysis_result, gemini_file_uri, gemini_file_name,
                    oss_url, oss_file_name, feishu_record_id, coze_call_id, sync_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sequence_id, file_path, file_name, file_size, mime_type,
                analysis_prompt, analysis_result, gemini_file_uri, gemini_file_name,
                oss_url, oss_file_name, feishu_record_id, coze_call_id, 1 if feishu_record_id else 0
            ))
            
            conn.commit()
        
        return sequence_id
    
    def get_analysis_by_sequence_id(self, sequence_id: str) -> Optional[Dict[str, Any]]:
        """
        根据序列号获取分析结果
        
        Args:
            sequence_id (str): 序列号
            
        Returns:
            Optional[Dict[str, Any]]: 分析结果数据，如果不存在则返回None
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM video_analysis WHERE sequence_id = ?
            """, (sequence_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_all_analysis_results(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取所有分析结果
        
        Args:
            limit (int): 限制返回数量
            offset (int): 偏移量
            
        Returns:
            List[Dict[str, Any]]: 分析结果列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM video_analysis 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def search_analysis_results(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索分析结果
        
        Args:
            keyword (str): 搜索关键词
            
        Returns:
            List[Dict[str, Any]]: 匹配的分析结果列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM video_analysis 
                WHERE file_name LIKE ? OR analysis_prompt LIKE ? OR analysis_result LIKE ?
                ORDER BY created_at DESC
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_recent_records(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的分析记录
        
        Args:
            limit (int): 限制返回数量，默认10条
            
        Returns:
            List[Dict[str, Any]]: 最近的分析记录列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM video_analysis 
                WHERE analysis_result IS NOT NULL AND analysis_result != ''
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_all_history_records(self) -> List[Dict[str, Any]]:
        """
        获取所有历史分析记录
        
        Returns:
            List[Dict[str, Any]]: 所有历史分析记录列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM video_analysis 
                WHERE analysis_result IS NOT NULL AND analysis_result != ''
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def delete_analysis_result(self, sequence_id: str) -> bool:
        """
        删除分析结果
        
        Args:
            sequence_id (str): 序列号
            
        Returns:
            bool: 删除是否成功
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM video_analysis WHERE sequence_id = ?
            """, (sequence_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_multiple_analysis_results(self, sequence_ids: List[str]) -> Dict[str, int]:
        """
        批量删除分析结果
        
        Args:
            sequence_ids (List[str]): 序列号列表
            
        Returns:
            Dict[str, int]: 删除结果统计 {'deleted': 删除成功数量, 'failed': 删除失败数量}
        """
        deleted_count = 0
        failed_count = 0
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for sequence_id in sequence_ids:
                try:
                    cursor.execute("""
                        DELETE FROM video_analysis WHERE sequence_id = ?
                    """, (sequence_id,))
                    
                    if cursor.rowcount > 0:
                        deleted_count += 1
                    else:
                        failed_count += 1
                        
                except Exception:
                    failed_count += 1
            
            conn.commit()
            
        return {'deleted': deleted_count, 'failed': failed_count}
    
    def update_doc_sync_status(self, sequence_id: str, sync_status: int) -> bool:
        """
        更新云文档同步状态
        
        Args:
            sequence_id (str): 序列号
            sync_status (int): 同步状态 (0: 未同步, 1: 已同步, 2: 同步失败)
            
        Returns:
            bool: 更新是否成功
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE video_analysis 
                SET doc_sync_status = ?, doc_sync_time = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE sequence_id = ?
            """, (sync_status, sequence_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_all_analysis_results(self) -> Dict[str, int]:
        """
        删除所有分析结果
        
        Returns:
            Dict[str, int]: 删除结果统计 {'deleted': 删除成功数量}
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 先获取总数
            cursor.execute("SELECT COUNT(*) FROM video_analysis")
            total_count = cursor.fetchone()[0]
            
            # 删除所有记录
            cursor.execute("DELETE FROM video_analysis")
            
            conn.commit()
            
        return {'deleted': total_count}
    
    def update_feishu_record_id(self, sequence_id: str, feishu_record_id: str) -> bool:
        """
        更新飞书记录ID
        
        Args:
            sequence_id (str): 序列号
            feishu_record_id (str): 飞书记录ID，None表示清除同步状态
            
        Returns:
            bool: 更新是否成功
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 根据feishu_record_id是否为None来设置sync_status
            sync_status = 1 if feishu_record_id else 0
            
            cursor.execute("""
                UPDATE video_analysis 
                SET feishu_record_id = ?, sync_status = ? 
                WHERE sequence_id = ?
            """, (feishu_record_id, sync_status, sequence_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_total_analysis_count(self) -> int:
        """
        获取分析记录总数
        
        Returns:
            int: 记录总数
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM video_analysis
            """)
            
            result = cursor.fetchone()
            return result[0] if result else 0
    
    def get_synced_records_count(self) -> int:
        """
        获取已同步到飞书的记录数
        
        Returns:
            int: 已同步记录数
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM video_analysis 
                WHERE feishu_record_id IS NOT NULL AND feishu_record_id != ''
            """)
            
            result = cursor.fetchone()
            return result[0] if result else 0
    
    # 快速提示相关方法
    def get_all_quick_prompts(self) -> List[Dict[str, Any]]:
        """
        获取所有快速提示
        
        Returns:
            List[Dict[str, Any]]: 快速提示列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM quick_prompts ORDER BY is_default DESC, name ASC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def add_quick_prompt(self, name: str, prompt_text: str, description: str = None) -> bool:
        """
        添加快速提示
        
        Args:
            name (str): 提示名称
            prompt_text (str): 提示内容
            description (str, optional): 描述
            
        Returns:
            bool: 添加是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO quick_prompts (name, prompt_text, description)
                    VALUES (?, ?, ?)
                """, (name, prompt_text, description))
                
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False  # 名称已存在
    
    def update_quick_prompt(self, prompt_id: int, name: str, prompt_text: str, description: str = None) -> bool:
        """
        更新快速提示
        
        Args:
            prompt_id (int): 提示ID
            name (str): 提示名称
            prompt_text (str): 提示内容
            description (str, optional): 描述
            
        Returns:
            bool: 更新是否成功
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE quick_prompts 
                SET name = ?, prompt_text = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (name, prompt_text, description, prompt_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_quick_prompt(self, prompt_id: int) -> bool:
        """
        删除快速提示（现在可以删除默认提示）
        
        Args:
            prompt_id (int): 提示ID
            
        Returns:
            bool: 删除是否成功
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM quick_prompts WHERE id = ?
            """, (prompt_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_quick_prompt_by_id(self, prompt_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取快速提示
        
        Args:
            prompt_id (int): 提示ID
            
        Returns:
            Optional[Dict[str, Any]]: 快速提示数据，如果不存在则返回None
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM quick_prompts WHERE id = ?
            """, (prompt_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None
    
    def update_feishu_sync_info(self, sequence_id: str, feishu_record_id: str = None, 
                               coze_call_id: str = None, sync_status: int = None) -> bool:
        """
        更新飞书同步信息
        
        Args:
            sequence_id (str): 序列号
            feishu_record_id (str, optional): 飞书记录ID
            coze_call_id (str, optional): 扣子调用ID
            sync_status (int, optional): 同步状态 (0: 未同步, 1: 已同步, 2: 同步失败)
            
        Returns:
            bool: 更新是否成功
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 构建动态更新语句
            update_fields = []
            values = []
            
            if feishu_record_id is not None:
                update_fields.append("feishu_record_id = ?")
                values.append(feishu_record_id)
            
            if coze_call_id is not None:
                update_fields.append("coze_call_id = ?")
                values.append(coze_call_id)
            
            if sync_status is not None:
                update_fields.append("sync_status = ?")
                values.append(sync_status)
            
            if not update_fields:
                return False
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(sequence_id)
            
            sql = f"UPDATE video_analysis SET {', '.join(update_fields)} WHERE sequence_id = ?"
            cursor.execute(sql, values)
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_unsynced_records(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取未同步到飞书的记录
        
        Args:
            limit (int): 限制返回数量
            
        Returns:
            List[Dict[str, Any]]: 未同步的记录列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM video_analysis 
                WHERE sync_status = 0 OR sync_status IS NULL
                ORDER BY created_at ASC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_sync_statistics(self) -> Dict[str, int]:
        """
        获取同步统计信息
        
        Returns:
            Dict[str, int]: 包含各种同步状态的统计数据
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN sync_status = 0 OR sync_status IS NULL THEN 1 ELSE 0 END) as unsynced,
                    SUM(CASE WHEN sync_status = 1 THEN 1 ELSE 0 END) as synced,
                    SUM(CASE WHEN sync_status = 2 THEN 1 ELSE 0 END) as failed
                FROM video_analysis
            """)
            
            row = cursor.fetchone()
            return {
                'total': row[0] or 0,
                'unsynced': row[1] or 0,
                'synced': row[2] or 0,
                'failed': row[3] or 0
            }
    
    def get_records_by_sync_status(self, sync_status: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        根据同步状态获取记录
        
        Args:
            sync_status (int): 同步状态 (0: 未同步, 1: 已同步, 2: 同步失败)
            limit (int): 限制返回数量
            
        Returns:
            List[Dict[str, Any]]: 指定同步状态的记录列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM video_analysis 
                WHERE sync_status = ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (sync_status, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_analysis_fields(self, sequence_id: str, fields: Dict[str, str]) -> bool:
        """
        更新分析结果的字段数据
        
        Args:
            sequence_id (str): 序列号
            fields (Dict[str, str]): 要更新的字段数据
            
        Returns:
            bool: 更新是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 构建动态更新语句
                set_clauses = []
                values = []
                
                for field_name, field_value in fields.items():
                    set_clauses.append(f"{field_name} = ?")
                    values.append(field_value)
                
                # 添加更新时间
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                # 不需要添加值，因为使用了CURRENT_TIMESTAMP
                
                # 添加序列号作为WHERE条件
                values.append(sequence_id)
                
                sql = f"""
                    UPDATE video_analysis 
                    SET {', '.join(set_clauses)}
                    WHERE sequence_id = ?
                """
                
                cursor.execute(sql, values)
                
                # 检查是否有记录被更新
                if cursor.rowcount > 0:
                    return True
                else:
                    return False
                    
        except Exception as e:
            print(f"更新分析字段失败: {str(e)}")
            return False
    
    def update_feishu_spreadsheet_row(self, sequence_id: str, row_number: int) -> bool:
        """
        更新记录的飞书电子表格行号
        
        Args:
            sequence_id (str): 序列号
            row_number (int): 电子表格行号
            
        Returns:
            bool: 更新是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE video_analysis 
                    SET feishu_spreadsheet_row = ?, 
                        spreadsheet_sync_status = 1,
                        spreadsheet_sync_time = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE sequence_id = ?
                """, (row_number, sequence_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"更新飞书电子表格行号失败: {str(e)}")
            return False
    
    def get_unsynced_spreadsheet_records(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取未同步到飞书电子表格的记录
        
        Args:
            limit (int): 限制返回数量
            
        Returns:
            List[Dict[str, Any]]: 未同步的记录列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM video_analysis 
                WHERE spreadsheet_sync_status = 0 OR spreadsheet_sync_status IS NULL
                ORDER BY created_at ASC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_synced_spreadsheet_records_count(self) -> int:
        """
        获取已同步到飞书电子表格的记录数量
        
        Returns:
            int: 已同步的记录数量
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM video_analysis 
                WHERE spreadsheet_sync_status = 1
            """)
            
            result = cursor.fetchone()
            return result[0] if result else 0
    
    def get_total_records_count(self) -> int:
        """
        获取总记录数量
        
        Returns:
            int: 总记录数量
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM video_analysis")
            
            result = cursor.fetchone()
            return result[0] if result else 0
    
    def get_analysis_by_sequence_id(self, sequence_id: str) -> Optional[Dict[str, Any]]:
        """
        根据序列号获取分析记录
        
        Args:
            sequence_id (str): 序列号
            
        Returns:
            Optional[Dict[str, Any]]: 记录数据，如果不存在则返回None
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM video_analysis 
                WHERE sequence_id = ?
            """, (sequence_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def close(self) -> None:
        """
        关闭数据库连接（SQLite会自动管理连接，此方法为兼容性保留）
        """
        pass

# 创建全局数据库实例
db = VideoAnalysisDB()
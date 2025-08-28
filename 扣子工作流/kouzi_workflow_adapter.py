#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扣子工作流兼容版本 - 输入格式适配器
专门为扣子工作流环境设计的版本
支持args.params输入方式和字典返回格式
"""

import json
import re


def kouzi_workflow_main(args):
    """
    扣子工作流主函数
    专门为扣子工作流环境设计的入口函数
    
    参数:
        args: 扣子工作流传入的参数对象，包含params属性
    
    返回:
        dict: 包含所有输出字段的字典
    """
    try:
        # 从args.params获取输入数据
        input_data = getattr(args, 'params', {}).get('input', None)
        
        # 调试信息
        debug_info = {
            "received_args_type": str(type(args)),
            "received_input_type": str(type(input_data)),
            "received_input_preview": str(input_data)[:200] if input_data else "None"
        }
        
        # 创建适配器实例
        adapter = KouziInputFormatAdapter()
        
        # 处理输入数据
        result = adapter.process_input(input_data)
        
        # 确保返回字典格式，包含所有必需字段
        output = {
            "video_serial_number": result.get("video_serial_number", ""),
            "video_content_summary": result.get("video_content_summary", ""),
            "detailed_content_description": result.get("detailed_content_description", ""),
            "keyword_tags": result.get("keyword_tags", ""),
            "main_objects": result.get("main_objects", ""),
            "status": result.get("status", "success"),
            "message": result.get("message", "数据处理成功"),
            "debug_info": debug_info
        }
        
        return output
        
    except Exception as e:
        # 错误处理，返回标准字典格式
        return {
            "video_serial_number": "",
            "video_content_summary": "",
            "detailed_content_description": "",
            "keyword_tags": "",
            "main_objects": "",
            "status": "error",
            "message": f"处理失败: {str(e)}",
            "debug_info": {
                "error_type": str(type(e).__name__),
                "error_message": str(e),
                "args_received": str(type(args)) if 'args' in locals() else "None"
            }
        }


class KouziInputFormatAdapter:
    """
    扣子工作流专用输入格式适配器
    优化了字段映射和错误处理机制
    """
    
    def __init__(self):
        """
        初始化适配器
        """
        # 字段映射配置
        self.field_mapping = {
            # 中文字段映射
            "视频序列号": "video_serial_number",
            "视频内容摘要": "video_content_summary", 
            "详细内容描述": "detailed_content_description",
            "关键词标签": "keyword_tags",
            "主要对象": "main_objects",
            
            # 官方格式字段映射
            "单选": "video_serial_number",
            "文本": "video_content_summary",
            "日期": "detailed_content_description",
            
            # 英文字段映射（直接映射）
            "video_serial_number": "video_serial_number",
            "video_content_summary": "video_content_summary",
            "detailed_content_description": "detailed_content_description",
            "keyword_tags": "keyword_tags",
            "main_objects": "main_objects"
        }
        
        # 默认输出字段
        self.default_output = {
            "video_serial_number": "",
            "video_content_summary": "",
            "detailed_content_description": "",
            "keyword_tags": "",
            "main_objects": "",
            "status": "success",
            "message": "数据处理成功"
        }
    
    def process_input(self, input_data):
        """
        处理输入数据的主函数
        
        参数:
            input_data: 输入数据，可以是字符串、字典或其他格式
        
        返回:
            dict: 处理结果
        """
        try:
            # 输入数据验证
            if input_data is None:
                return self._create_error_result("输入数据为空")
            
            # 处理不同格式的输入数据
            if isinstance(input_data, str):
                return self._process_string_input(input_data)
            elif isinstance(input_data, dict):
                return self._process_dict_input(input_data)
            elif isinstance(input_data, list):
                return self._process_list_input(input_data)
            else:
                return self._create_error_result(f"不支持的输入数据类型: {type(input_data)}")
                
        except Exception as e:
            return self._create_error_result(f"处理输入数据时发生错误: {str(e)}")
    
    def _process_string_input(self, input_str):
        """
        处理字符串格式的输入
        
        参数:
            input_str: 字符串输入
        
        返回:
            dict: 处理结果
        """
        try:
            # 尝试解析为JSON
            cleaned_str = self._clean_json_string(input_str)
            data = json.loads(cleaned_str)
            return self._process_dict_input(data)
        except json.JSONDecodeError:
            # 如果不是JSON，尝试解析键值对格式
            return self._parse_key_value_format(input_str)
    
    def _process_dict_input(self, input_dict):
        """
        处理字典格式的输入
        
        参数:
            input_dict: 字典输入
        
        返回:
            dict: 处理结果
        """
        result = self.default_output.copy()
        
        try:
            # 遍历输入字典，映射字段
            for key, value in input_dict.items():
                # 查找对应的英文字段名
                english_key = self.field_mapping.get(key, key)
                
                # 如果是目标字段，进行映射
                if english_key in self.default_output:
                    processed_value = self._process_field_value(value)
                    result[english_key] = processed_value
            
            # 检查是否有有效数据
            has_data = any(result[key] for key in ["video_serial_number", "video_content_summary", 
                                                  "detailed_content_description", "keyword_tags", "main_objects"])
            
            if not has_data:
                result["message"] = "警告：未提取到有效数据，请检查输入格式"
            
            return result
            
        except Exception as e:
            return self._create_error_result(f"处理字典输入时发生错误: {str(e)}")
    
    def _process_list_input(self, input_list):
        """
        处理列表格式的输入
        
        参数:
            input_list: 列表输入
        
        返回:
            dict: 处理结果
        """
        try:
            if not input_list:
                return self._create_error_result("输入列表为空")
            
            # 如果列表只有一个元素，直接处理该元素
            if len(input_list) == 1:
                return self.process_input(input_list[0])
            
            # 如果有多个元素，尝试合并处理
            result = self.default_output.copy()
            
            for item in input_list:
                if isinstance(item, dict):
                    item_result = self._process_dict_input(item)
                    # 合并非空字段
                    for key in ["video_serial_number", "video_content_summary", 
                               "detailed_content_description", "keyword_tags", "main_objects"]:
                        if item_result.get(key) and not result.get(key):
                            result[key] = item_result[key]
            
            return result
            
        except Exception as e:
            return self._create_error_result(f"处理列表输入时发生错误: {str(e)}")
    
    def _clean_json_string(self, json_str):
        """
        清理JSON字符串，移除多余的字符
        
        参数:
            json_str: 原始JSON字符串
        
        返回:
            str: 清理后的JSON字符串
        """
        # 移除前后空白字符
        cleaned = json_str.strip()
        
        # 移除可能的markdown代码块标记
        cleaned = re.sub(r'^```json\s*', '', cleaned)
        cleaned = re.sub(r'\s*```$', '', cleaned)
        
        # 移除其他可能的前缀和后缀
        cleaned = re.sub(r'^[^{\[]*', '', cleaned)
        cleaned = re.sub(r'[^}\]]*$', '', cleaned)
        
        return cleaned
    
    def _parse_key_value_format(self, input_str):
        """
        解析键值对格式的字符串
        
        参数:
            input_str: 键值对格式的字符串
        
        返回:
            dict: 解析结果
        """
        result = self.default_output.copy()
        
        try:
            # 按行分割
            lines = input_str.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 查找对应的英文字段名
                    english_key = self.field_mapping.get(key, key)
                    
                    # 如果是目标字段，进行映射
                    if english_key in self.default_output:
                        processed_value = self._process_field_value(value)
                        result[english_key] = processed_value
            
            return result
            
        except Exception as e:
            return self._create_error_result(f"解析键值对格式时发生错误: {str(e)}")
    
    def _process_field_value(self, value):
        """
        处理字段值，确保类型正确
        
        参数:
            value: 原始字段值
        
        返回:
            str: 处理后的字符串值
        """
        if value is None:
            return ""
        
        # 转换为字符串
        if isinstance(value, (list, dict)):
            try:
                return json.dumps(value, ensure_ascii=False)
            except:
                return str(value)
        
        # 清理字符串值
        str_value = str(value).strip()
        
        # 移除引号
        if str_value.startswith('"') and str_value.endswith('"'):
            str_value = str_value[1:-1]
        elif str_value.startswith("'") and str_value.endswith("'"):
            str_value = str_value[1:-1]
        
        return str_value
    
    def _create_error_result(self, error_message):
        """
        创建错误结果
        
        参数:
            error_message: 错误信息
        
        返回:
            dict: 错误结果字典
        """
        result = self.default_output.copy()
        result["status"] = "error"
        result["message"] = error_message
        return result


# 为了兼容性，保留原有的函数名
def main(args):
    """
    主函数 - 扣子工作流调用入口
    
    参数:
        args: 扣子工作流传入的参数对象
    
    返回:
        dict: 处理结果字典
    """
    return kouzi_workflow_main(args)


if __name__ == "__main__":
    # 测试代码
    class MockArgs:
        def __init__(self, input_data):
            self.params = {'input': input_data}
    
    # 测试用例
    test_input = {
        "video_serial_number": "TEST_001",
        "video_content_summary": "测试视频摘要",
        "detailed_content_description": "测试详细描述",
        "keyword_tags": "测试, 标签",
        "main_objects": "测试对象"
    }
    
    mock_args = MockArgs(test_input)
    result = kouzi_workflow_main(mock_args)
    
    print("扣子工作流适配器测试结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输入格式适配器 - 精简版
"""

import json
import re


class InputFormatAdapter:
    """输入格式适配器 - 精简版"""
    
    def __init__(self):
        # 字段映射
        self.field_mapping = {
            "视频序列号": "video_serial_number",
            "视频内容摘要": "video_content_summary", 
            "详细内容描述": "detailed_content_description",
            "关键词标签": "keyword_tags",
            "主要对象": "main_objects",
            "单选": "video_serial_number",
            "文本": "video_content_summary",
            "日期": "detailed_content_description",
            "video_serial_number": "video_serial_number",
            "video_content_summary": "video_content_summary",
            "detailed_content_description": "detailed_content_description",
            "keyword_tags": "keyword_tags",
            "main_objects": "main_objects"
        }
    
    def main(self, input_data):
        """主处理函数"""
        try:
            processed_data = self._process_input(input_data)
            formatted_result = self._format_data(processed_data)
            
            return {
                "main_objects": formatted_result,
                "status": "success",
                "message": "数据处理成功"
            }
        except Exception as e:
            return {
                "$error": f"处理失败: {str(e)}",
                "status": "error"
            }
    
    def _process_input(self, input_data):
        """处理输入数据"""
        if input_data is None:
            raise ValueError("输入数据为空")
        
        # 字符串输入
        if isinstance(input_data, str):
            try:
                parsed_data = json.loads(input_data)
                return [parsed_data] if isinstance(parsed_data, dict) else parsed_data
            except json.JSONDecodeError:
                return [self._parse_key_value_format(input_data)]
        
        # 列表输入
        elif isinstance(input_data, list):
            result_list = []
            for item in input_data:
                if isinstance(item, dict) and "fields" in item:
                    result_list.extend(self._process_fields_format(item))
                else:
                    result_list.append(item)
            return result_list
        
        # 字典输入
        elif isinstance(input_data, dict):
            if "input" in input_data:
                return self._process_input(input_data["input"])
            elif "items" in input_data:
                return self._process_input(input_data["items"])
            elif "fields" in input_data:
                return self._process_fields_format(input_data)
            else:
                return [input_data]
        
        return [{"data": str(input_data)}]
    
    def _process_fields_format(self, input_data):
        """处理fields格式"""
        try:
            fields_str = input_data.get("fields", "{}")
            fields_data = json.loads(fields_str) if isinstance(fields_str, str) else fields_str
            
            if not fields_data:
                return []
            
            converted_data = {}
            for field_name, field_value in fields_data.items():
                if isinstance(field_value, list) and field_value:
                    if isinstance(field_value[0], dict) and "text" in field_value[0]:
                        converted_data[field_name] = field_value[0]["text"]
                    else:
                        converted_data[field_name] = str(field_value[0])
                else:
                    converted_data[field_name] = str(field_value)
            
            if input_data.get("record_id"):
                converted_data["record_id"] = input_data["record_id"]
            
            return [converted_data]
        except Exception:
            return [input_data]
    
    def _parse_key_value_format(self, input_str):
        """解析键值对格式"""
        result = {}
        patterns = [
            r'"([^"]+)"\s*:\s*"([^"]*)",?',
            r'([^:]+):\s*([^,\n]+)',
            r'([^=]+)=([^,\n]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, input_str)
            if matches:
                for key, value in matches:
                    result[key.strip().strip('"\'')] = value.strip().strip('"\'')
                break
        
        return result if result else {"raw_input": input_str}
    
    def _format_data(self, data_list):
        """格式化数据"""
        formatted_objects = []
        target_fields = [
            "video_serial_number", "video_content_summary", 
            "detailed_content_description", "keyword_tags", "main_objects"
        ]
        
        for data in data_list:
            formatted_object = {}
            for target_field in target_fields:
                value = self._extract_field_value(data, target_field)
                formatted_object[target_field] = str(value) if value else ""
            formatted_objects.append(formatted_object)
        
        return formatted_objects
    
    def _extract_field_value(self, data, target_key):
        """提取字段值"""
        # 直接查找
        if target_key in data:
            return self._process_field_value(data[target_key])
        
        # 通过映射查找
        for source_key, mapped_key in self.field_mapping.items():
            if mapped_key == target_key and source_key in data:
                return self._process_field_value(data[source_key])
        
        return ""
    
    def _process_field_value(self, value):
        """处理字段值"""
        if value is None:
            return ""
        
        if isinstance(value, list) and value:
            first_item = value[0]
            if isinstance(first_item, dict) and "text" in first_item:
                return str(first_item["text"])
            return str(first_item)
        
        elif isinstance(value, dict):
            if "text" in value:
                return str(value["text"])
            elif value:
                return str(list(value.values())[0])
        
        return str(value)


def main(input_data=None, args=None):
    """全局主函数"""
    try:
        # 扣子工作流调用检测
        if args is not None and hasattr(args, 'params'):
            return kouzi_workflow_main(args)
        if input_data is not None and hasattr(input_data, 'params'):
            return kouzi_workflow_main(input_data)
        
        # 普通调用
        adapter = InputFormatAdapter()
        if input_data is None:
            return demo_mode()
        
        return adapter.main(input_data)
        
    except Exception as e:
        return {
            "$error": f"执行失败: {str(e)}",
            "status": "error"
        }


def kouzi_workflow_main(args):
    """扣子工作流专用函数"""
    try:
        input_data = getattr(args, 'params', {}).get('input', None)
        adapter = InputFormatAdapter()
        
        if input_data is None:
            result = demo_mode()
        else:
            result = adapter.main(input_data)
        
        # 构造扣子工作流要求的数组格式
        if "main_objects" in result and isinstance(result["main_objects"], list) and result["main_objects"]:
            main_objects_array = result["main_objects"]
            first_obj = main_objects_array[0]
            output = {
                "video_serial_number": first_obj.get("video_serial_number", ""),
                "video_content_summary": first_obj.get("video_content_summary", ""),
                "detailed_content_description": first_obj.get("detailed_content_description", ""),
                "keyword_tags": first_obj.get("keyword_tags", ""),
                "main_objects": main_objects_array,
                "status": result.get("status", "success"),
                "message": result.get("message", "数据处理成功")
            }
        else:
            # 构造数组格式
            main_objects_array = [{
                "video_serial_number": result.get("video_serial_number", ""),
                "video_content_summary": result.get("video_content_summary", ""),
                "detailed_content_description": result.get("detailed_content_description", ""),
                "keyword_tags": result.get("keyword_tags", ""),
                "main_objects": result.get("main_objects", "")
            }]
            
            output = {
                "video_serial_number": result.get("video_serial_number", ""),
                "video_content_summary": result.get("video_content_summary", ""),
                "detailed_content_description": result.get("detailed_content_description", ""),
                "keyword_tags": result.get("keyword_tags", ""),
                "main_objects": main_objects_array,
                "status": result.get("status", "success"),
                "message": result.get("message", "数据处理成功")
            }
        
        return output
        
    except Exception as e:
        return {
            "video_serial_number": "",
            "video_content_summary": "",
            "detailed_content_description": "",
            "keyword_tags": "",
            "main_objects": [],
            "status": "error",
            "message": f"扣子工作流处理失败: {str(e)}"
        }


def demo_mode():
    """演示模式"""
    return {
        "main_objects": [{
            "video_serial_number": "DEMO_001",
            "video_content_summary": "演示视频内容",
            "detailed_content_description": "这是一个演示用的详细描述",
            "keyword_tags": "演示,测试,示例",
            "main_objects": "演示对象"
        }],
        "status": "success",
        "message": "演示模式运行成功"
    }


if __name__ == "__main__":
    # 简单测试
    adapter = InputFormatAdapter()
    test_data = {
        "video_serial_number": "TEST_001",
        "video_content_summary": "测试内容",
        "detailed_content_description": "测试描述",
        "keyword_tags": "测试,标签",
        "main_objects": "测试对象"
    }
    result = adapter.main(test_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
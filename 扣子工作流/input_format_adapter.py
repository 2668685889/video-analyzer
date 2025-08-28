#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输入格式适配器
专门处理用户截图中显示的输入格式，解决函数参数不匹配问题
"""

import json
import re


class InputFormatAdapter:
    """
    输入格式适配器
    处理用户特定的输入格式并转换为标准的JSON结构
    """
    
    def __init__(self):
        """
        初始化适配器
        """
        # 默认字段映射（支持多种字段名格式）
        self.field_mapping = {
            # 原有的中文字段映射
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
    
    def main(self, input_data):
        """
        主处理函数 - 接受输入参数并处理
        这个函数专门设计来接受外部传入的参数
        
        参数:
            input_data: 输入的数据，可以是字符串或字典格式
        
        返回:
            dict: 包含处理结果的字典
        """
        try:
            # 处理输入数据
            processed_data = self._process_input(input_data)
            
            # 格式化数据
            formatted_result = self._format_data(processed_data)
            
            # 返回结构化结果
            return {
                "main_objects": formatted_result,
                "status": "success",
                "message": "数据处理成功"
            }
            
        except Exception as e:
            return {
                "$error": f"处理失败: {str(e)}",
                "status": "error",
                "input_received": str(input_data)[:200] if input_data else "None"
            }
    
    def _process_input(self, input_data):
        """
        处理输入数据，支持多种输入格式
        
        参数:
            input_data: 输入数据
        
        返回:
            list: 处理后的数据列表（支持Array<Object>格式）
        """
        if input_data is None:
            raise ValueError("输入数据为空")
        
        # 如果输入是字符串，尝试解析为JSON
        if isinstance(input_data, str):
            # 清理字符串中的特殊字符
            cleaned_input = self._clean_input_string(input_data)
            
            try:
                # 尝试解析为JSON
                parsed_data = json.loads(cleaned_input)
                # 如果解析结果是列表，直接返回
                if isinstance(parsed_data, list):
                    return parsed_data
                # 如果是字典，包装成列表
                elif isinstance(parsed_data, dict):
                    return [parsed_data]
                else:
                    return [{"data": parsed_data}]
            except json.JSONDecodeError:
                # 如果不是JSON，尝试解析为键值对格式
                parsed_dict = self._parse_key_value_format(cleaned_input)
                return [parsed_dict]
        
        # 如果输入是列表（Array<Object>格式）
        elif isinstance(input_data, list):
            if len(input_data) == 0:
                return [{}]  # 空列表返回空对象
            
            # 处理列表中的每个元素
            result_list = []
            for item in input_data:
                if isinstance(item, dict):
                    # 检查是否是包含fields和record_id的格式
                    if "fields" in item:
                        processed_items = self._process_fields_format(item)
                        result_list.extend(processed_items)
                    else:
                        result_list.append(item)
                elif isinstance(item, str):
                    try:
                        parsed_item = json.loads(item)
                        result_list.append(parsed_item if isinstance(parsed_item, dict) else {"data": parsed_item})
                    except json.JSONDecodeError:
                        result_list.append({"data": item})
                else:
                    result_list.append({"data": str(item)})
            
            return result_list
        
        # 如果输入已经是字典，检查是否包含特殊格式
        elif isinstance(input_data, dict):
            # 检查是否是包含input数组的新格式
            if "input" in input_data:
                return self._process_input_array_format(input_data)
            # 检查是否是包含items数组的官方格式
            elif "items" in input_data:
                return self._process_items_format(input_data)
            # 检查是否是包含fields和record_id的特殊格式
            elif "fields" in input_data:
                return self._process_fields_format(input_data)
            else:
                return [input_data]
        
        else:
            # 其他类型转换为字典并包装成列表
            return [{"data": str(input_data)}]
    
    def _process_input_array_format(self, input_data):
        """
        处理包含input数组的新输入格式
        
        参数:
            input_data (dict): 包含input数组的输入数据
        
        返回:
            list: 处理后的数据列表
        """
        try:
            input_array = input_data.get("input", [])
            result_list = []
            
            for item in input_array:
                if isinstance(item, dict) and "fields" in item:
                    # 处理每个item中的fields格式
                    processed_items = self._process_fields_format(item)
                    result_list.extend(processed_items)
                else:
                    # 如果不是预期格式，直接添加
                    result_list.append(item)
            
            return result_list
            
        except Exception as e:
            # 如果解析失败，返回原始数据
            return [input_data]
    
    def _process_items_format(self, input_data):
        """
        处理包含items数组的官方输入格式
        
        参数:
            input_data (dict): 包含items数组的输入数据
        
        返回:
            list: 处理后的数据列表
        """
        try:
            items = input_data.get("items", [])
            result_list = []
            
            for item in items:
                if isinstance(item, dict) and "fields" in item:
                    # 处理每个item中的fields格式
                    processed_items = self._process_fields_format(item)
                    result_list.extend(processed_items)
                else:
                    # 如果不是预期格式，直接添加
                    result_list.append(item)
            
            return result_list
            
        except Exception as e:
            # 如果解析失败，返回原始数据
            return [input_data]
    
    def _process_fields_format(self, input_data):
        """
        处理包含fields字段的特殊输入格式
        
        参数:
            input_data (dict): 包含fields和record_id的输入数据
        
        返回:
            list: 处理后的数据列表
        """
        try:
            # 提取fields字段
            fields_str = input_data.get("fields", "{}")
            record_id = input_data.get("record_id", "")
            
            # 解析fields JSON字符串
            if isinstance(fields_str, str):
                # 清理和修复JSON字符串
                cleaned_fields_str = self._clean_json_string(fields_str)
                fields_data = json.loads(cleaned_fields_str)
            else:
                fields_data = fields_str
            
            # 如果fields为空，跳过处理
            if not fields_data:
                return []
            
            # 转换为标准格式
            converted_data = {}
            
            # 处理每个字段
            for field_name, field_value in fields_data.items():
                if isinstance(field_value, list) and len(field_value) > 0:
                    # 提取第一个元素的text值
                    if isinstance(field_value[0], dict) and "text" in field_value[0]:
                        converted_data[field_name] = field_value[0]["text"]
                    else:
                        converted_data[field_name] = str(field_value[0])
                else:
                    converted_data[field_name] = str(field_value)
            
            # 添加record_id
            if record_id:
                converted_data["record_id"] = record_id
            
            return [converted_data]
            
        except Exception as e:
            # 如果解析失败，返回原始数据
            return [input_data]
    
    def _clean_json_string(self, json_str):
        """
        清理和修复JSON字符串
        
        参数:
            json_str (str): 原始JSON字符串
        
        返回:
            str: 清理后的JSON字符串
        """
        # 移除首尾空白字符
        cleaned = json_str.strip()
        
        # 检查并修复括号匹配问题
        open_braces = cleaned.count('{')
        close_braces = cleaned.count('}')
        
        # 如果闭括号多于开括号，尝试移除多余的闭括号
        if close_braces > open_braces:
            excess_braces = close_braces - open_braces
            # 从末尾移除多余的闭括号
            for _ in range(excess_braces):
                if cleaned.endswith('}'):
                    cleaned = cleaned[:-1]
        
        # 如果开括号多于闭括号，添加缺失的闭括号
        elif open_braces > close_braces:
            missing_braces = open_braces - close_braces
            cleaned += '}' * missing_braces
        
        return cleaned
    
    def _clean_input_string(self, input_str):
        """
        清理输入字符串，移除可能导致解析错误的字符
        
        参数:
            input_str (str): 原始输入字符串
        
        返回:
            str: 清理后的字符串
        """
        # 移除可能的控制字符和特殊字符
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', input_str)
        
        # 移除多余的空白字符
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def _parse_key_value_format(self, input_str):
        """
        解析键值对格式的输入
        
        参数:
            input_str (str): 键值对格式的字符串
        
        返回:
            dict: 解析后的字典
        """
        result = {}
        
        # 尝试匹配 key: value 格式
        patterns = [
            r'"([^"]+)"\s*:\s*"([^"]*)",?',  # "key": "value"
            r'([^:]+):\s*([^,\n]+)',  # key: value
            r'([^=]+)=([^,\n]+)'  # key=value
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, input_str)
            if matches:
                for key, value in matches:
                    clean_key = key.strip().strip('"\'')
                    clean_value = value.strip().strip('"\'')
                    result[clean_key] = clean_value
                break
        
        # 如果没有匹配到任何模式，返回原始数据
        if not result:
            result = {"raw_input": input_str}
        
        return result
    
    def _format_data(self, data_list):
        """
        格式化数据为标准输出格式
        
        参数:
            data_list (list): 输入数据列表
        
        返回:
            list: 格式化后的对象数组
        """
        formatted_objects = []
        
        # 目标输出字段（按照用户截图中的结构）
        target_fields = [
            "video_serial_number",
            "video_content_summary", 
            "detailed_content_description",
            "keyword_tags",
            "main_objects"
        ]
        
        # 处理列表中的每个数据对象
        for data in data_list:
            # 创建标准化的输出对象
            formatted_object = {}
            
            # 为每个目标字段提取值
            for target_field in target_fields:
                value = self._extract_field_value(data, target_field)
                formatted_object[target_field] = str(value) if value else ""
            
            formatted_objects.append(formatted_object)
        
        # 返回对象数组
        return formatted_objects
    
    def _extract_field_value(self, data, target_english_key, fallback_key=None):
        """
        从数据中提取字段值
        
        参数:
            data (dict): 数据字典
            target_english_key (str): 目标英文键名
            fallback_key (str): 备用键名
        
        返回:
            str: 提取的值
        """
        # 直接查找目标英文键名
        if target_english_key in data:
            return self._process_field_value(data[target_english_key])
        
        # 查找所有可能映射到目标键的源键名
        for source_key, mapped_key in self.field_mapping.items():
            if mapped_key == target_english_key and source_key in data:
                return self._process_field_value(data[source_key])
        
        # 尝试备用键名
        if fallback_key and fallback_key in data:
            return self._process_field_value(data[fallback_key])
        
        # 尝试其他可能的键名变体
        possible_keys = [
            target_english_key.lower(),
            target_english_key.upper(),
            target_english_key.replace('_', ''),
            target_english_key.replace('_', '-')
        ]
        
        for key in possible_keys:
            if key in data:
                return self._process_field_value(data[key])
        
        # 如果都没找到，返回空字符串
        return ""
    
    def _process_field_value(self, value):
        """
        处理字段值，提取有用信息
        
        参数:
            value: 字段值
        
        返回:
            str: 处理后的字符串值
        """
        if value is None:
            return ""
        
        # 如果是列表，尝试提取text值
        if isinstance(value, list) and len(value) > 0:
            first_item = value[0]
            if isinstance(first_item, dict) and "text" in first_item:
                return str(first_item["text"])
            else:
                return str(first_item)
        
        # 如果是字典，尝试提取text值
        elif isinstance(value, dict):
            if "text" in value:
                return str(value["text"])
            else:
                # 返回字典的字符串表示或第一个值
                if value:
                    return str(list(value.values())[0])
                else:
                    return ""
        
        # 其他类型直接转换为字符串
        else:
            return str(value)
    
    def process_multiple_inputs(self, input_list):
        """
        处理多个输入数据
        
        参数:
            input_list (list): 输入数据列表
        
        返回:
            dict: 处理结果
        """
        try:
            all_results = []
            
            for i, input_data in enumerate(input_list):
                result = self.main(input_data)
                if result.get("status") == "success":
                    all_results.extend(result["main_objects"])
                else:
                    # 记录错误但继续处理其他数据
                    print(f"处理第{i+1}个输入时出错: {result.get('$error', '未知错误')}")
            
            return {
                "main_objects": all_results,
                "status": "success",
                "total_processed": len(all_results),
                "message": f"成功处理{len(all_results)}组数据"
            }
            
        except Exception as e:
            return {
                "$error": f"批量处理失败: {str(e)}",
                "status": "error"
            }
    
    def get_sample_input_format(self):
        """
        获取示例输入格式
        
        返回:
            dict: 示例输入格式
        """
        return {
            "video_serial_number": "VIDEO_001",
            "video_content_summary": "视频内容摘要",
            "detailed_content_description": "详细内容描述",
            "keyword_tags": "关键词1, 关键词2",
            "main_objects": "主要对象1, 主要对象2"
        }
    
    def get_expected_output_format(self):
        """
        获取期望的输出格式
        
        返回:
            dict: 期望输出格式
        """
        return {
            "main_objects": [
                {
                    "video_serial_number": "VIDEO_001",
                    "video_content_summary": "视频内容摘要",
                    "detailed_content_description": "详细内容描述",
                    "keyword_tags": "关键词1, 关键词2",
                    "main_objects": "主要对象1, 主要对象2"
                }
            ],
            "status": "success",
            "message": "数据处理成功"
        }


def main(input_data=None, args=None):
    """
    全局主函数 - 系统调用的入口点
    支持普通调用和扣子工作流调用
    
    参数:
        input_data: 输入数据，可以是字符串、字典或None
        args: 扣子工作流参数对象（可选）
    
    返回:
        dict: 处理结果
    """
    try:
        # 检测是否为扣子工作流调用
        if args is not None and hasattr(args, 'params'):
            return kouzi_workflow_main(args)
        
        # 如果input_data实际上是args对象（扣子工作流单参数调用）
        if input_data is not None and hasattr(input_data, 'params'):
            return kouzi_workflow_main(input_data)
        
        # 普通调用逻辑
        adapter = InputFormatAdapter()
        
        # 如果没有输入数据，运行演示模式
        if input_data is None:
            return demo_mode()
        
        # 处理输入数据
        result = adapter.main(input_data)
        return result
        
    except Exception as e:
        return {
            "$error": f"全局main函数执行失败: {str(e)}",
            "status": "error",
            "input_received": str(input_data)[:200] if input_data else "None"
        }


def kouzi_workflow_main(args):
    """
    扣子工作流专用主函数
    
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
        adapter = InputFormatAdapter()
        
        # 处理输入数据
        if input_data is None:
            # 如果没有输入，返回演示数据
            result = demo_mode()
        else:
            result = adapter.main(input_data)
        
        # 确保返回字典格式，包含所有必需字段
        # 扣子工作流要求main_objects字段必须是数组类型
        if "main_objects" in result and isinstance(result["main_objects"], list) and result["main_objects"]:
            # 如果result已经包含main_objects数组，直接使用
            output = {
                "video_serial_number": result["main_objects"][0].get("video_serial_number", ""),
                "video_content_summary": result["main_objects"][0].get("video_content_summary", ""),
                "detailed_content_description": result["main_objects"][0].get("detailed_content_description", ""),
                "keyword_tags": result["main_objects"][0].get("keyword_tags", ""),
                "main_objects": result["main_objects"],  # 保持数组格式
                "status": result.get("status", "success"),
                "message": result.get("message", "数据处理成功"),
                "debug_info": debug_info
            }
        else:
            # 构造符合扣子工作流要求的数组格式
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
                "main_objects": main_objects_array,  # 返回数组格式
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


def demo_mode():
    """
    演示模式 - 当没有输入参数时运行
    
    返回:
        dict: 演示结果
    """
    adapter = InputFormatAdapter()
    
    # 创建演示数据
    demo_input = {
        "video_serial_number": "DEMO_001",
        "video_content_summary": "演示视频内容摘要",
        "detailed_content_description": "这是演示模式的详细内容描述",
        "keyword_tags": "演示, 测试, 示例",
        "main_objects": "演示对象, 测试内容"
    }
    
    # 处理演示数据
    result = adapter.main(demo_input)
    
    # 添加演示模式标识
    if isinstance(result, dict):
        result["demo_mode"] = True
        result["message"] = "演示模式 - " + result.get("message", "")
    
    return result


def demo():
    """
    详细演示函数 - 展示如何使用输入格式适配器
    """
    print("=== 输入格式适配器演示 ===\n")
    
    adapter = InputFormatAdapter()
    
    # 示例1：标准JSON格式输入
    print("【示例1：标准JSON格式】")
    json_input = {
        "video_serial_number": "VIDEO_001",
        "video_content_summary": "这是一个测试视频的摘要",
        "detailed_content_description": "这是详细的内容描述",
        "keyword_tags": "测试, 演示, 视频",
        "main_objects": "测试对象, 演示内容"
    }
    
    result1 = adapter.main(json_input)
    print(f"输入: {json_input}")
    print(f"输出: {json.dumps(result1, ensure_ascii=False, indent=2)}\n")
    
    # 示例2：字符串格式输入
    print("【示例2：字符串格式】")
    string_input = '{"video_serial_number": "VIDEO_002", "video_content_summary": "字符串格式测试"}'
    
    result2 = adapter.main(string_input)
    print(f"输入: {string_input}")
    print(f"输出: {json.dumps(result2, ensure_ascii=False, indent=2)}\n")
    
    # 示例3：处理错误输入
    print("【示例3：错误输入处理】")
    error_input = None
    
    result3 = adapter.main(error_input)
    print(f"输入: {error_input}")
    print(f"输出: {json.dumps(result3, ensure_ascii=False, indent=2)}\n")
    
    # 示例4：测试全局main函数
    print("【示例4：全局main函数测试】")
    global_result = main(json_input)
    print(f"全局main函数输出: {json.dumps(global_result, ensure_ascii=False, indent=2)}\n")
    
    # 显示示例格式
    print("【示例输入格式】")
    sample_input = adapter.get_sample_input_format()
    print(json.dumps(sample_input, ensure_ascii=False, indent=2))
    
    print("\n【期望输出格式】")
    expected_output = adapter.get_expected_output_format()
    print(json.dumps(expected_output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    demo()
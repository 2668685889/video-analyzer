# 智能字段模板生成功能使用示例

## 使用场景示例

### 场景1：视频内容分析结果模板生成

假设您的大模型分析视频后返回以下格式的结果：

```json
{
  "video_serial_number": "20250321163301122334",
  "videoContentSummary": "一位身着白色上衣的女性正在进行健身操练习",
  "detailed_content_description": "视频展示了一位女性在室内进行健身操练习...",
  "keywords_tags": "女性, 健身, 室内运动, 白色上衣, 健身操",
  "main_characters_objects": "女性健身教练",
  "video_source_path": "健身房/汽车/Range Rover Sport FlyRamp Test 01.mp4"
}
```

### 智能分析过程

#### 1. 内容结构识别
系统会自动识别这是JSON格式的结构化数据，并分析每个字段的特征：

- `video_serial_number`: 数字字符串 → 单行文本
- `videoContentSummary`: 短描述文本 → 单行文本  
- `detailed_content_description`: 长描述文本 → 多行文本
- `keywords_tags`: 逗号分隔的标签 → 多行文本
- `main_characters_objects`: 描述性文本 → 单行文本
- `video_source_path`: 文件路径 → 单行文本

#### 2. 字段映射生成
系统会生成以下飞书字段映射：

| 原字段名 | 中文字段名 | 飞书字段类型 | 说明 |
|---------|-----------|-------------|------|
| video_serial_number | 视频序列号 | 单行文本(1) | 唯一标识符 |
| videoContentSummary | 内容摘要 | 单行文本(1) | 简短描述 |
| detailed_content_description | 详细内容描述 | 多行文本(1) | 完整描述 |
| keywords_tags | 关键词标签 | 多行文本(1) | 标签列表 |
| main_characters_objects | 主要角色对象 | 单行文本(1) | 主要元素 |
| video_source_path | 视频源路径 | 单行文本(1) | 文件位置 |

### 场景2：复杂结构化数据处理

对于更复杂的分析结果：

```json
{
  "basic_info": {
    "duration": 120,
    "resolution": "1920x1080",
    "file_size": 45.6
  },
  "content_analysis": {
    "scene_count": 5,
    "has_dialogue": true,
    "emotion_score": 8.5,
    "content_rating": "适合所有年龄"
  },
  "technical_details": {
    "codec": "H.264",
    "bitrate": "2000kbps",
    "frame_rate": 30
  }
}
```

系统会智能展平结构并创建对应字段：

- `duration` → 时长(数字类型)
- `resolution` → 分辨率(单行文本)
- `file_size` → 文件大小(数字类型)
- `scene_count` → 场景数量(数字类型)
- `has_dialogue` → 包含对话(复选框)
- `emotion_score` → 情感评分(数字类型)
- `content_rating` → 内容评级(单行文本)

## 实际操作步骤

### 步骤1：准备历史数据

1. 首先分析几个视频文件，确保数据库中有历史记录：
   ```
   选择视频文件 → 输入分析提示词 → 开始分析
   ```

2. 确认分析结果已保存到数据库

### 步骤2：执行智能设置

1. 点击主界面的「设置表格结构」按钮
2. 在确认对话框中点击「确定」
3. 等待系统处理（通常需要10-30秒）

### 步骤3：查看设置结果

成功时会显示类似信息：
```
智能字段模板生成完成！

📊 分析摘要：
• 分析了 10 条历史记录
• 检测到 15 个字段
• 置信度等级：high

📋 模板摘要：
• 生成了 12 个字段
• 字段类型分布： 文本(5) 数字(2) 单选(3) 多选(2)

📄 模板已保存到：
/path/to/templates/smart_field_template_20240120_103000.json

📝 下一步操作：
1. 打开飞书多维表格
2. 根据生成的模板手动创建字段
3. 完成后即可正常同步数据

🔧 字段创建指南：
1. 创建文本类型字段：视频标题
2. 创建数字类型字段：视频时长
3. 创建单选类型字段：情感分析
... 等共 12 个字段
```

#### 生成的字段列表
- 📝 视频标题 (文本)
- 🔢 视频时长 (数字)
- 📋 主要角色 (多选)
- 🎯 情感分析 (单选)
- 🏷️ 关键词 (多选)
- 📅 分析时间 (日期时间)
- 📊 置信度分数 (数字)
- 🎬 视频类型 (单选)

## 生成的模板文件示例

```json
{
  "template_info": {
    "name": "智能生成的飞书字段模板",
    "version": "1.0",
    "created_at": "2024-01-20T10:30:00.123456",
    "based_on_records": 8
  },
  "analysis_summary": {
    "content_type": "json",
    "structure_complexity": "medium",
    "detected_fields_count": 12,
    "confidence_level": "high"
  },
  "feishu_fields": [
    {
      "field_name": "视频序列号",
      "field_type": 1,
      "description": "视频的唯一标识符",
      "source_field": "video_serial_number"
    },
    {
      "field_name": "内容摘要",
      "field_type": 1,
      "description": "视频内容的简短摘要",
      "source_field": "videoContentSummary"
    },
    {
      "field_name": "详细内容描述",
      "field_type": 1,
      "description": "视频内容的详细描述",
      "source_field": "detailed_content_description"
    },
    {
      "field_name": "关键词标签",
      "field_type": 1,
      "description": "视频相关的关键词和标签",
      "source_field": "keywords_tags"
    },
    {
      "field_name": "主要角色对象",
      "field_type": 1,
      "description": "视频中的主要人物或对象",
      "source_field": "main_characters_objects"
    },
    {
      "field_name": "视频源路径",
      "field_type": 1,
      "description": "视频文件的存储路径",
      "source_field": "video_source_path"
    }
  ],
  "field_mapping": {
    "video_serial_number": "视频序列号",
    "videoContentSummary": "内容摘要",
    "detailed_content_description": "详细内容描述",
    "keywords_tags": "关键词标签",
    "main_characters_objects": "主要角色对象",
    "video_source_path": "视频源路径"
  },
  "sample_data": [
    {
      "video_serial_number": "20250321163301122334",
      "videoContentSummary": "一位身着白色上衣的女性正在进行健身操练习",
      "detailed_content_description": "视频展示了一位女性在室内进行健身操练习..."
    }
  ],
  "setup_instructions": {
    "manual_steps": [
      {
        "step": 1,
        "field_name": "视频序列号",
        "field_type": "单行文本",
        "description": "创建单行文本字段，用于存储视频唯一标识符",
        "config_notes": "设置为必填字段"
      },
      {
        "step": 2,
        "field_name": "内容摘要",
        "field_type": "单行文本",
        "description": "创建单行文本字段，用于存储视频内容简短摘要",
        "config_notes": "建议设置字符长度限制"
      },
      {
        "step": 3,
        "field_name": "详细内容描述",
        "field_type": "多行文本",
        "description": "创建多行文本字段，用于存储详细的视频内容描述",
        "config_notes": "支持长文本输入"
      },
      {
        "step": 4,
        "field_name": "关键词标签",
        "field_type": "多行文本",
        "description": "创建多行文本字段，用于存储关键词和标签",
        "config_notes": "可以存储逗号分隔的标签"
      },
      {
        "step": 5,
        "field_name": "主要角色对象",
        "field_type": "单行文本",
        "description": "创建单行文本字段，用于存储主要人物或对象信息",
        "config_notes": "描述性文本字段"
      },
      {
        "step": 6,
        "field_name": "视频源路径",
        "field_type": "单行文本",
        "description": "创建单行文本字段，用于存储视频文件路径",
        "config_notes": "存储文件位置信息"
      }
    ],
    "notes": [
      "创建字段时请保持字段名称与模板完全一致",
      "可根据实际需求调整字段配置和选项",
      "建议按照步骤顺序依次创建字段",
      "完成字段创建后即可开始数据同步"
    ]
  }
}
```

## 常见问题处理

### Q1: 智能设置失败，提示"没有找到历史记录"

**解决方案：**
1. 先分析几个视频文件
2. 确保分析结果不为空
3. 检查数据库连接是否正常

### Q2: 模板生成成功但字段创建困难

**现象：**
```
智能字段模板生成完成！
模板已保存，但手动创建字段时遇到困难
```

**原因分析：**
- 对飞书字段类型不熟悉
- 字段配置选项不清楚
- 字段名称或类型选择有疑问

**解决方案：**
1. 仔细阅读模板文件中的 `setup_instructions` 部分
2. 参考每个字段的 `config_notes` 配置说明
3. 按照 `manual_steps` 的步骤顺序依次创建
4. 如有疑问，可以简化字段类型（如将复杂类型改为文本类型）

### Q3: 字段类型不符合预期

**解决方案：**
1. 查看生成的模板文件
2. 手动修改飞书表格中的字段类型
3. 或者修改 `field_mapper.py` 中的推断规则

## 高级用法

### 1. 自定义字段映射规则

可以通过修改 `field_mapper.py` 来自定义字段类型推断规则：

```python
# 在 field_mapper.py 中添加自定义规则
def custom_field_type_inference(content):
    if "评分" in content:
        return "number"    # 数字字段用于评分
    elif "链接" in content:
        return "url"       # URL字段
    elif "标签" in content:
        return "multi_select"  # 多选字段用于标签
    # ... 更多自定义规则
```

### 2. 模板文件管理

```python
# 加载已有模板文件
import json
with open('templates/previous_template.json', 'r') as f:
    template = json.load(f)
    
# 根据模板手动创建字段
for field in template['feishu_fields']:
    print(f"创建字段：{field['field_name']} ({field['field_type']})")
    # 手动在飞书中创建对应字段
```

### 3. 批量模板生成

```python
# 为不同类型的分析生成不同模板
analysis_types = ["视频内容", "音频转录", "图像识别"]
for analysis_type in analysis_types:
    smart_setup = SmartFieldSetup(db, feishu_client)
    result = smart_setup.run_smart_setup(
        save_template=True,
        template_name=f"{analysis_type}_template"
    )
    print(f"{analysis_type} 模板生成结果：{result['status']}")
```

## 性能优化建议

1. **历史记录数量**：建议分析5-15条记录，过多会影响性能
2. **网络优化**：在网络良好的环境下执行
3. **分批创建**：对于大量字段，系统会自动分批创建
4. **缓存机制**：重复运行时会跳过已存在的字段

## 扩展开发

### 添加新的字段类型支持

1. 在 `FieldMapper` 类中添加新的字段类型：
```python
self.feishu_field_types['custom_type'] = 999
```

2. 添加对应的推断逻辑：
```python
def _detect_custom_type(self, value: str) -> bool:
    # 自定义检测逻辑
    return pattern_match(value)
```

### 集成外部AI服务

可以集成其他AI服务来提高字段类型推断的准确性：

```python
def _ai_enhanced_inference(self, content: str) -> Dict[str, Any]:
    # 调用外部AI服务
    ai_result = external_ai_service.analyze(content)
    return self._merge_inference_results(ai_result, self._basic_inference(content))
```

这个智能字段设置功能大大简化了飞书多维表格的配置过程，让您可以专注于视频内容分析，而不用担心表格结构的设置问题。
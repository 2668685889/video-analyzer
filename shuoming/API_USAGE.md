# Gemini API 使用说明

本文档详细介绍了如何在项目中使用Gemini API进行视频内容分析。

## API概述

本项目使用Google Gemini 2.5 Flash模型，该模型具有以下特点：

- **多模态能力**: 支持文本、图像、视频、音频等多种输入格式
- **视频理解**: 能够分析视频内容、描述场景、回答相关问题
- **长上下文**: 支持处理长时间的视频内容
- **高质量输出**: 提供详细、准确的分析结果

## API配置

### 1. 获取API密钥

1. 访问 [Google AI Studio](https://aistudio.google.com/)
2. 使用Google账户登录
3. 点击"Get API Key"或"创建API密钥"
4. 复制生成的API密钥

### 2. 配置环境变量

在项目根目录的 `.env` 文件中设置：

```bash
GEMINI_API_KEY=your_actual_api_key_here
```

## API使用流程

### 1. 文件上传

```python
from src.api.gemini_client import GeminiClient

# 创建客户端
client = GeminiClient()

# 上传视频文件
upload_result = client.upload_file(
    file_path="/path/to/video.mp4",
    display_name="我的视频"
)

if upload_result['success']:
    file_uri = upload_result['file_uri']
    print(f"文件上传成功: {file_uri}")
else:
    print(f"上传失败: {upload_result['error']}")
```

### 2. 视频分析

```python
# 分析视频内容
analysis_result = client.analyze_video(
    file_uri=file_uri,
    prompt="请详细描述这个视频的内容"
)

if analysis_result['success']:
    print("分析结果:")
    print(analysis_result['result'])
else:
    print(f"分析失败: {analysis_result['error']}")
```

### 3. 一步完成上传和分析

```python
# 直接分析本地视频文件
result = client.analyze_video_with_file(
    file_path="/path/to/video.mp4",
    prompt="分析这个视频的主要内容和情感色彩"
)

if result['success']:
    print("分析结果:", result['result'])
    print("文件信息:", result['file_info'])
else:
    print("错误:", result['error'])
```

## 提示词设计

### 基础提示词模板

#### 1. 视频摘要
```
请详细描述这个视频的内容，包括：
- 主要场景和环境
- 出现的人物或对象
- 主要动作和事件
- 视频的整体主题
```

#### 2. 内容分析
```
分析这个视频的以下方面：
- 主题和核心信息
- 情感色彩和氛围
- 视觉风格和制作质量
- 目标受众和用途
```

#### 3. 时间轴描述
```
请按时间顺序描述视频中发生的主要事件，格式如下：
- 0:00-0:30: [描述]
- 0:30-1:00: [描述]
- ...
```

#### 4. 特定元素识别
```
在这个视频中识别以下元素：
- 文字和标题
- 品牌和标志
- 产品和物品
- 地点和场景
```

### 高级提示词技巧

#### 1. 结构化输出
```
请以JSON格式分析这个视频：
{
  "title": "视频标题",
  "duration": "视频时长",
  "main_topics": ["主题1", "主题2"],
  "key_moments": [
    {"time": "时间点", "description": "描述"}
  ],
  "summary": "整体摘要"
}
```

#### 2. 多语言支持
```
请用中文分析这个视频的内容，如果视频中有其他语言的对话或文字，请翻译成中文。
```

#### 3. 专业领域分析
```
从教育角度分析这个视频：
- 教学目标和内容
- 适合的年龄群体
- 教学方法和技巧
- 学习效果评估
```

## API限制和注意事项

### 1. 文件大小限制

- **单个文件**: 最大2GB
- **请求大小**: 总请求大小（包括文件和文本）不超过20MB时建议使用内联方式
- **推荐**: 大文件使用File API上传

### 2. 视频时长限制

- **2M上下文窗口**: 最长2小时（默认分辨率）或6小时（低分辨率）
- **1M上下文窗口**: 最长1小时（默认分辨率）或3小时（低分辨率）

### 3. 支持的视频格式

- MP4 (推荐)
- AVI
- MOV
- MKV
- WebM

### 4. 处理时间

- **短视频** (< 1分钟): 通常10-30秒
- **中等视频** (1-10分钟): 通常30秒-2分钟
- **长视频** (> 10分钟): 可能需要2-10分钟

### 5. 费用考虑

- 视频处理按帧数计费
- 默认分辨率: 每768x768像素块收费258个token
- 建议优化视频分辨率以控制成本

## 错误处理

### 常见错误类型

#### 1. 认证错误
```python
# 错误信息: "API key not valid"
# 解决方案: 检查API密钥是否正确配置
```

#### 2. 文件格式错误
```python
# 错误信息: "Unsupported file format"
# 解决方案: 确认文件格式在支持列表中
```

#### 3. 文件大小错误
```python
# 错误信息: "File too large"
# 解决方案: 压缩视频或分割成较小的片段
```

#### 4. 网络错误
```python
# 错误信息: "Connection timeout"
# 解决方案: 检查网络连接，重试请求
```

### 错误处理最佳实践

```python
import time
from typing import Dict, Any

def robust_video_analysis(client: GeminiClient, file_path: str, prompt: str, max_retries: int = 3) -> Dict[str, Any]:
    """
    带重试机制的视频分析
    """
    for attempt in range(max_retries):
        try:
            result = client.analyze_video_with_file(file_path, prompt)
            
            if result['success']:
                return result
            
            # 如果是临时错误，等待后重试
            if "timeout" in result.get('error', '').lower():
                time.sleep(2 ** attempt)  # 指数退避
                continue
            
            # 其他错误直接返回
            return result
            
        except Exception as e:
            if attempt == max_retries - 1:
                return {'success': False, 'error': str(e)}
            time.sleep(2 ** attempt)
    
    return {'success': False, 'error': '重试次数已用完'}
```

## 性能优化

### 1. 文件预处理

```python
import subprocess

def optimize_video_for_analysis(input_path: str, output_path: str) -> bool:
    """
    优化视频以提高分析效率
    """
    try:
        # 使用ffmpeg压缩视频
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', 'scale=720:480',  # 降低分辨率
            '-c:v', 'libx264',       # 使用H.264编码
            '-crf', '28',            # 压缩质量
            '-preset', 'fast',       # 编码速度
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False
```

### 2. 批量处理

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def batch_analyze_videos(client: GeminiClient, video_files: list, prompt: str):
    """
    批量分析多个视频文件
    """
    def analyze_single_video(file_path):
        return client.analyze_video_with_file(file_path, prompt)
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, analyze_single_video, file_path)
            for file_path in video_files
        ]
        
        results = await asyncio.gather(*tasks)
        return results
```

## 最佳实践

### 1. 提示词设计

- **具体明确**: 避免模糊的描述，明确指出需要分析的内容
- **结构化**: 使用列表、编号等结构化格式
- **示例引导**: 提供期望输出的示例格式
- **语言一致**: 保持提示词和期望输出的语言一致

### 2. 文件管理

- **格式统一**: 尽量使用MP4格式以获得最佳兼容性
- **大小控制**: 在保证质量的前提下控制文件大小
- **临时清理**: 及时清理上传到API的临时文件

### 3. 错误处理

- **重试机制**: 对临时性错误实施重试
- **用户反馈**: 提供清晰的错误信息给用户
- **日志记录**: 记录详细的错误日志便于调试

### 4. 成本控制

- **预处理**: 在上传前优化视频文件
- **提示优化**: 设计高效的提示词减少重复分析
- **缓存结果**: 对相同文件的分析结果进行缓存
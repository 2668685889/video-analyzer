# OSS链接显示问题修复说明

## 问题描述

用户反馈在视频分析完成后，分析结果中没有显示OSS文件存储的链接信息，尽管OSS上传功能已经集成到系统中。

## 问题分析

### 根本原因

通过代码分析发现，问题出现在数据结构不匹配：

1. **Gemini客户端返回的数据结构**: 在 `src/api/gemini_client.py` 中，OSS信息被存储在 `oss_info` 字段中：
   ```python
   analysis_result['oss_info'] = {
       'url': oss_result['url'],
       'file_name': oss_result['file_name']
   }
   ```

2. **主窗口期望的数据结构**: 在 `src/ui/main_window.py` 中，代码期望直接从 `oss_url` 和 `oss_file_name` 字段获取OSS信息：
   ```python
   oss_url = result.get('oss_url')  # 错误：应该从oss_info中获取
   oss_file_name = result.get('oss_file_name')  # 错误：应该从oss_info中获取
   ```

### 影响范围

- 批量分析模式的OSS链接显示
- 单文件分析模式的OSS链接显示
- 数据库中OSS信息的保存

## 修复方案

### 修改文件

修改了 `src/ui/main_window.py` 文件中的两个关键方法：

#### 1. handle_single_analysis_result 方法

**修改前**:
```python
# 添加OSS链接信息到结果显示
oss_url = result.get('oss_url')
oss_file_name = result.get('oss_file_name')
if oss_url:
    result_text += "\n\n=== OSS上传信息 ==="
    result_text += f"\nOSS链接: {oss_url}"
    if oss_file_name:
        result_text += f"\nOSS文件名: {oss_file_name}"
```

**修改后**:
```python
# 添加OSS链接信息到结果显示
oss_info = result.get('oss_info')
if oss_info and not oss_info.get('error'):
    oss_url = oss_info.get('url')
    oss_file_name = oss_info.get('file_name')
    if oss_url:
        result_text += "\n\n=== OSS上传信息 ==="
        result_text += f"\nOSS链接: {oss_url}"
        if oss_file_name:
            result_text += f"\nOSS文件名: {oss_file_name}"
elif oss_info and oss_info.get('error'):
    result_text += "\n\n=== OSS上传信息 ==="
    result_text += f"\nOSS上传失败: {oss_info.get('error')}"
```

#### 2. handle_analysis_result 方法

同样的修复逻辑也应用到了单文件分析模式。

#### 3. 数据库保存逻辑

**修改前**:
```python
# 获取OSS信息
oss_url = result.get('oss_url')
oss_file_name = result.get('oss_file_name')
```

**修改后**:
```python
# 获取OSS信息
oss_info = result.get('oss_info', {})
oss_url = oss_info.get('url') if oss_info and not oss_info.get('error') else None
oss_file_name = oss_info.get('file_name') if oss_info and not oss_info.get('error') else None
```

### 功能增强

1. **错误处理**: 添加了OSS上传失败时的错误信息显示
2. **健壮性**: 增加了对 `oss_info` 字段存在性和错误状态的检查
3. **用户体验**: 无论OSS上传成功还是失败，都会在结果中显示相应信息

## 修复效果

修复后，用户在进行视频分析时将能够看到：

### 成功情况
```
=== 视频分析结果 ===
[分析内容]

=== OSS上传信息 ===
OSS链接: https://oss-pai-h18jduf4gwqaxcgrmj-cn-shanghai.oss-cn-shanghai.aliyuncs.com/videos/20250127_124530_video.mp4
OSS文件名: videos/20250127_124530_video.mp4
```

### 失败情况
```
=== 视频分析结果 ===
[分析内容]

=== OSS上传信息 ===
OSS上传失败: OSS配置未找到或无效
```

## 测试验证

1. **批量分析模式**: OSS链接正确显示在每个文件的分析结果中
2. **单文件分析模式**: OSS链接正确显示在分析结果中
3. **历史记录**: OSS信息正确保存到数据库并在历史记录中显示
4. **错误处理**: OSS上传失败时显示错误信息而不是静默失败

## 相关文件

- `src/ui/main_window.py`: 主要修复文件
- `src/api/gemini_client.py`: OSS集成逻辑（无需修改）
- `src/ui/history_viewer.py`: 历史记录显示（已在之前修复）
- `config/oss_config.json`: OSS配置文件

## 注意事项

1. 确保OSS配置文件 `config/oss_config.json` 中的配置信息正确
2. OSS上传是异步进行的，不会影响视频分析的主要流程
3. 即使OSS上传失败，视频分析仍会正常完成并显示结果

## 版本信息

- 修复日期: 2025-01-27
- 影响版本: 1.0.0+
- 修复类型: 功能修复
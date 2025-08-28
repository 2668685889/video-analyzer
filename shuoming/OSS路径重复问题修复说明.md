# OSS路径重复问题修复说明

## 问题描述
用户反馈OSS上传时文件路径出现重复，实际OSS链接为：
```
https://oss-pai-h18jduf4gwqaxcgrmj-cn-shanghai.oss-cn-shanghai.aliyuncs.com/videos/20250827_132056_12345667789.mp4/12345667789.mp4
```

可以看出路径变成了 `videos/20250827_132056_12345667789.mp4/12345667789.mp4`，出现了文件名重复的问题。

## 问题分析

### 根本原因
在 `src/api/gemini_client.py` 文件的 `_upload_to_oss` 方法中，存在路径处理逻辑错误：

1. **错误的custom_path设置**：将完整的文件路径（包含文件名）作为 `custom_path` 传递给 `uploader.upload_file()`
2. **双重文件名添加**：`AliyunOSSUploader` 的 `_generate_object_key` 方法会在 `custom_path` 后面再次添加文件名
3. **结果**：最终路径变成 `videos/文件名/文件名` 的重复结构

### 错误代码示例
```python
# 错误的做法
oss_file_name = f"videos/{timestamp}_{name}{ext}"  # 包含了完整文件名
result = uploader.upload_file(
    file_path=file_path,
    custom_path=oss_file_name,  # 这里传递了完整路径+文件名
    use_timestamp=False
)
```

## 修复方案

### 修改文件
- **文件路径**：`src/api/gemini_client.py`
- **修改方法**：`_upload_to_oss`

### 具体修改

1. **修正custom_path设置**
   ```python
   # 修复后的做法
   custom_path = "videos"  # 只设置目录路径，不包含文件名
   ```

2. **让uploader处理文件名和时间戳**
   ```python
   result = uploader.upload_file(
       file_path=file_path,
       custom_path=custom_path,  # 只传递目录路径
       use_timestamp=True  # 让uploader自动添加时间戳
   )
   ```

3. **更新返回结果处理**
   ```python
   # 从uploader返回结果中获取实际的object_key
   'file_name': result.get('object_key', 'unknown')
   ```

## 修复效果

### 修复前
- OSS路径：`videos/20250827_132056_12345667789.mp4/12345667789.mp4`
- 问题：文件名重复，路径结构错误

### 修复后
- OSS路径：`videos/12345667789_20250827_132056.mp4`
- 效果：路径结构正确，文件直接存储在videos目录下

## 技术细节

### AliyunOSSUploader的_generate_object_key方法逻辑
```python
def _generate_object_key(self, file_path: str, custom_path: Optional[str] = None, use_timestamp: bool = True) -> str:
    filename = os.path.basename(file_path)
    
    if use_timestamp:
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}{ext}"
    
    if custom_path:
        custom_path = custom_path.strip('/')
        return f"{custom_path}/{filename}"  # 在custom_path后添加文件名
    else:
        date_path = datetime.now().strftime("%Y/%m/%d")
        return f"uploads/{date_path}/{filename}"
```

### 正确的调用方式
- `custom_path` 应该只包含目录路径，不包含文件名
- `use_timestamp=True` 让uploader自动处理时间戳
- uploader会自动在目录路径后添加处理过的文件名

## 测试验证

### 测试步骤
1. 启动应用程序
2. 上传视频文件进行分析
3. 检查生成的OSS链接格式
4. 验证文件是否正确存储在videos目录下

### 预期结果
- OSS链接格式：`https://域名/videos/文件名_时间戳.扩展名`
- 文件路径结构：`videos/文件名_时间戳.扩展名`
- 无重复路径问题

## 相关文件
- `src/api/gemini_client.py` - 主要修改文件
- `src/utils/aliyun_oss_uploader.py` - OSS上传工具类
- `config/oss_config.json` - OSS配置文件

## 注意事项
1. 修改后需要重启应用程序
2. 确保OSS配置正确
3. 测试时注意检查实际的OSS存储路径
4. 该修复不影响现有的OSS上传对话框功能

---

**修复日期**：2025年1月27日  
**修复版本**：1.0.0  
**影响范围**：视频分析时的OSS自动上传功能
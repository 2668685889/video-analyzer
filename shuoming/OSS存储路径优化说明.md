# OSS存储路径优化说明

## 问题描述

在使用OSS上传功能时，系统总是以文件名称的形式创建多余的文件夹，每次都把上传的文件传到创建的文件夹里面。用户希望能够手动设置一个固定的存储路径，并保存该配置，以后按照设定的路径进行存储，而不是每次都单独创建文件夹。

## 问题分析

### 原有逻辑问题
1. **路径配置无法保存**：存储路径设置无法保存到配置文件中，每次重启应用都需要重新设置
2. **路径处理逻辑**：当用户不设置存储路径时，系统会按日期自动分组，但用户希望有更多控制权
3. **界面说明不清晰**：用户不清楚存储路径的作用和格式要求

### 根本原因
- `_get_config()` 方法中没有包含存储路径配置
- `_load_config()` 方法中没有加载存储路径配置
- 界面缺少对存储路径功能的说明

## 修复方案

### 1. 配置保存和加载优化

**修改文件**: `src/ui/oss_upload_dialog.py`

#### 配置保存修改
```python
def _get_config(self) -> Dict[str, str]:
    """获取OSS配置"""
    config = {
        'access_key_id': self.access_key_id_var.get().strip(),
        'access_key_secret': self.access_key_secret_var.get().strip(),
        'endpoint': self.endpoint_var.get().strip(),
        'bucket_name': self.bucket_name_var.get().strip(),
        'default_storage_path': self.custom_path_var.get().strip()  # 保存默认存储路径
    }
    
    # 验证必填配置
    required_fields = ['access_key_id', 'access_key_secret', 'endpoint', 'bucket_name']
    for key in required_fields:
        if not config[key]:
            raise ValueError(f"请填写{key}")
    
    return config
```

#### 配置加载修改
```python
def _load_config(self):
    """加载OSS配置"""
    try:
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.access_key_id_var.set(config.get('access_key_id', ''))
            self.access_key_secret_var.set(config.get('access_key_secret', ''))
            self.endpoint_var.set(config.get('endpoint', 'oss-cn-hangzhou.aliyuncs.com'))
            self.bucket_name_var.set(config.get('bucket_name', ''))
            self.custom_path_var.set(config.get('default_storage_path', ''))  # 加载默认存储路径
            
            self._log_result("已加载OSS配置")
    except Exception as e:
        self._log_result(f"加载配置失败：{str(e)}")
```

### 2. 界面优化

#### 存储路径说明优化
```python
# 自定义路径
ttk.Label(options_frame, text="存储路径:").grid(row=0, column=0, sticky=tk.W, pady=2)
path_frame = ttk.Frame(options_frame)
path_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
path_frame.columnconfigure(0, weight=1)

self.custom_path_var = tk.StringVar()
self.custom_path_entry = ttk.Entry(path_frame, textvariable=self.custom_path_var, width=30)
self.custom_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

# 路径说明标签
path_desc = ttk.Label(path_frame, text="(留空则按日期自动分组，如: videos/2025/01)", 
                    font=('Arial', 8), foreground='gray')
path_desc.grid(row=1, column=0, sticky=tk.W, pady=(2, 0))
```

### 3. 上传逻辑优化

#### 存储路径处理逻辑
```python
# 获取存储路径
storage_path = self.custom_path_var.get().strip()
# 如果用户设置了存储路径，直接使用；否则传入None让系统自动按日期分组
custom_path = storage_path if storage_path else None

# 上传文件
result = self.uploader.upload_file(
    file_path,
    custom_path=custom_path,
    use_timestamp=self.use_timestamp_var.get(),
    progress_callback=progress_callback,
    overwrite=self.overwrite_var.get(),
    permission=self.permission_var.get()
)
```

## 修复效果

### 1. 功能改进
- **配置持久化**：存储路径配置能够保存到配置文件并在下次启动时自动加载
- **路径控制**：用户可以完全控制文件的存储路径，避免不必要的文件夹创建
- **界面友好**：添加了清晰的说明文字，用户了解如何使用存储路径功能

### 2. 使用方式
- **固定路径**：在"存储路径"字段中输入如 `videos` 或 `documents/2025`，文件将直接存储到该路径下
- **自动分组**：留空存储路径，系统将按日期自动分组，如 `uploads/2025/01/25/`
- **配置保存**：点击"保存配置"按钮，存储路径设置将被保存

### 3. 路径示例
- 设置 `videos` → 文件存储为 `videos/filename.mp4`
- 设置 `projects/demo` → 文件存储为 `projects/demo/filename.mp4`
- 留空 → 文件存储为 `uploads/2025/01/25/filename.mp4`

## 测试验证

### 测试步骤
1. 打开OSS上传对话框
2. 在"存储路径"字段中输入自定义路径（如：`videos`）
3. 点击"保存配置"按钮
4. 选择文件并上传
5. 验证文件是否存储在指定路径下
6. 重启应用，验证存储路径配置是否被正确加载

### 预期结果
- 文件按照用户设定的路径进行存储
- 不会创建以文件名为名的多余文件夹
- 存储路径配置能够持久保存
- 界面说明清晰易懂

## 相关文件

- **主要修改文件**：`src/ui/oss_upload_dialog.py`
- **配置文件**：`config/oss_config.json`
- **依赖文件**：`src/utils/aliyun_oss_uploader.py`

## 注意事项

1. **路径格式**：存储路径不需要以 `/` 开头或结尾，系统会自动处理
2. **路径验证**：系统会自动验证路径格式的正确性
3. **兼容性**：修改保持向后兼容，不影响现有配置文件
4. **权限控制**：存储路径的访问权限仍然受文件权限设置控制

---

**修复完成时间**：2025-01-27  
**修复版本**：v1.0  
**状态**：已完成
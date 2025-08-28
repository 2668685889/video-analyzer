# 阿里云OSS文件上传功能使用说明

## 功能概述

本系统集成了阿里云对象存储（OSS）文件上传功能，允许用户直接从本地上传文件到阿里云OSS存储桶中。该功能支持单文件和批量文件上传，具有进度显示、错误处理等完善的用户体验。

## 主要特性

### 🚀 核心功能
- **单文件上传**：支持选择单个文件进行上传
- **批量上传**：支持选择多个文件或整个文件夹进行批量上传
- **进度显示**：实时显示上传进度，包括单文件进度和总体进度
- **错误处理**：完善的错误处理机制，显示详细的错误信息
- **配置管理**：支持保存和加载OSS配置信息

### 📁 文件管理
- **智能路径**：自动按日期分组存储文件
- **自定义路径**：支持用户自定义存储路径
- **时间戳**：可选择在文件名中添加时间戳避免冲突
- **覆盖控制**：可选择是否覆盖已存在的文件

### 🔧 技术特性
- **大文件支持**：自动使用分片上传处理大文件（>100MB）
- **MD5校验**：确保文件传输完整性
- **MIME类型**：自动识别文件类型
- **连接测试**：支持测试OSS连接是否正常

## 使用前准备

### 1. 安装依赖

确保已安装阿里云OSS SDK：

```bash
pip install oss2>=2.18.0
```

### 2. 获取阿里云OSS配置信息

在使用OSS上传功能前，需要准备以下信息：

#### AccessKey信息
1. 登录[阿里云控制台](https://ecs.console.aliyun.com/)
2. 点击右上角头像 → AccessKey管理
3. 创建或查看AccessKey ID和AccessKey Secret

#### OSS存储桶信息
1. 登录[OSS控制台](https://oss.console.aliyun.com/)
2. 创建或选择一个存储桶（Bucket）
3. 记录存储桶名称和所在地域的Endpoint

#### 常用Endpoint列表
- 华东1（杭州）：`oss-cn-hangzhou.aliyuncs.com`
- 华东2（上海）：`oss-cn-shanghai.aliyuncs.com`
- 华北1（青岛）：`oss-cn-qingdao.aliyuncs.com`
- 华北2（北京）：`oss-cn-beijing.aliyuncs.com`
- 华南1（深圳）：`oss-cn-shenzhen.aliyuncs.com`
- 更多地域请参考[官方文档](https://help.aliyun.com/document_detail/31837.html)

## 使用步骤

### 1. 打开OSS上传功能

在主界面点击 **"OSS上传"** 按钮，打开OSS文件上传对话框。

### 2. 配置OSS连接信息

在对话框的"OSS配置"区域填入以下信息：

- **Access Key ID**：阿里云AccessKey ID
- **Access Key Secret**：阿里云AccessKey Secret
- **Endpoint**：OSS服务端点（如：oss-cn-hangzhou.aliyuncs.com）
- **Bucket名称**：OSS存储桶名称

### 3. 测试连接

点击 **"测试连接"** 按钮验证配置是否正确。如果连接成功，会显示"OSS连接测试成功！"的提示。

### 4. 保存配置

点击 **"保存配置"** 按钮将配置信息保存到本地，下次使用时会自动加载。

### 5. 选择要上传的文件

#### 选择单个或多个文件
点击 **"选择文件"** 按钮，在文件选择对话框中选择要上传的文件。

#### 选择整个文件夹
点击 **"选择文件夹"** 按钮，选择包含要上传文件的文件夹，系统会自动扫描文件夹中的所有文件。

#### 清空文件列表
点击 **"清空列表"** 按钮可以清空当前选择的文件列表。

### 6. 配置上传选项

在"上传选项"区域可以配置：

- **存储路径**：自定义文件在OSS中的存储路径（留空则使用默认的日期分组路径）
- **文件名添加时间戳**：勾选后会在文件名中添加时间戳，避免文件名冲突
- **覆盖已存在文件**：勾选后会覆盖OSS中已存在的同名文件

### 7. 开始上传

点击 **"开始上传"** 按钮开始上传文件。上传过程中可以：

- 查看当前上传文件的进度
- 查看总体上传进度
- 在结果区域查看详细的上传日志
- 点击 **"停止上传"** 按钮取消上传

### 8. 查看上传结果

上传完成后，在"上传结果"区域会显示：

- ✓ 成功上传的文件及其访问URL
- ✗ 上传失败的文件及错误原因
- 总体上传统计信息

## 配置文件说明

### 配置文件位置

OSS配置信息保存在：`config/oss_config.json`

### 配置文件格式

```json
{
  "access_key_id": "your_access_key_id",
  "access_key_secret": "your_access_key_secret",
  "endpoint": "oss-cn-hangzhou.aliyuncs.com",
  "bucket_name": "your_bucket_name"
}
```

### 环境变量配置（可选）

也可以通过环境变量配置OSS信息：

```bash
export ALIYUN_ACCESS_KEY_ID="your_access_key_id"
export ALIYUN_ACCESS_KEY_SECRET="your_access_key_secret"
export ALIYUN_OSS_ENDPOINT="oss-cn-hangzhou.aliyuncs.com"
export ALIYUN_OSS_BUCKET="your_bucket_name"
```

## 文件存储规则

### 默认存储路径

如果不指定自定义路径，文件会按以下规则存储：

```
uploads/YYYY/MM/DD/filename_timestamp.ext
```

例如：`uploads/2025/01/25/document_20250125_143022.pdf`

### 自定义存储路径

可以指定自定义路径，例如：
- `documents/` → `documents/filename.ext`
- `images/2025/` → `images/2025/filename.ext`
- `videos/project1/` → `videos/project1/filename.ext`

### 文件名处理

- **添加时间戳**：`document.pdf` → `document_20250125_143022.pdf`
- **不添加时间戳**：保持原文件名不变
- **冲突处理**：如果不添加时间戳且文件已存在，根据"覆盖已存在文件"选项决定是否覆盖

## 支持的文件类型

系统支持上传所有类型的文件，包括但不限于：

### 图片文件
- JPG/JPEG、PNG、GIF、BMP、TIFF、WebP等

### 视频文件
- MP4、AVI、MOV、WMV、FLV、MKV、WebM等

### 文档文件
- PDF、DOC/DOCX、XLS/XLSX、PPT/PPTX、TXT等

### 音频文件
- MP3、WAV、AAC、FLAC、OGG等

### 压缩文件
- ZIP、RAR、7Z、TAR、GZ等

### 其他文件
- 代码文件、配置文件、数据文件等

## 性能优化

### 大文件处理

- **小文件（≤100MB）**：使用简单上传，速度快
- **大文件（>100MB）**：自动使用分片上传，支持断点续传
- **分片大小**：默认10MB每片，可根据网络情况调整

### 并发控制

- 批量上传时按顺序逐个上传文件
- 避免同时上传过多文件导致网络拥塞
- 支持中途取消上传操作

### 网络优化

- 自动重试机制处理网络波动
- MD5校验确保文件完整性
- 进度回调提供实时反馈

## 错误处理

### 常见错误及解决方案

#### 1. 连接失败
**错误信息**："OSS连接测试失败"

**可能原因**：
- AccessKey信息错误
- Endpoint配置错误
- 网络连接问题
- 存储桶不存在或无权限

**解决方案**：
- 检查AccessKey ID和Secret是否正确
- 确认Endpoint是否与存储桶地域匹配
- 检查网络连接
- 确认存储桶存在且有读写权限

#### 2. 文件上传失败
**错误信息**："文件上传失败"

**可能原因**：
- 文件不存在或已被删除
- 文件正在被其他程序使用
- 存储空间不足
- 文件名包含特殊字符

**解决方案**：
- 确认文件存在且可读
- 关闭正在使用文件的程序
- 检查OSS存储空间
- 避免使用特殊字符命名文件

#### 3. 权限错误
**错误信息**："权限不足"

**可能原因**：
- AccessKey权限不足
- 存储桶访问策略限制
- IP白名单限制

**解决方案**：
- 确认AccessKey具有OSS读写权限
- 检查存储桶访问策略
- 配置IP白名单或使用RAM角色

#### 4. 文件已存在
**错误信息**："文件已存在"

**解决方案**：
- 勾选"覆盖已存在文件"选项
- 或勾选"文件名添加时间戳"选项
- 或手动修改文件名

## 安全注意事项

### 1. AccessKey安全

- **不要**将AccessKey信息硬编码在代码中
- **不要**将包含AccessKey的配置文件提交到版本控制系统
- **建议**使用RAM子账号，只授予必要的OSS权限
- **建议**定期轮换AccessKey

### 2. 存储桶安全

- **建议**设置合适的存储桶访问策略
- **建议**启用访问日志记录
- **建议**配置防盗链设置
- **注意**公共读写权限的安全风险

### 3. 文件安全

- **注意**不要上传包含敏感信息的文件
- **建议**对敏感文件进行加密后再上传
- **建议**设置合适的文件访问权限

## 故障排除

### 1. 检查网络连接

```bash
# 测试网络连通性
ping oss-cn-hangzhou.aliyuncs.com

# 测试端口连通性
telnet oss-cn-hangzhou.aliyuncs.com 80
```

### 2. 验证配置信息

- 登录阿里云控制台确认AccessKey状态
- 确认存储桶名称和地域设置
- 检查RAM权限配置

### 3. 查看详细日志

在上传结果区域查看详细的错误信息和日志，根据具体错误信息进行排查。

### 4. 联系技术支持

如果问题仍无法解决，可以：
- 查看阿里云OSS官方文档
- 联系阿里云技术支持
- 在项目GitHub页面提交Issue

## 相关链接

- [阿里云OSS官方文档](https://help.aliyun.com/product/31815.html)
- [OSS Python SDK文档](https://help.aliyun.com/document_detail/32026.html)
- [阿里云控制台](https://oss.console.aliyun.com/)
- [AccessKey管理](https://usercenter.console.aliyun.com/)

## 更新日志

### v1.0.0 (2025-01-25)
- ✨ 新增OSS文件上传功能
- ✨ 支持单文件和批量文件上传
- ✨ 支持大文件分片上传
- ✨ 支持上传进度显示
- ✨ 支持配置管理和连接测试
- ✨ 完善的错误处理和日志记录

---

**注意**：使用本功能前请确保已正确配置阿里云OSS服务，并具有相应的访问权限。如有疑问，请参考阿里云官方文档或联系技术支持。
# GitHub推送敏感信息保护解决方案

## 问题描述

GitHub的推送保护功能检测到您的代码中包含敏感信息（阿里云AccessKey），阻止了推送操作。

## 错误信息解读

```
remote: error: GH013: Repository rule violations found for refs/heads/main.
remote: - GITHUB PUSH PROTECTION
remote: - Push cannot contain secrets
```

**检测到的敏感信息：**
- Alibaba Cloud AccessKey ID
- Alibaba Cloud AccessKey Secret

**涉及文件：**
- `shuoming/OSS_Endpoint配置错误修复说明.md`
- `shuoming/OSS配置路径问题修复说明.md`

## 解决方案

### 方案一：移除敏感信息（推荐）

1. **编辑涉及的文件**
   ```bash
   # 编辑包含敏感信息的文件
   nano shuoming/OSS_Endpoint配置错误修复说明.md
   nano shuoming/OSS配置路径问题修复说明.md
   ```

2. **替换真实密钥为示例格式**
   ```
   # 将真实的AccessKey替换为：
   access_key_id = "LTAI5t***********"  # 您的AccessKey ID
   access_key_secret = "2Bb***********"  # 您的AccessKey Secret
   
   # 或者使用占位符：
   access_key_id = "YOUR_ACCESS_KEY_ID"
   access_key_secret = "YOUR_ACCESS_KEY_SECRET"
   ```

3. **提交修改**
   ```bash
   git add .
   git commit -m "移除敏感信息，使用示例格式"
   git push -u origin main
   ```

### 方案二：使用GitHub允许推送（不推荐）

如果您确定要推送包含敏感信息的内容，可以点击GitHub提供的链接：
- [允许AccessKey ID](https://github.com/2668685889/video-analyzer/security/secret-scanning/unblock-secret/31uZ8rInBDHrDYhtkOAjmnj5xYl)
- [允许AccessKey Secret](https://github.com/2668685889/video-analyzer/security/secret-scanning/unblock-secret/31uZ8wOXzbRI1qfFWgYfPj5QPX3)

⚠️ **安全警告：** 不建议将真实的AccessKey推送到公开仓库

## 最佳实践

### 1. 使用环境变量
```python
import os

# 在代码中使用环境变量
access_key_id = os.getenv('ALIBABA_ACCESS_KEY_ID')
access_key_secret = os.getenv('ALIBABA_ACCESS_KEY_SECRET')
```

### 2. 使用配置文件模板
```json
// config/oss_config.json.example
{
    "access_key_id": "YOUR_ACCESS_KEY_ID",
    "access_key_secret": "YOUR_ACCESS_KEY_SECRET",
    "endpoint": "YOUR_ENDPOINT",
    "bucket_name": "YOUR_BUCKET_NAME"
}
```

### 3. 更新.gitignore
```
# 添加到.gitignore
config/oss_config.json
.env
*.key
*.secret
```

## 快速修复步骤

1. **立即执行以下命令：**
   ```bash
   # 编辑文件，移除真实密钥
   sed -i '' 's/LTAI5t[A-Za-z0-9]*/LTAI5t***********/g' shuoming/OSS_*.md
   sed -i '' 's/2Bb[A-Za-z0-9]*/2Bb***********/g' shuoming/OSS_*.md
   
   # 提交修改
   git add .
   git commit -m "安全修复：移除敏感AccessKey信息"
   git push -u origin main
   ```

2. **验证推送成功后，GitHub Actions将自动开始编译**

## 后续操作

推送成功后：
- ✅ GitHub Actions自动编译Windows程序
- ✅ 生成可执行文件和安装包
- ✅ 自动发布到Releases
- ✅ 专业的版本管理

## 常见问题

**Q: 为什么GitHub会检测敏感信息？**
A: GitHub有自动扫描功能，防止意外泄露API密钥、密码等敏感信息。

**Q: 移除敏感信息后会影响功能吗？**
A: 不会，文档中的示例代码使用占位符即可，实际使用时用户会配置自己的密钥。

**Q: 如何避免以后再次出现这个问题？**
A: 在文档中始终使用示例格式，真实密钥通过环境变量或配置文件管理。

---

**安全提醒：** 永远不要将真实的API密钥、密码等敏感信息提交到代码仓库中！
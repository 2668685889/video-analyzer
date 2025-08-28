# GitHub Actions Windows编译使用指南

## 🎯 方案一：GitHub Actions自动编译完整操作指南

### 📋 前提条件

1. **GitHub账户**：确保您有GitHub账户
2. **项目仓库**：将项目上传到GitHub仓库
3. **权限设置**：确保仓库有Actions权限

### 🚀 第一步：上传项目到GitHub

#### 1.1 初始化Git仓库（如果还没有）

```bash
# 在项目根目录执行
git init
git add .
git commit -m "Initial commit: 视频分析工具项目"
```

#### 1.2 创建GitHub仓库

1. 访问 [GitHub](https://github.com)
2. 点击右上角的 "+" 按钮
3. 选择 "New repository"
4. 填写仓库信息：
   - Repository name: `video-analyzer` (或您喜欢的名称)
   - Description: `视频分析工具 - 支持多平台的智能视频内容分析系统`
   - 选择 Public 或 Private
   - 不要勾选 "Initialize this repository with a README"

#### 1.3 推送代码到GitHub

```bash
# 添加远程仓库
git remote add origin https://github.com/您的用户名/video-analyzer.git

# 推送代码
git branch -M main
git push -u origin main
```

### 🔧 第二步：启用GitHub Actions

#### 2.1 检查Actions权限

1. 进入您的GitHub仓库
2. 点击 "Settings" 标签
3. 在左侧菜单中找到 "Actions" → "General"
4. 确保选择了 "Allow all actions and reusable workflows"

#### 2.2 验证工作流文件

确认以下文件已存在于您的仓库中：
- `.github/workflows/build-windows.yml`

如果文件不存在，请确保推送时包含了这个文件。

### 🎮 第三步：触发自动编译

#### 3.1 方式一：推送代码触发

```bash
# 任何推送到main分支的代码都会触发编译
git add .
git commit -m "触发Windows编译"
git push origin main
```

#### 3.2 方式二：手动触发

1. 进入GitHub仓库
2. 点击 "Actions" 标签
3. 在左侧选择 "Build Windows Executable"
4. 点击右侧的 "Run workflow" 按钮
5. 选择分支（通常是main）
6. 点击绿色的 "Run workflow" 按钮

#### 3.3 方式三：创建标签触发发布

```bash
# 创建版本标签，会自动编译并发布到Releases
git tag v1.0.0
git push origin v1.0.0
```

### 📊 第四步：监控编译过程

#### 4.1 查看编译状态

1. 进入GitHub仓库的 "Actions" 页面
2. 找到最新的 "Build Windows Executable" 工作流
3. 点击进入查看详细状态

#### 4.2 编译过程说明

编译过程包含以下步骤：
- ✅ 检出代码
- ✅ 设置Python环境
- ✅ 缓存pip依赖
- ✅ 升级pip
- ✅ 安装项目依赖
- ✅ 清理缓存文件
- ✅ 编译Windows可执行文件
- ✅ 验证编译结果
- ✅ 创建发布包
- ✅ 上传编译产物

### 📦 第五步：下载编译结果

#### 5.1 下载Artifacts（编译产物）

1. 在Actions页面找到成功的编译任务
2. 点击进入任务详情
3. 在页面底部找到 "Artifacts" 部分
4. 下载 "VideoAnalyzer-Windows-3.12" 文件

#### 5.2 下载Release版本（如果使用标签触发）

1. 进入仓库主页
2. 点击右侧的 "Releases"
3. 找到对应版本
4. 下载 "VideoAnalyzer-Windows-*.zip" 文件

### 🎯 第六步：使用编译结果

#### 6.1 解压和运行

1. 解压下载的zip文件
2. 找到 "VideoAnalyzer.exe" 文件
3. 双击运行（首次运行可能需要几秒钟）

#### 6.2 分发给其他用户

- 将整个解压后的文件夹发送给用户
- 用户只需双击 "VideoAnalyzer.exe" 即可运行
- 无需安装Python或其他依赖

### 🔄 自动化工作流程

#### 开发流程

```
开发代码 → 推送到GitHub → 自动编译 → 下载使用
     ↓
创建标签 → 自动发布 → 用户下载
```

#### 版本发布流程

```bash
# 1. 完成开发
git add .
git commit -m "完成新功能开发"
git push origin main

# 2. 创建版本标签
git tag v1.1.0
git push origin v1.1.0

# 3. 自动编译和发布
# GitHub Actions会自动：
# - 编译Windows版本
# - 创建Release
# - 上传可执行文件
```

### ⚠️ 常见问题和解决方案

#### Q1: Actions权限被拒绝
**解决方案：**
1. 检查仓库Settings → Actions → General
2. 确保启用了Actions权限
3. 如果是组织仓库，联系管理员开启权限

#### Q2: 编译失败
**解决方案：**
1. 查看Actions日志中的错误信息
2. 检查requirements.txt是否包含所有依赖
3. 确保main.spec文件配置正确

#### Q3: 下载的文件无法运行
**解决方案：**
1. 确保下载了完整的文件夹
2. 检查Windows系统版本（建议Windows 10+）
3. 临时关闭杀毒软件重试

#### Q4: 编译时间过长
**解决方案：**
- 正常情况下编译需要5-10分钟
- 首次编译可能需要更长时间
- 可以通过缓存优化（已在配置中启用）

### 📈 高级功能

#### 自定义编译触发条件

可以修改 `.github/workflows/build-windows.yml` 中的触发条件：

```yaml
# 只在特定分支触发
on:
  push:
    branches: [ main, release ]

# 只在特定路径变化时触发
on:
  push:
    paths:
      - 'src/**'
      - 'main.py'
      - 'requirements.txt'
```

#### 多版本编译

当前配置支持Python 3.12，可以扩展支持多个版本：

```yaml
strategy:
  matrix:
    python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
```

### 🎉 总结

使用GitHub Actions方案的优势：

1. **完全自动化**：推送代码即可触发编译
2. **无需本地环境**：在云端Windows环境编译
3. **版本管理**：自动创建Release和版本标签
4. **多人协作**：团队成员都可以触发编译
5. **免费使用**：GitHub提供免费的Actions额度
6. **专业分发**：通过GitHub Releases专业分发

现在您可以按照这个指南，轻松实现在macOS上开发，自动编译Windows版本的完整工作流程！
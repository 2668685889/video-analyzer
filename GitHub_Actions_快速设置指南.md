# 🚀 GitHub Actions 快速设置指南

## 📋 当前状态

✅ **已完成的准备工作：**
- Git仓库已初始化
- 项目文件已添加到Git
- GitHub Actions工作流文件已配置 (`.github/workflows/build-windows.yml`)
- 初始提交已创建

## 🎯 接下来需要做的3个步骤

### 第1步：创建GitHub仓库

1. 打开浏览器，访问 [GitHub](https://github.com)
2. 点击右上角的 "+" 按钮 → "New repository"
3. 填写仓库信息：
   - **Repository name**: `video-analyzer` (或您喜欢的名称)
   - **Description**: `视频分析工具 - 支持多平台的智能视频内容分析系统`
   - 选择 **Public** 或 **Private**
   - ⚠️ **重要**: 不要勾选 "Initialize this repository with a README"
4. 点击 "Create repository"

### 第2步：推送代码到GitHub

复制GitHub页面显示的命令，或者使用以下命令：

```bash
# 添加远程仓库（替换为您的GitHub用户名和仓库名）
git remote add origin https://github.com/您的用户名/video-analyzer.git

# 设置主分支
git branch -M main

# 推送代码
git push -u origin main
```

### 第3步：触发自动编译

推送完成后，有3种方式触发编译：

#### 方式1：自动触发（推荐）
代码推送后会自动开始编译，无需额外操作。

#### 方式2：手动触发
1. 进入GitHub仓库页面
2. 点击 "Actions" 标签
3. 选择 "Build Windows Executable"
4. 点击 "Run workflow" → "Run workflow"

#### 方式3：版本发布
```bash
# 创建版本标签（会自动发布到Releases）
git tag v1.0.0
git push origin v1.0.0
```

## 📊 监控编译过程

1. 进入GitHub仓库的 "Actions" 页面
2. 查看 "Build Windows Executable" 工作流状态
3. 编译大约需要 5-10 分钟

## 📦 下载编译结果

### 下载方式1：Artifacts（推荐）
1. 在Actions页面找到成功的编译任务
2. 点击进入任务详情
3. 在页面底部找到 "Artifacts"
4. 下载 "VideoAnalyzer-Windows-3.12.zip"

### 下载方式2：Releases（如果使用了标签）
1. 进入仓库主页
2. 点击右侧的 "Releases"
3. 下载对应版本的zip文件

## 🎉 使用编译结果

1. 解压下载的zip文件
2. 找到 "VideoAnalyzer.exe" 文件
3. 双击运行（首次运行可能需要几秒钟）
4. 可以将整个文件夹分发给其他用户使用

## ⚠️ 常见问题

**Q: 编译失败怎么办？**
A: 查看Actions页面的错误日志，通常是依赖问题，检查requirements.txt文件。

**Q: 下载的文件无法运行？**
A: 确保下载了完整的文件夹，Windows系统版本建议Windows 10+。

**Q: Actions权限被拒绝？**
A: 检查仓库Settings → Actions → General，确保启用了Actions权限。

## 🔄 后续开发流程

```
修改代码 → git add . → git commit -m "更新说明" → git push
     ↓
  自动触发编译 → 下载新版本
```

---

**💡 提示**: 完成设置后，每次推送代码都会自动编译Windows版本，非常方便！

**📞 需要帮助**: 如有问题，请查看详细的 `shuoming/GitHub_Actions_Windows编译使用指南.md` 文件。
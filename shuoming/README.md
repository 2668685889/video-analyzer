# Gemini视频内容识别客户端

这是一个基于Google Gemini API的视频内容识别客户端应用程序，支持上传视频文件并使用AI分析视频内容。

## 功能特性

- 🎥 **视频文件上传**: 支持多种视频格式（MP4、AVI、MOV、MKV、WebM）
- 🤖 **AI内容分析**: 使用Gemini 2.5 Flash模型分析视频内容
- 💬 **自定义提示**: 支持自定义分析提示，获得针对性的分析结果
- 🎯 **预设提示**: 提供常用的分析模板（视频摘要、内容分析、时间轴等）
- 💾 **结果保存**: 支持将分析结果保存为文本文件
- 🖥️ **图形界面**: 友好的图形用户界面，操作简单直观
- ⚡ **异步处理**: 后台处理视频分析，不阻塞用户界面

## 系统要求

- **操作系统**: macOS / Windows / Linux
- **Python版本**: 3.7 或更高版本
- **网络连接**: 需要稳定的网络连接访问Gemini API
- **API密钥**: 有效的Google Gemini API密钥

## 安装步骤

### 1. 克隆或下载项目

```bash
# 如果使用Git
git clone <项目地址>
cd ceshishipin

# 或直接下载并解压项目文件
```

### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 3. 配置API密钥

1. 复制环境变量模板文件：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，添加您的Gemini API密钥：
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### 4. 获取Gemini API密钥

1. 访问 [Google AI Studio](https://aistudio.google.com/)
2. 登录您的Google账户
3. 创建新的API密钥
4. 将API密钥复制到 `.env` 文件中

## 使用方法

### 启动应用程序

```bash
python main.py
```

### 使用步骤

1. **选择视频文件**
   - 点击"浏览文件"按钮
   - 选择要分析的视频文件
   - 支持的格式：MP4、AVI、MOV、MKV、WebM
   - 最大文件大小：100MB（可在配置中修改）

2. **输入分析提示**
   - 在"分析提示"文本框中输入您的问题或要求
   - 或点击预设提示按钮快速选择常用模板

3. **开始分析**
   - 点击"开始分析"按钮
   - 程序会自动上传文件并调用Gemini API进行分析
   - 分析过程中界面会显示进度状态

4. **查看结果**
   - 分析完成后，结果会显示在"分析结果"区域
   - 可以点击"保存结果"将分析结果保存为文本文件

## 配置选项

可以在 `.env` 文件中配置以下选项：

```bash
# 必需配置
GEMINI_API_KEY=your_gemini_api_key_here

# 可选配置
MAX_FILE_SIZE_MB=100                    # 最大文件大小（MB）
SUPPORTED_VIDEO_FORMATS=mp4,avi,mov,mkv,webm  # 支持的视频格式
```

## 项目结构

```
ceshishipin/
├── main.py                 # 主程序入口
├── requirements.txt        # Python依赖包
├── .env.example           # 环境变量模板
├── .env                   # 环境变量配置（需要创建）
├── src/                   # 源代码目录
│   ├── __init__.py
│   ├── api/               # API相关模块
│   │   ├── __init__.py
│   │   └── gemini_client.py
│   ├── ui/                # 用户界面模块
│   │   ├── __init__.py
│   │   └── main_window.py
│   └── utils/             # 工具模块
│       ├── __init__.py
│       ├── config.py
│       ├── file_validator.py
│       └── file_handler.py
└── shuoming/              # 说明文档目录
    ├── README.md
    ├── API_USAGE.md
    └── TROUBLESHOOTING.md
```

## 常见问题

### 1. API密钥相关

**Q: 如何获取Gemini API密钥？**
A: 访问 [Google AI Studio](https://aistudio.google.com/)，登录后创建新的API密钥。

**Q: API密钥配置后仍然提示未配置？**
A: 请检查 `.env` 文件是否在项目根目录，且格式正确（`GEMINI_API_KEY=your_key`）。

### 2. 文件上传相关

**Q: 支持哪些视频格式？**
A: 目前支持 MP4、AVI、MOV、MKV、WebM 格式。

**Q: 文件大小有限制吗？**
A: 默认限制为100MB，可以在 `.env` 文件中修改 `MAX_FILE_SIZE_MB` 参数。

### 3. 分析相关

**Q: 分析需要多长时间？**
A: 分析时间取决于视频大小和内容复杂度，通常在1-5分钟之间。

**Q: 可以分析多长的视频？**
A: Gemini 2.5模型支持最长2小时的视频（默认分辨率）或6小时（低分辨率）。

## 技术支持

如果遇到问题，请查看：

1. [故障排除指南](TROUBLESHOOTING.md)
2. [API使用说明](API_USAGE.md)
3. 检查控制台输出的错误信息
4. 确认网络连接和API密钥有效性

## 许可证

本项目仅供学习和研究使用。使用Gemini API需要遵守Google的服务条款。

## 更新日志

### v1.0.0 (2024-01-20)
- 初始版本发布
- 支持视频文件上传和内容分析
- 图形用户界面
- 预设分析提示
- 结果保存功能
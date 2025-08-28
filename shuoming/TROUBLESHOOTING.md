# 故障排除指南

本文档提供了使用Gemini视频内容识别客户端时可能遇到的常见问题及其解决方案。

## 安装和配置问题

### 1. 依赖包安装失败

**问题**: 运行 `pip install -r requirements.txt` 时出现错误

**可能原因和解决方案**:

#### Python版本不兼容
```bash
# 检查Python版本
python --version
# 或
python3 --version

# 确保使用Python 3.7+
# 如果版本过低，请升级Python
```

#### 网络连接问题
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 或使用阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

#### 权限问题（macOS/Linux）
```bash
# 使用用户安装
pip install --user -r requirements.txt

# 或使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 2. API密钥配置问题

**问题**: 提示"Gemini API密钥未配置"

**解决步骤**:

1. **检查.env文件是否存在**
   ```bash
   ls -la .env
   ```
   如果不存在，复制模板文件：
   ```bash
   cp .env.example .env
   ```

2. **检查.env文件内容**
   ```bash
   cat .env
   ```
   确保格式正确：
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

3. **验证API密钥有效性**
   - 确保API密钥没有多余的空格或换行符
   - 确保API密钥是从Google AI Studio获取的有效密钥
   - 检查API密钥是否已过期

**问题**: API密钥配置正确但仍然报错

**解决方案**:
```bash
# 检查环境变量是否正确加载
python -c "from src.utils.config import config; print(config.gemini_api_key[:10] + '...')" 

# 重启应用程序
# 确保.env文件在项目根目录
```

## 文件上传问题

### 3. 文件格式不支持

**问题**: 提示"不支持的文件格式"

**解决方案**:

1. **检查文件扩展名**
   - 支持的格式：mp4, avi, mov, mkv, webm
   - 确保文件扩展名正确

2. **转换文件格式**
   ```bash
   # 使用ffmpeg转换为MP4格式
   ffmpeg -i input_video.avi -c:v libx264 -c:a aac output_video.mp4
   ```

3. **检查MIME类型**
   ```bash
   # 在macOS/Linux上检查文件类型
   file your_video_file.mp4
   ```

### 4. 文件大小超限

**问题**: 提示"文件大小超过限制"

**解决方案**:

1. **压缩视频文件**
   ```bash
   # 使用ffmpeg压缩视频
   ffmpeg -i input.mp4 -vf scale=720:480 -c:v libx264 -crf 28 output.mp4
   ```

2. **修改大小限制**
   在.env文件中增加：
   ```
   MAX_FILE_SIZE_MB=200
   ```

3. **分割长视频**
   ```bash
   # 分割视频为10分钟的片段
   ffmpeg -i input.mp4 -c copy -map 0 -segment_time 600 -f segment output%03d.mp4
   ```

### 5. 文件上传超时

**问题**: 上传过程中出现超时错误

**解决方案**:

1. **检查网络连接**
   ```bash
   # 测试网络连接
   ping google.com
   ```

2. **重试上传**
   - 程序会自动重试，请耐心等待
   - 如果多次失败，尝试压缩文件后重新上传

3. **使用有线网络**
   - WiFi不稳定时，尝试使用有线网络连接

## API调用问题

### 6. API调用失败

**问题**: 分析过程中出现API错误

**常见错误和解决方案**:

#### 认证失败
```
错误: "API key not valid" 或 "Authentication failed"
解决: 检查API密钥是否正确，是否已过期
```

#### 配额超限
```
错误: "Quota exceeded" 或 "Rate limit exceeded"
解决: 等待一段时间后重试，或检查API使用配额
```

#### 服务不可用
```
错误: "Service unavailable" 或 "Internal server error"
解决: 这是临时性问题，稍后重试
```

### 7. 分析结果异常

**问题**: 分析结果不准确或不完整

**解决方案**:

1. **优化提示词**
   ```
   # 不好的提示
   "分析视频"
   
   # 好的提示
   "请详细描述这个视频的内容，包括主要场景、人物、动作和关键信息。请按时间顺序组织描述。"
   ```

2. **检查视频质量**
   - 确保视频清晰度足够
   - 避免过度压缩的视频
   - 检查视频是否损坏

3. **调整分析策略**
   - 对于长视频，考虑分段分析
   - 使用更具体的提示词
   - 尝试不同的分析角度

## 界面和操作问题

### 8. 程序启动失败

**问题**: 双击main.py或运行命令后程序无响应

**解决步骤**:

1. **检查Python环境**
   ```bash
   python main.py
   # 查看控制台输出的错误信息
   ```

2. **检查依赖包**
   ```bash
   python -c "import tkinter; print('tkinter OK')"
   python -c "from google import genai; print('genai OK')"
   ```

3. **检查图形界面支持**
   ```bash
   # 在Linux上可能需要安装tkinter
   sudo apt-get install python3-tk  # Ubuntu/Debian
   sudo yum install tkinter         # CentOS/RHEL
   ```

### 9. 界面显示异常

**问题**: 界面布局混乱或按钮无响应

**解决方案**:

1. **调整窗口大小**
   - 手动拖拽调整窗口大小
   - 最小窗口大小为600x500像素

2. **重启程序**
   - 关闭程序后重新启动
   - 清除可能的临时状态

3. **检查系统兼容性**
   - 确保操作系统支持tkinter
   - 在不同操作系统上测试

### 10. 分析过程卡住

**问题**: 点击"开始分析"后程序无响应

**解决方案**:

1. **检查网络连接**
   - 确保网络连接稳定
   - 检查防火墙设置

2. **等待处理完成**
   - 大文件分析需要较长时间
   - 观察状态栏的进度提示

3. **重启程序**
   - 如果长时间无响应，重启程序
   - 尝试分析较小的文件

## 性能问题

### 11. 程序运行缓慢

**问题**: 程序响应速度慢

**优化方案**:

1. **系统资源检查**
   ```bash
   # 检查内存使用
   top
   # 或
   htop
   ```

2. **文件预处理**
   - 压缩大视频文件
   - 降低视频分辨率
   - 使用MP4格式

3. **关闭其他程序**
   - 释放系统内存
   - 确保网络带宽充足

### 12. 内存不足

**问题**: 处理大文件时出现内存错误

**解决方案**:

1. **增加虚拟内存**
   - 在系统设置中增加交换文件大小

2. **分割处理**
   - 将大视频分割成小片段
   - 分别处理后合并结果

3. **优化文件**
   - 降低视频分辨率
   - 减少视频时长

## 日志和调试

### 13. 启用详细日志

如果遇到难以诊断的问题，可以启用详细日志：

```python
# 在main.py开头添加
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 14. 常用调试命令

```bash
# 检查Python环境
python --version
pip list

# 检查文件权限
ls -la .env
ls -la main.py

# 测试API连接
python -c "from src.api.gemini_client import GeminiClient; client = GeminiClient(); print('API连接正常')"

# 检查文件格式
file your_video.mp4
```

## 获取帮助

如果以上解决方案都无法解决您的问题，请：

1. **收集错误信息**
   - 完整的错误消息
   - 操作系统和Python版本
   - 问题复现步骤

2. **检查官方文档**
   - [Gemini API文档](https://ai.google.dev/gemini-api/docs)
   - [Google AI Studio](https://aistudio.google.com/)

3. **社区支持**
   - 搜索相关的技术论坛
   - 查看GitHub Issues（如果项目开源）

## 预防措施

为了避免常见问题，建议：

1. **定期更新**
   - 保持Python和依赖包的最新版本
   - 关注API的更新和变化

2. **备份配置**
   - 备份.env配置文件
   - 记录重要的设置参数

3. **测试环境**
   - 在正式使用前进行充分测试
   - 使用小文件验证功能正常

4. **监控使用**
   - 定期检查API使用配额
   - 监控程序性能和资源使用
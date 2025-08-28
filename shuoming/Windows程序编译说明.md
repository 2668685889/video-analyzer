# Windows程序编译说明

## 概述

本文档详细说明了如何将Python视频分析工具编译成Windows可执行程序的完整过程。

## 编译环境要求

### 系统要求
- Windows 10/11 (推荐)
- Python 3.8 或更高版本
- 至少 2GB 可用磁盘空间

### 必要工具
- PyInstaller 6.0+
- 项目所有依赖包（见 requirements.txt）

## 编译步骤

### 方法一：使用批处理脚本（推荐）

1. **准备项目文件**
   ```bash
   # 将整个项目文件夹复制到Windows系统
   # 确保包含以下关键文件：
   # - main.py
   # - main.spec
   # - build_windows.bat
   # - requirements.txt
   # - src/ 文件夹
   # - config/ 文件夹
   ```

2. **运行编译脚本**
   ```cmd
   # 右键点击 build_windows.bat
   # 选择"以管理员身份运行"
   # 或在命令提示符中执行：
   build_windows.bat
   ```

3. **等待编译完成**
   - 脚本会自动安装依赖
   - 自动清理旧的构建文件
   - 执行PyInstaller打包
   - 完成后在 `dist/` 文件夹中生成可执行文件

### 方法二：手动编译

1. **安装依赖**
   ```cmd
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **清理旧文件**
   ```cmd
   rmdir /s /q build
   rmdir /s /q dist
   ```

3. **执行编译**
   ```cmd
   pyinstaller main.spec --clean --noconfirm
   ```

## 编译配置说明

### main.spec 文件配置

```python
# 主要配置项说明：

# 入口文件
['main.py']

# 数据文件包含
datas=[
    ('config', 'config'),           # 配置文件夹
    ('shuoming', 'shuoming'),       # 说明文档
    ('扣子工作流', '扣子工作流'),      # 工作流文件
    ('.env.example', '.'),          # 环境变量示例
    ('requirements.txt', '.'),      # 依赖列表
    ('custom_field_mapping.json', '.'), # 字段映射配置
]

# 隐式导入模块
hiddenimports=[
    'tkinter',                      # GUI框架
    'sqlite3',                      # 数据库
    'requests',                     # HTTP请求
    # ... 其他必要模块
]

# 排除的模块（避免冲突）
excludes=[
    'PyQt5', 'PyQt6',              # Qt框架
    'matplotlib', 'numpy',          # 科学计算库
    # ... 其他不需要的大型库
]
```

### 编译参数说明

- `--clean`: 清理临时文件
- `--noconfirm`: 自动确认覆盖
- `console=False`: 无控制台窗口（GUI程序）
- `upx=True`: 启用UPX压缩

## 生成的文件结构

```
dist/
└── VideoAnalyzer.exe          # 主可执行文件（约45-50MB）
```

## 部署说明

### 文件分发
1. 将 `dist/VideoAnalyzer.exe` 复制到目标Windows系统
2. 确保目标系统有必要的运行时库（通常Windows 10/11自带）
3. 首次运行时需要配置相关设置

### 运行要求
- Windows 10/11 系统
- 网络连接（用于API调用）
- 足够的磁盘空间存储分析结果

## 常见问题解决

### 编译错误

1. **Qt冲突错误**
   ```
   ERROR: multiple Qt bindings packages
   ```
   **解决方案**: 已在spec文件中排除冲突的Qt包

2. **模块缺失错误**
   ```
   ModuleNotFoundError: No module named 'xxx'
   ```
   **解决方案**: 在spec文件的hiddenimports中添加缺失模块

3. **权限错误**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   **解决方案**: 以管理员身份运行编译脚本

### 运行时错误

1. **DLL缺失**
   - 安装 Microsoft Visual C++ Redistributable
   - 确保Windows系统更新到最新

2. **配置文件错误**
   - 检查 .env 文件配置
   - 确保API密钥正确设置

## 优化建议

### 减小文件大小
1. 启用UPX压缩（已配置）
2. 排除不必要的模块（已配置）
3. 使用 `--exclude-module` 排除特定模块

### 提高启动速度
1. 使用 `--onefile` 选项（可选）
2. 优化hiddenimports列表
3. 减少数据文件包含

## 技术细节

### 跨平台兼容性
- 在macOS上编译的程序无法直接在Windows运行
- 必须在目标平台上重新编译
- 使用相同的spec配置确保一致性

### 依赖管理
- 所有Python依赖都会被打包到可执行文件中
- 系统级依赖（如DLL）需要单独处理
- 建议在干净的Python环境中编译

## 版本信息

- 编译工具: PyInstaller 6.14.2
- Python版本: 3.12+
- 目标平台: Windows 10/11
- 生成文件: VideoAnalyzer.exe

## 更新日志

### v1.0 (2025-01-28)
- 初始版本
- 支持完整功能打包
- 包含所有必要依赖
- 提供自动化编译脚本

---

**注意**: 本文档基于当前项目结构编写，如有代码更新，请相应更新编译配置。
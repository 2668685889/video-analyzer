@echo off
chcp 65001 >nul
echo ========================================
echo 视频分析工具 Windows 打包脚本 v2.0
echo ========================================

echo [1/6] 检查 Python 安装...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [2/6] 升级 pip...
python -m pip install --upgrade pip

echo [3/6] 安装项目依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)

echo [4/6] 安装 PyInstaller...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo 错误: PyInstaller 安装失败
    pause
    exit /b 1
)

echo [5/6] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

echo [6/6] 开始打包（这可能需要几分钟）...
pyinstaller main.spec --clean --noconfirm --log-level INFO
if %errorlevel% neq 0 (
    echo 错误: 打包失败，请检查错误信息
    echo 常见问题:
    echo - 确保所有依赖都已正确安装
    echo - 检查是否有杀毒软件阻止
    echo - 确保有足够的磁盘空间
    pause
    exit /b 1
)

echo.
echo ========================================
echo 🎉 打包完成！
echo ========================================
echo 📁 可执行文件位置: dist\VideoAnalyzer\
echo 📄 主程序: VideoAnalyzer.exe
echo 📦 文件大小: 
for %%I in ("dist\VideoAnalyzer\VideoAnalyzer.exe") do echo    %%~zI 字节
echo.
echo 💡 使用说明:
echo 1. 将整个 VideoAnalyzer 文件夹复制到目标电脑
echo 2. 双击 VideoAnalyzer.exe 运行程序
echo 3. 首次运行可能需要几秒钟加载时间
echo.
echo ⚠️  注意事项:
echo - 请保持 VideoAnalyzer 文件夹完整，不要单独复制 .exe 文件
echo - 如遇到杀毒软件报警，请添加信任
echo - 建议在 Windows 10/11 上运行
echo ========================================
pause
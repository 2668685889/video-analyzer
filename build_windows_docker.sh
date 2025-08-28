#!/bin/bash

# 使用Docker在macOS上编译Windows版本的脚本
# 作者：视频分析工具开发团队
# 版本：1.0

set -e  # 遇到错误立即退出

echo "========================================"
echo "🐳 Docker Windows编译脚本 v1.0"
echo "========================================"
echo

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误：未找到Docker"
    echo "请先安装Docker Desktop：https://www.docker.com/products/docker-desktop"
    exit 1
fi

# 检查Docker是否运行
if ! docker info &> /dev/null; then
    echo "❌ 错误：Docker未运行"
    echo "请启动Docker Desktop后重试"
    exit 1
fi

echo "✅ Docker环境检查通过"
echo

# 清理旧的构建
echo "🧹 清理旧的构建文件..."
rm -rf dist-windows
mkdir -p dist-windows

# 构建Docker镜像
echo "🏗️  构建Windows编译环境（首次运行可能需要较长时间）..."
docker build -f Dockerfile.windows -t video-analyzer-windows . || {
    echo "❌ Docker镜像构建失败"
    echo "常见问题："
    echo "1. 检查网络连接"
    echo "2. 确保Dockerfile.windows文件存在"
    echo "3. 检查Docker磁盘空间"
    exit 1
}

echo "✅ Docker镜像构建完成"
echo

# 运行编译
echo "⚙️  开始编译Windows可执行文件..."
docker run --rm -v "$(pwd)/dist-windows:/output" video-analyzer-windows || {
    echo "❌ 编译失败"
    echo "请检查编译日志中的错误信息"
    exit 1
}

# 检查编译结果
if [ -f "dist-windows/VideoAnalyzer/VideoAnalyzer.exe" ]; then
    echo
    echo "========================================"
    echo "🎉 编译成功！"
    echo "========================================"
    echo "📁 输出目录: dist-windows/VideoAnalyzer/"
    echo "📄 主程序: VideoAnalyzer.exe"
    
    # 显示文件大小
    if command -v du &> /dev/null; then
        size=$(du -sh "dist-windows/VideoAnalyzer" | cut -f1)
        echo "📦 文件夹大小: $size"
    fi
    
    echo
    echo "💡 使用说明:"
    echo "1. 将 dist-windows/VideoAnalyzer 文件夹复制到Windows电脑"
    echo "2. 双击 VideoAnalyzer.exe 运行程序"
    echo "3. 首次运行可能需要几秒钟加载时间"
    echo
    echo "⚠️  注意事项:"
    echo "- 请保持VideoAnalyzer文件夹完整"
    echo "- 如遇杀毒软件报警，请添加信任"
    echo "- 建议在Windows 10/11上运行"
    echo "========================================"
else
    echo "❌ 编译失败：未找到可执行文件"
    echo "请检查编译过程中的错误信息"
    exit 1
fi

# 清理Docker镜像（可选）
read -p "🗑️  是否删除Docker镜像以节省空间？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker rmi video-analyzer-windows
    echo "✅ Docker镜像已删除"
else
    echo "💾 Docker镜像已保留，下次编译会更快"
fi

echo
echo "🎯 编译完成！Windows版本已准备就绪。"
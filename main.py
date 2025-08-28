#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini视频内容识别客户端 - 主程序入口

这是一个基于Gemini API的视频内容识别客户端应用程序。
支持上传视频文件并使用AI分析视频内容。

使用方法:
    python main.py

要求:
    - Python 3.7+
    - 有效的Gemini API密钥
    - 安装所需依赖包（见requirements.txt）
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.ui.main_window import MainWindow
    from src.utils.config import config
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保已安装所有依赖包: pip install -r requirements.txt")
    sys.exit(1)

def check_dependencies():
    """
    检查依赖包是否已安装
    
    Returns:
        bool: 依赖包是否完整
    """
    required_packages = [
        'google.genai',
        'dotenv',
        'PIL'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行以下命令安装依赖包:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def check_configuration():
    """
    检查配置是否正确
    
    Returns:
        bool: 配置是否有效
    """
    if not config.is_valid():
        print("配置检查失败:")
        print("- Gemini API密钥未配置")
        print("\n请按以下步骤配置:")
        print("1. 复制 .env.example 为 .env")
        print("2. 在 .env 文件中设置您的 GEMINI_API_KEY")
        print("3. 重新运行程序")
        return False
    
    return True

def show_startup_info():
    """
    显示启动信息
    """
    print("="*50)
    print("Gemini视频内容识别客户端")
    print("版本: 1.0.0")
    print("="*50)
    print(f"支持的视频格式: {', '.join(config.get_supported_formats())}")
    print(f"最大文件大小: {config.max_file_size_mb}MB")
    print("="*50)

def main():
    """
    主函数
    """
    try:
        # 显示启动信息
        show_startup_info()
        
        # 检查依赖包
        print("检查依赖包...")
        if not check_dependencies():
            return 1
        print("✓ 依赖包检查通过")
        
        # 检查配置
        print("检查配置...")
        if not check_configuration():
            return 1
        print("✓ 配置检查通过")
        
        print("启动应用程序...")
        print("="*50)
        
        # 创建并运行主窗口
        app = MainWindow()
        app.run()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        return 0
    except Exception as e:
        print(f"程序运行时发生错误: {e}")
        
        # 如果是图形界面错误，显示错误对话框
        try:
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            messagebox.showerror(
                "程序错误", 
                f"程序运行时发生错误:\n{str(e)}\n\n请检查配置和依赖包是否正确安装。"
            )
            root.destroy()
        except:
            pass
        
        return 1

if __name__ == "__main__":
    # 设置程序退出码
    exit_code = main()
    sys.exit(exit_code)
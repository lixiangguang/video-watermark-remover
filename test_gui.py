##########test_gui.py: [GUI测试脚本] ##################
# 变更记录: [2025-01-27] @李祥光 [创建GUI测试脚本]########
# 输入: [无] | 输出: [测试结果]###############

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("正在测试GUI组件...")
    
    # 测试tkinter
    import tkinter as tk
    print("✓ tkinter 导入成功")
    
    # 测试PIL
    from PIL import Image, ImageTk
    print("✓ PIL 导入成功")
    
    # 测试cv2
    import cv2
    print("✓ OpenCV 导入成功")
    
    # 测试numpy
    import numpy as np
    print("✓ NumPy 导入成功")
    
    # 测试自定义模块
    from watermark_remover import WatermarkRemover
    print("✓ WatermarkRemover 导入成功")
    
    from utils.logger import setup_logger
    print("✓ Logger 导入成功")
    
    print("\n所有依赖检查通过！")
    print("正在启动GUI...")
    
    # 导入并启动GUI
    from watermark_gui import WatermarkGUI
    
    app = WatermarkGUI()
    print("GUI初始化成功，正在显示窗口...")
    app.run()
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请检查依赖是否正确安装")
except Exception as e:
    print(f"❌ 运行错误: {e}")
    import traceback
    traceback.print_exc()

print("测试完成")

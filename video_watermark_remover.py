##########video_watermark_remover.py: 视频去水印处理工具 ##################
# 变更记录: [2025-06-25] @李祥光 [初始创建视频去水印功能]########
# 输入: [视频文件路径/文件夹路径] | 输出: [处理后的无水印视频文件]###############


###########################文件下的所有函数###########################
"""
main：主程序入口，处理命令行参数和用户交互
process_video：处理单个视频文件的去水印操作
process_video_folder：批量处理文件夹中的视频文件
get_video_files：获取指定文件夹中的所有视频文件
setup_directories：创建必要的输出目录
validate_input_path：验证输入路径的有效性
"""
###########################文件下的所有函数###########################

#########mermaid格式说明所有函数的调用关系说明开始#########
"""
flowchart TD
    A[程序启动] --> B[main函数]
    B --> C{检查命令行参数}
    C -->|有参数| D[validate_input_path验证路径]
    C -->|无参数| E[显示交互菜单]
    D --> F{判断输入类型}
    F -->|文件| G[process_video处理单个视频]
    F -->|文件夹| H[process_video_folder批量处理]
    H --> I[get_video_files获取视频列表]
    I --> J[循环调用process_video]
    G --> K[setup_directories创建输出目录]
    J --> K
    K --> L[WatermarkRemover去水印]
    L --> M[保存处理结果]
"""
#########mermaid格式说明所有函数的调用关系说明结束#########

import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional
import cv2
import numpy as np

# 导入水印去除库
try:
    from watermark_remover import WatermarkRemover
except ImportError:
    print("错误：未找到 watermark_remover 库，请先安装相关依赖")
    print("安装命令：pip install watermark-remover")
    sys.exit(1)


def setup_directories() -> None:
    """
    setup_directories 功能说明:
    # 创建项目所需的目录结构
    # 输入: [无] | 输出: [无，创建目录结构]
    """
    directories = [
        "output",  # 输出视频目录
        "logs",    # 日志文件目录
        "temp",    # 临时文件目录
        "config"   # 配置文件目录
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ 创建目录: {directory}")


def validate_input_path(path: str) -> bool:
    """
    validate_input_path 功能说明:
    # 验证输入路径是否有效（文件或文件夹）
    # 输入: [path: str 文件或文件夹路径] | 输出: [bool 路径是否有效]
    """
    if not os.path.exists(path):
        print(f"❌ 错误：路径不存在 - {path}")
        return False
    
    if os.path.isfile(path):
        # 检查是否为视频文件
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v']
        if not any(path.lower().endswith(ext) for ext in video_extensions):
            print(f"❌ 错误：不支持的视频格式 - {path}")
            return False
    
    return True


def get_video_files(folder_path: str) -> List[str]:
    """
    get_video_files 功能说明:
    # 获取指定文件夹中的所有视频文件
    # 输入: [folder_path: str 文件夹路径] | 输出: [List[str] 视频文件路径列表]
    """
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v']
    video_files = []
    
    for file in os.listdir(folder_path):
        if any(file.lower().endswith(ext) for ext in video_extensions):
            video_files.append(os.path.join(folder_path, file))
    
    return sorted(video_files)


def process_video(input_path: str, output_dir: str = "output") -> bool:
    """
    process_video 功能说明:
    # 处理单个视频文件，去除水印
    # 输入: [input_path: str 输入视频路径, output_dir: str 输出目录] | 输出: [bool 处理是否成功]
    """
    try:
        print(f"\n🎬 开始处理视频: {os.path.basename(input_path)}")
        
        # 创建输出文件名
        input_name = Path(input_path).stem
        output_path = os.path.join(output_dir, f"{input_name}_no_watermark.mp4")
        
        # 初始化水印去除器
        remover = WatermarkRemover()
        
        # 处理视频
        print("📊 正在分析视频...")
        result = remover.remove_watermark(input_path, output_path)
        
        if result:
            print(f"✅ 处理完成: {output_path}")
            return True
        else:
            print(f"❌ 处理失败: {input_path}")
            return False
            
    except Exception as e:
        print(f"❌ 处理出错: {str(e)}")
        return False


def process_video_folder(folder_path: str, output_dir: str = "output") -> None:
    """
    process_video_folder 功能说明:
    # 批量处理文件夹中的所有视频文件
    # 输入: [folder_path: str 文件夹路径, output_dir: str 输出目录] | 输出: [无，批量处理结果]
    """
    video_files = get_video_files(folder_path)
    
    if not video_files:
        print(f"❌ 在文件夹 {folder_path} 中未找到视频文件")
        return
    
    print(f"\n📁 发现 {len(video_files)} 个视频文件")
    print("🚀 开始批量处理...\n")
    
    success_count = 0
    failed_count = 0
    
    for i, video_file in enumerate(video_files, 1):
        print(f"[{i}/{len(video_files)}] 处理进度")
        
        if process_video(video_file, output_dir):
            success_count += 1
        else:
            failed_count += 1
        
        print("-" * 50)
    
    # 显示处理结果统计
    print(f"\n📊 批量处理完成！")
    print(f"✅ 成功: {success_count} 个文件")
    print(f"❌ 失败: {failed_count} 个文件")
    print(f"📁 输出目录: {output_dir}")


def main():
    """
    main 功能说明:
    # 主程序入口，处理命令行参数和用户交互
    # 输入: [命令行参数] | 输出: [程序执行结果]
    """
    print("🎬 视频去水印工具 v1.0")
    print("=" * 40)
    
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description='视频去水印处理工具')
    parser.add_argument('input', nargs='?', help='输入视频文件或文件夹路径')
    parser.add_argument('--output', '-o', default='output', help='输出目录 (默认: output)')
    
    args = parser.parse_args()
    
    # 创建必要的目录
    setup_directories()
    
    # 如果没有提供输入参数，显示交互菜单
    if not args.input:
        print("\n请选择操作模式:")
        print("1. 处理单个视频文件")
        print("2. 批量处理文件夹")
        print("3. 退出程序")
        
        while True:
            choice = input("\n请输入选择 (1-3): ").strip()
            
            if choice == '1':
                input_path = input("请输入视频文件路径: ").strip().strip('"')
                if validate_input_path(input_path) and os.path.isfile(input_path):
                    process_video(input_path, args.output)
                break
                
            elif choice == '2':
                input_path = input("请输入文件夹路径: ").strip().strip('"')
                if validate_input_path(input_path) and os.path.isdir(input_path):
                    process_video_folder(input_path, args.output)
                break
                
            elif choice == '3':
                print("👋 程序退出")
                sys.exit(0)
                
            else:
                print("❌ 无效选择，请重新输入")
    
    else:
        # 处理命令行参数
        if not validate_input_path(args.input):
            sys.exit(1)
        
        if os.path.isfile(args.input):
            process_video(args.input, args.output)
        elif os.path.isdir(args.input):
            process_video_folder(args.input, args.output)
    
    print("\n🎉 程序执行完成！")


if __name__ == "__main__":
    main()
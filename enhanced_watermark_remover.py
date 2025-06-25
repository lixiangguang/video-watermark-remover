##########enhanced_watermark_remover.py: 增强版视频去水印工具 ##################
# 变更记录: [2025-06-25] @李祥光 [创建增强版去水印工具，集成日志和配置]########
# 输入: [视频文件路径/文件夹路径，配置参数] | 输出: [处理后的无水印视频文件]###############


###########################文件下的所有函数###########################
"""
main：主程序入口，处理命令行参数和用户交互
process_video_enhanced：增强版单个视频处理功能
process_video_folder_enhanced：增强版批量处理功能
get_video_files_with_info：获取视频文件及其信息
validate_and_prepare：验证输入并准备处理环境
show_processing_menu：显示处理选项菜单
get_user_config：获取用户配置参数
cleanup_temp_files：清理临时文件
"""
###########################文件下的所有函数###########################

#########mermaid格式说明所有函数的调用关系说明开始#########
"""
flowchart TD
    A[程序启动] --> B[main函数]
    B --> C[validate_and_prepare验证准备]
    C --> D[show_processing_menu显示菜单]
    D --> E{用户选择}
    E -->|单个文件| F[process_video_enhanced]
    E -->|批量处理| G[process_video_folder_enhanced]
    G --> H[get_video_files_with_info]
    H --> I[循环调用process_video_enhanced]
    F --> J[WatermarkRemover处理]
    I --> J
    J --> K[log_processing_end记录日志]
    K --> L[cleanup_temp_files清理]
"""
#########mermaid格式说明所有函数的调用关系说明结束#########

import os
import sys
import time
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import cv2
import numpy as np

# 导入项目模块
from config.config import get_default_config, get_supported_formats, PRESET_CONFIGS
from utils.logger import (
    setup_logger, log_info, log_warning, log_error,
    log_processing_start, log_processing_end, log_batch_summary
)

# 导入水印去除库
try:
    from watermark_remover import WatermarkRemover
except ImportError:
    print("❌ 错误：未找到 watermark_remover 库")
    print("📦 请先安装依赖：pip install -r requirements.txt")
    sys.exit(1)


def validate_and_prepare() -> bool:
    """
    validate_and_prepare 功能说明:
    # 验证环境并准备必要的目录结构
    # 输入: [无] | 输出: [bool 准备是否成功]
    """
    try:
        # 创建必要的目录
        directories = ['output', 'logs', 'temp', 'config']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        # 初始化日志系统
        setup_logger()
        log_info("🚀 视频去水印工具启动")
        log_info("✅ 目录结构创建完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        return False


def get_video_files_with_info(folder_path: str) -> List[Dict[str, any]]:
    """
    get_video_files_with_info 功能说明:
    # 获取文件夹中的视频文件及其详细信息
    # 输入: [folder_path: str 文件夹路径] | 输出: [List[Dict] 视频文件信息列表]
    """
    supported_formats = get_supported_formats()
    video_files = []
    
    try:
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(file.lower())
                if ext in supported_formats['input_formats']:
                    file_size = os.path.getsize(file_path)
                    file_size_mb = file_size / (1024 * 1024)
                    
                    video_info = {
                        'path': file_path,
                        'name': file,
                        'size_mb': round(file_size_mb, 2),
                        'format': ext
                    }
                    video_files.append(video_info)
        
        log_info(f"📁 在 {folder_path} 中找到 {len(video_files)} 个视频文件")
        return video_files
        
    except Exception as e:
        log_error(f"获取视频文件信息失败", e)
        return []


def get_user_config() -> Dict[str, any]:
    """
    get_user_config 功能说明:
    # 获取用户自定义配置参数
    # 输入: [无] | 输出: [Dict 用户配置字典]
    """
    print("\n⚙️  配置参数设置")
    print("可选预设配置:")
    print("1. 快速模式 (fast) - 速度优先")
    print("2. 平衡模式 (balanced) - 速度与质量平衡 [推荐]")
    print("3. 精确模式 (precise) - 质量优先")
    print("4. 自定义配置")
    
    choice = input("\n请选择配置模式 (1-4, 默认2): ").strip() or '2'
    
    if choice == '1':
        return PRESET_CONFIGS['fast']
    elif choice == '2':
        return PRESET_CONFIGS['balanced']
    elif choice == '3':
        return PRESET_CONFIGS['precise']
    elif choice == '4':
        config = get_default_config()
        print("\n🔧 自定义配置:")
        
        threshold = input(f"阈值分割灰度值 (当前: {config['threshold']}): ").strip()
        if threshold:
            config['threshold'] = int(threshold)
        
        kernel_size = input(f"核大小 (当前: {config['kernel_size']}): ").strip()
        if kernel_size:
            config['kernel_size'] = int(kernel_size)
        
        return config
    else:
        return PRESET_CONFIGS['balanced']


def process_video_enhanced(video_path: str, config: Dict[str, any]) -> Tuple[bool, str]:
    """
    process_video_enhanced 功能说明:
    # 增强版单个视频处理功能，包含详细日志和错误处理
    # 输入: [video_path: str 视频路径, config: Dict 配置参数] | 输出: [Tuple[bool, str] 处理结果和输出路径]
    """
    start_time = time.time()
    
    try:
        # 记录处理开始
        log_processing_start(video_path, config)
        
        # 生成输出文件路径
        input_filename = os.path.basename(video_path)
        name, ext = os.path.splitext(input_filename)
        output_path = os.path.join("output", f"{name}_no_watermark{ext}")
        
        # 检查输出文件是否已存在
        if os.path.exists(output_path) and not config.get('overwrite_existing', False):
            log_warning(f"输出文件已存在，跳过处理: {output_path}")
            return False, output_path
        
        # 创建水印去除器实例
        remover = WatermarkRemover(
            threshold=config['threshold'],
            kernel_size=config['kernel_size']
        )
        
        print(f"🎬 正在处理: {input_filename}")
        print(f"⚙️  参数: 阈值={config['threshold']}, 核大小={config['kernel_size']}")
        
        # 执行去水印处理
        remover.remove_video_watermark(video_path, output_path)
        
        # 验证输出文件
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            duration = time.time() - start_time
            log_processing_end(video_path, True, duration, output_path)
            print(f"✅ 处理完成: {os.path.basename(output_path)}")
            return True, output_path
        else:
            raise Exception("输出文件创建失败或为空")
        
    except Exception as e:
        duration = time.time() - start_time
        log_processing_end(video_path, False, duration)
        log_error(f"处理视频失败: {os.path.basename(video_path)}", e)
        print(f"❌ 处理失败: {str(e)}")
        return False, ""


def process_video_folder_enhanced(folder_path: str, config: Dict[str, any]) -> None:
    """
    process_video_folder_enhanced 功能说明:
    # 增强版批量处理功能，包含进度显示和统计信息
    # 输入: [folder_path: str 文件夹路径, config: Dict 配置参数] | 输出: [无，批量处理结果]
    """
    start_time = time.time()
    
    # 获取视频文件信息
    video_files = get_video_files_with_info(folder_path)
    
    if not video_files:
        log_warning(f"在文件夹 {folder_path} 中未找到支持的视频文件")
        return
    
    # 显示文件列表
    print(f"\n📋 找到 {len(video_files)} 个视频文件:")
    total_size = 0
    for i, video_info in enumerate(video_files, 1):
        print(f"  {i}. {video_info['name']} ({video_info['size_mb']} MB)")
        total_size += video_info['size_mb']
    
    print(f"📊 总大小: {total_size:.2f} MB")
    
    # 确认处理
    confirm = input("\n是否继续批量处理？(y/N): ").strip().lower()
    if confirm not in ['y', 'yes', '是']:
        print("❌ 用户取消操作")
        return
    
    # 批量处理
    success_count = 0
    failed_count = 0
    
    print(f"\n🚀 开始批量处理...")
    
    for i, video_info in enumerate(video_files, 1):
        print(f"\n[{i}/{len(video_files)}] 处理进度: {(i-1)/len(video_files)*100:.1f}%")
        
        success, output_path = process_video_enhanced(video_info['path'], config)
        
        if success:
            success_count += 1
        else:
            failed_count += 1
    
    # 记录批处理汇总
    total_time = time.time() - start_time
    log_batch_summary(len(video_files), success_count, failed_count, total_time)
    
    print(f"\n🎉 批量处理完成！")
    print(f"📊 统计: 成功 {success_count}/{len(video_files)}, 失败 {failed_count}")
    print(f"⏱️  总耗时: {total_time:.2f} 秒")


def show_processing_menu() -> str:
    """
    show_processing_menu 功能说明:
    # 显示处理选项菜单
    # 输入: [无] | 输出: [str 用户选择]
    """
    print("\n🎬 视频去水印工具 v2.0 (增强版)")
    print("=" * 50)
    print("请选择操作:")
    print("1. 处理单个视频文件")
    print("2. 批量处理文件夹中的视频")
    print("3. 查看支持的视频格式")
    print("4. 退出")
    
    return input("\n请输入选择 (1-4): ").strip()


def cleanup_temp_files() -> None:
    """
    cleanup_temp_files 功能说明:
    # 清理临时文件
    # 输入: [无] | 输出: [无]
    """
    try:
        temp_dir = "temp"
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            log_info("🧹 临时文件清理完成")
    except Exception as e:
        log_warning(f"清理临时文件时出错: {str(e)}")


def main():
    """
    main 功能说明:
    # 增强版主程序入口
    # 输入: [命令行参数] | 输出: [程序执行结果]
    """
    # 初始化环境
    if not validate_and_prepare():
        return
    
    try:
        # 解析命令行参数
        parser = argparse.ArgumentParser(description='增强版视频去水印处理工具')
        parser.add_argument('input_path', nargs='?', help='输入视频文件或文件夹路径')
        parser.add_argument('--preset', '-p', choices=['fast', 'balanced', 'precise'], 
                          default='balanced', help='预设配置模式')
        parser.add_argument('--threshold', '-t', type=int, help='阈值分割灰度值')
        parser.add_argument('--kernel-size', '-k', type=int, help='核大小')
        
        args = parser.parse_args()
        
        # 获取配置
        if args.input_path:
            # 命令行模式
            if args.threshold or args.kernel_size:
                config = get_default_config()
                if args.threshold:
                    config['threshold'] = args.threshold
                if args.kernel_size:
                    config['kernel_size'] = args.kernel_size
            else:
                config = PRESET_CONFIGS[args.preset]
            
            if not os.path.exists(args.input_path):
                log_error(f"路径不存在: {args.input_path}")
                return
            
            if os.path.isfile(args.input_path):
                process_video_enhanced(args.input_path, config)
            else:
                process_video_folder_enhanced(args.input_path, config)
        
        else:
            # 交互模式
            while True:
                choice = show_processing_menu()
                
                if choice == '1':
                    video_path = input("请输入视频文件路径: ").strip().strip('"')
                    if os.path.exists(video_path) and os.path.isfile(video_path):
                        config = get_user_config()
                        process_video_enhanced(video_path, config)
                    else:
                        print("❌ 文件不存在或路径无效")
                
                elif choice == '2':
                    folder_path = input("请输入文件夹路径: ").strip().strip('"')
                    if os.path.exists(folder_path) and os.path.isdir(folder_path):
                        config = get_user_config()
                        process_video_folder_enhanced(folder_path, config)
                    else:
                        print("❌ 文件夹不存在或路径无效")
                
                elif choice == '3':
                    formats = get_supported_formats()
                    print("\n📋 支持的视频格式:")
                    for fmt in formats['input_formats']:
                        print(f"  • {fmt}")
                
                elif choice == '4':
                    break
                
                else:
                    print("❌ 无效选择，请重新输入")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        log_info("用户中断程序执行")
    
    except Exception as e:
        log_error("程序执行出错", e)
        print(f"❌ 程序出错: {str(e)}")
    
    finally:
        # 清理工作
        cleanup_temp_files()
        log_info("🏁 程序结束")
        print("\n👋 感谢使用视频去水印工具！")


if __name__ == "__main__":
    main()
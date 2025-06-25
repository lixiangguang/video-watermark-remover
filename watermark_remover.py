##########watermark_remover.py: [视频水印去除核心模块] ##################
# 变更记录: [2025-01-27] @李祥光 [创建水印去除核心功能]########
# 输入: [视频文件路径，配置参数] | 输出: [去水印后的视频文件]###############


###########################文件下的所有函数###########################
"""
WatermarkRemover：水印去除器主类
remove_video_watermark：视频水印去除主方法
detect_watermark_region：检测水印区域
process_frame：处理单帧图像
create_mask：创建水印掩码
inpaint_frame：修复帧图像
"""
###########################文件下的所有函数###########################

#########mermaid格式说明所有函数的调用关系说明开始#########
"""
flowchart TD
    A[WatermarkRemover初始化] --> B[remove_video_watermark]
    B --> C[读取视频]
    C --> D[detect_watermark_region检测水印]
    D --> E[逐帧处理]
    E --> F[process_frame处理帧]
    F --> G[create_mask创建掩码]
    G --> H[inpaint_frame修复]
    H --> I[写入输出视频]
"""
#########mermaid格式说明所有函数的调用关系说明结束#########

import cv2
import numpy as np
from typing import Tuple, Optional
import os
from tqdm import tqdm


class WatermarkRemover:
    """
    WatermarkRemover 功能说明:
    # 视频水印去除器，使用OpenCV实现水印检测和去除
    # 输入: [threshold: int 阈值, kernel_size: int 核大小] | 输出: [WatermarkRemover实例]
    """
    
    def __init__(self, threshold: int = 60, kernel_size: int = 5, iterations: int = 3):
        self.threshold = threshold
        self.kernel_size = kernel_size
        self.iterations = iterations
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    
    def detect_watermark_region(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        detect_watermark_region 功能说明:
        # 检测帧中的水印区域
        # 输入: [frame: np.ndarray 输入帧] | 输出: [Optional[np.ndarray] 水印掩码]
        """
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 使用阈值分割检测水印
            _, binary = cv2.threshold(gray, self.threshold, 255, cv2.THRESH_BINARY)
            
            # 形态学操作去除噪声
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, self.kernel, iterations=self.iterations)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, self.kernel, iterations=self.iterations)
            
            return binary
            
        except Exception as e:
            print(f"❌ 水印检测失败: {str(e)}")
            return None
    
    def create_mask(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        create_mask 功能说明:
        # 创建水印掩码用于修复
        # 输入: [frame: np.ndarray 输入帧] | 输出: [Optional[np.ndarray] 修复掩码]
        """
        try:
            watermark_mask = self.detect_watermark_region(frame)
            if watermark_mask is None:
                return None
            
            # 扩展掩码区域以确保完全覆盖水印
            dilate_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.kernel_size + 2, self.kernel_size + 2))
            mask = cv2.dilate(watermark_mask, dilate_kernel, iterations=2)
            
            return mask
            
        except Exception as e:
            print(f"❌ 掩码创建失败: {str(e)}")
            return None
    
    def inpaint_frame(self, frame: np.ndarray, mask: np.ndarray) -> Optional[np.ndarray]:
        """
        inpaint_frame 功能说明:
        # 使用图像修复技术去除水印
        # 输入: [frame: np.ndarray 输入帧, mask: np.ndarray 掩码] | 输出: [Optional[np.ndarray] 修复后的帧]
        """
        try:
            # 使用快速行进修复算法
            inpainted = cv2.inpaint(frame, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
            return inpainted
            
        except Exception as e:
            print(f"❌ 图像修复失败: {str(e)}")
            return frame  # 返回原始帧
    
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        process_frame 功能说明:
        # 处理单帧图像，去除水印
        # 输入: [frame: np.ndarray 输入帧] | 输出: [np.ndarray 处理后的帧]
        """
        try:
            # 创建水印掩码
            mask = self.create_mask(frame)
            if mask is None:
                return frame
            
            # 检查掩码是否有效（是否检测到水印）
            if np.sum(mask) < 100:  # 如果掩码区域太小，可能没有检测到水印
                return frame
            
            # 修复水印区域
            result = self.inpaint_frame(frame, mask)
            return result if result is not None else frame
            
        except Exception as e:
            print(f"❌ 帧处理失败: {str(e)}")
            return frame
    
    def remove_video_watermark(self, input_path: str, output_path: str) -> bool:
        """
        remove_video_watermark 功能说明:
        # 去除视频中的水印
        # 输入: [input_path: str 输入视频路径, output_path: str 输出视频路径] | 输出: [bool 处理是否成功]
        """
        try:
            # 打开输入视频
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                print(f"❌ 无法打开视频文件: {input_path}")
                return False
            
            # 获取视频属性
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(f"📹 视频信息: {width}x{height}, {fps}fps, {total_frames}帧")
            
            # 设置视频编码器
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                print(f"❌ 无法创建输出视频文件: {output_path}")
                cap.release()
                return False
            
            # 处理每一帧
            frame_count = 0
            with tqdm(total=total_frames, desc="处理进度", unit="帧") as pbar:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # 处理当前帧
                    processed_frame = self.process_frame(frame)
                    
                    # 写入输出视频
                    out.write(processed_frame)
                    
                    frame_count += 1
                    pbar.update(1)
            
            # 释放资源
            cap.release()
            out.release()
            
            print(f"✅ 视频处理完成: {output_path}")
            print(f"📊 处理统计: 共处理 {frame_count} 帧")
            
            return True
            
        except Exception as e:
            print(f"❌ 视频处理失败: {str(e)}")
            return False
        
        finally:
            # 确保资源被释放
            try:
                cap.release()
                out.release()
            except:
                pass


if __name__ == "__main__":
    # 测试代码
    print("🧪 WatermarkRemover 模块测试")
    remover = WatermarkRemover(threshold=60, kernel_size=5)
    print(f"✅ 水印去除器初始化成功 (阈值: {remover.threshold}, 核大小: {remover.kernel_size})")

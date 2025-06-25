##########watermark_gui.py: [视频水印区域选择GUI界面] ##################
# 变更记录: [2025-01-27] @李祥光 [创建图形界面用于选择水印区域]########
# 输入: [视频文件路径] | 输出: [水印区域坐标和处理后的视频]###############


###########################文件下的所有函数###########################
"""
WatermarkGUI：主GUI类
load_video：加载视频文件
show_frame：显示视频帧
select_watermark_area：选择水印区域
process_with_selected_area：使用选定区域处理视频
update_preview：更新预览
save_config：保存配置
load_config：加载配置
"""
###########################文件下的所有函数###########################

#########mermaid格式说明所有函数的调用关系说明开始#########
"""
flowchart TD
    A[启动GUI] --> B[WatermarkGUI初始化]
    B --> C[load_video加载视频]
    C --> D[show_frame显示帧]
    D --> E[select_watermark_area选择区域]
    E --> F[update_preview更新预览]
    F --> G[process_with_selected_area处理]
    G --> H[save_config保存配置]
"""
#########mermaid格式说明所有函数的调用关系说明结束#########

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import os
import json
from typing import Tuple, Optional, List
from watermark_remover import WatermarkRemover
from utils.logger import setup_logger, log_info, log_error


class WatermarkGUI:
    """
    WatermarkGUI 功能说明:
    # 视频水印区域选择的图形用户界面
    # 输入: [无] | 输出: [GUI应用实例]
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("智能视频去水印工具 - 区域选择")
        self.root.geometry("1200x800")
        
        # 初始化变量
        self.video_path = None
        self.cap = None
        self.current_frame = None
        self.watermark_areas = []  # 存储多个水印区域
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
        
        # 设置日志
        setup_logger()
        
        # 创建界面
        self.create_widgets()
        
        # 绑定事件
        self.bind_events()
    
    def create_widgets(self):
        """
        create_widgets 功能说明:
        # 创建GUI界面组件
        # 输入: [无] | 输出: [无，创建界面元素]
        """
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_frame.pack_propagate(False)
        
        # 文件选择
        file_frame = ttk.Frame(control_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(file_frame, text="选择视频文件", command=self.load_video).pack(fill=tk.X)
        
        self.file_label = ttk.Label(file_frame, text="未选择文件", wraplength=280)
        self.file_label.pack(fill=tk.X, pady=(5, 0))
        
        # 帧控制
        frame_control = ttk.LabelFrame(control_frame, text="帧控制")
        frame_control.pack(fill=tk.X, pady=10)
        
        self.frame_scale = ttk.Scale(frame_control, from_=0, to=100, orient=tk.HORIZONTAL)
        self.frame_scale.pack(fill=tk.X, padx=5, pady=5)
        self.frame_scale.bind("<Motion>", self.on_frame_change)
        
        self.frame_info = ttk.Label(frame_control, text="帧: 0/0")
        self.frame_info.pack(pady=5)
        
        # 水印区域列表
        area_frame = ttk.LabelFrame(control_frame, text="水印区域")
        area_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 区域列表
        self.area_listbox = tk.Listbox(area_frame, height=6)
        self.area_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 区域操作按钮
        area_btn_frame = ttk.Frame(area_frame)
        area_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(area_btn_frame, text="删除选中", command=self.delete_selected_area).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(area_btn_frame, text="清空全部", command=self.clear_all_areas).pack(side=tk.LEFT)
        
        # 处理参数
        param_frame = ttk.LabelFrame(control_frame, text="处理参数")
        param_frame.pack(fill=tk.X, pady=10)
        
        # 阈值
        ttk.Label(param_frame, text="阈值:").pack(anchor=tk.W, padx=5)
        self.threshold_var = tk.IntVar(value=60)
        threshold_scale = ttk.Scale(param_frame, from_=0, to=255, variable=self.threshold_var, orient=tk.HORIZONTAL)
        threshold_scale.pack(fill=tk.X, padx=5)
        self.threshold_label = ttk.Label(param_frame, text="60")
        self.threshold_label.pack(anchor=tk.W, padx=5)
        threshold_scale.bind("<Motion>", lambda e: self.threshold_label.config(text=str(self.threshold_var.get())))
        
        # 核大小
        ttk.Label(param_frame, text="核大小:").pack(anchor=tk.W, padx=5, pady=(10, 0))
        self.kernel_var = tk.IntVar(value=5)
        kernel_scale = ttk.Scale(param_frame, from_=3, to=15, variable=self.kernel_var, orient=tk.HORIZONTAL)
        kernel_scale.pack(fill=tk.X, padx=5)
        self.kernel_label = ttk.Label(param_frame, text="5")
        self.kernel_label.pack(anchor=tk.W, padx=5)
        kernel_scale.bind("<Motion>", lambda e: self.kernel_label.config(text=str(self.kernel_var.get())))
        
        # 处理按钮
        process_frame = ttk.Frame(control_frame)
        process_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(process_frame, text="预览效果", command=self.preview_effect).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(process_frame, text="开始处理", command=self.process_video).pack(fill=tk.X)
        
        # 配置保存/加载
        config_frame = ttk.Frame(control_frame)
        config_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(config_frame, text="保存配置", command=self.save_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(config_frame, text="加载配置", command=self.load_config).pack(side=tk.LEFT)
        
        # 右侧视频显示区域
        video_frame = ttk.LabelFrame(main_frame, text="视频预览")
        video_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建Canvas用于显示视频和绘制选择框
        self.canvas = tk.Canvas(video_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 使用说明
        help_text = "使用说明：\n1. 点击'选择视频文件'加载视频\n2. 拖动滑块选择合适的帧\n3. 在视频上拖拽选择水印区域\n4. 可以选择多个区域\n5. 调整处理参数\n6. 点击'预览效果'查看\n7. 点击'开始处理'生成视频"
        help_label = ttk.Label(control_frame, text=help_text, justify=tk.LEFT, font=("Arial", 8))
        help_label.pack(fill=tk.X, pady=10)
    
    def bind_events(self):
        """
        bind_events 功能说明:
        # 绑定鼠标和键盘事件
        # 输入: [无] | 输出: [无，绑定事件]
        """
        self.canvas.bind("<Button-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
    
    def load_video(self):
        """
        load_video 功能说明:
        # 加载视频文件
        # 输入: [无] | 输出: [bool 加载是否成功]
        """
        file_path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[("视频文件", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v")]
        )
        
        if not file_path:
            return False
        
        try:
            # 释放之前的视频
            if self.cap:
                self.cap.release()
            
            # 打开新视频
            self.cap = cv2.VideoCapture(file_path)
            if not self.cap.isOpened():
                messagebox.showerror("错误", "无法打开视频文件")
                return False
            
            self.video_path = file_path
            self.file_label.config(text=os.path.basename(file_path))
            
            # 获取视频信息
            total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.frame_scale.config(to=total_frames-1)
            
            # 显示第一帧
            self.show_frame(0)
            
            self.status_var.set(f"视频加载成功 - 共{total_frames}帧")
            log_info(f"视频加载成功: {file_path}")
            
            return True
            
        except Exception as e:
            messagebox.showerror("错误", f"加载视频失败: {str(e)}")
            log_error(f"视频加载失败: {str(e)}")
            return False
    
    def show_frame(self, frame_number: int):
        """
        show_frame 功能说明:
        # 显示指定帧
        # 输入: [frame_number: int 帧号] | 输出: [无，显示帧]
        """
        if not self.cap:
            return
        
        try:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.cap.read()
            
            if ret:
                self.current_frame = frame.copy()
                self.display_frame_with_areas(frame)
                
                total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.frame_info.config(text=f"帧: {frame_number}/{total_frames}")
                
        except Exception as e:
            log_error(f"显示帧失败: {str(e)}")
    
    def display_frame_with_areas(self, frame: np.ndarray):
        """
        display_frame_with_areas 功能说明:
        # 显示帧并绘制水印区域
        # 输入: [frame: np.ndarray 视频帧] | 输出: [无，显示带区域的帧]
        """
        try:
            # 调整帧大小以适应Canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                self.root.after(100, lambda: self.display_frame_with_areas(frame))
                return
            
            h, w = frame.shape[:2]
            
            # 计算缩放比例
            scale_w = canvas_width / w
            scale_h = canvas_height / h
            scale = min(scale_w, scale_h) * 0.9  # 留一些边距
            
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            # 缩放图像
            resized_frame = cv2.resize(frame, (new_w, new_h))
            
            # 在缩放后的帧上绘制水印区域
            for i, area in enumerate(self.watermark_areas):
                x1, y1, x2, y2 = area
                # 将原始坐标转换为缩放后的坐标
                scaled_x1 = int(x1 * scale)
                scaled_y1 = int(y1 * scale)
                scaled_x2 = int(x2 * scale)
                scaled_y2 = int(y2 * scale)
                
                # 绘制矩形框
                cv2.rectangle(resized_frame, (scaled_x1, scaled_y1), (scaled_x2, scaled_y2), (0, 255, 0), 2)
                # 添加标签
                cv2.putText(resized_frame, f"Area {i+1}", (scaled_x1, scaled_y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # 转换为PIL图像
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(pil_image)
            
            # 清空Canvas并显示图像
            self.canvas.delete("all")
            
            # 计算居中位置
            x_offset = (canvas_width - new_w) // 2
            y_offset = (canvas_height - new_h) // 2
            
            self.canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=photo)
            self.canvas.image = photo  # 保持引用
            
            # 保存缩放信息用于坐标转换
            self.scale = scale
            self.x_offset = x_offset
            self.y_offset = y_offset
            
        except Exception as e:
            log_error(f"显示帧失败: {str(e)}")
    
    def on_frame_change(self, event):
        """
        on_frame_change 功能说明:
        # 帧滑块变化事件处理
        # 输入: [event 事件对象] | 输出: [无，更新帧显示]
        """
        if self.cap:
            frame_number = int(self.frame_scale.get())
            self.show_frame(frame_number)
    
    def on_mouse_press(self, event):
        """
        on_mouse_press 功能说明:
        # 鼠标按下事件处理
        # 输入: [event 鼠标事件] | 输出: [无，开始选择区域]
        """
        if not self.current_frame is None:
            # 转换Canvas坐标到原始图像坐标
            x = (event.x - self.x_offset) / self.scale
            y = (event.y - self.y_offset) / self.scale
            
            self.selection_start = (int(x), int(y))
            self.is_selecting = True
    
    def on_mouse_drag(self, event):
        """
        on_mouse_drag 功能说明:
        # 鼠标拖拽事件处理
        # 输入: [event 鼠标事件] | 输出: [无，更新选择框]
        """
        if self.is_selecting and self.selection_start:
            # 转换坐标
            x = (event.x - self.x_offset) / self.scale
            y = (event.y - self.y_offset) / self.scale
            
            self.selection_end = (int(x), int(y))
            
            # 重新显示帧以更新选择框
            self.display_frame_with_selection()
    
    def on_mouse_release(self, event):
        """
        on_mouse_release 功能说明:
        # 鼠标释放事件处理
        # 输入: [event 鼠标事件] | 输出: [无，完成区域选择]
        """
        if self.is_selecting and self.selection_start and self.selection_end:
            # 确保坐标顺序正确
            x1, y1 = self.selection_start
            x2, y2 = self.selection_end
            
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            
            # 检查区域大小
            if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:
                self.watermark_areas.append((x1, y1, x2, y2))
                self.update_area_list()
                self.status_var.set(f"添加水印区域: ({x1},{y1}) - ({x2},{y2})")
                log_info(f"添加水印区域: ({x1},{y1}) - ({x2},{y2})")
            
            # 重置选择状态
            self.is_selecting = False
            self.selection_start = None
            self.selection_end = None
            
            # 重新显示帧
            if self.current_frame is not None:
                self.display_frame_with_areas(self.current_frame)
    
    def display_frame_with_selection(self):
        """
        display_frame_with_selection 功能说明:
        # 显示帧并绘制当前选择框
        # 输入: [无] | 输出: [无，显示带选择框的帧]
        """
        if self.current_frame is None or not self.selection_start or not self.selection_end:
            return
        
        frame = self.current_frame.copy()
        
        # 绘制现有的水印区域
        for i, area in enumerate(self.watermark_areas):
            x1, y1, x2, y2 = area
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"Area {i+1}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # 绘制当前选择框
        x1, y1 = self.selection_start
        x2, y2 = self.selection_end
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
        self.display_frame_with_areas(frame)
    
    def update_area_list(self):
        """
        update_area_list 功能说明:
        # 更新水印区域列表显示
        # 输入: [无] | 输出: [无，更新列表]
        """
        self.area_listbox.delete(0, tk.END)
        for i, area in enumerate(self.watermark_areas):
            x1, y1, x2, y2 = area
            self.area_listbox.insert(tk.END, f"区域{i+1}: ({x1},{y1}) - ({x2},{y2})")
    
    def delete_selected_area(self):
        """
        delete_selected_area 功能说明:
        # 删除选中的水印区域
        # 输入: [无] | 输出: [无，删除区域]
        """
        selection = self.area_listbox.curselection()
        if selection:
            index = selection[0]
            del self.watermark_areas[index]
            self.update_area_list()
            if self.current_frame is not None:
                self.display_frame_with_areas(self.current_frame)
            self.status_var.set(f"删除区域{index+1}")
    
    def clear_all_areas(self):
        """
        clear_all_areas 功能说明:
        # 清空所有水印区域
        # 输入: [无] | 输出: [无，清空区域]
        """
        self.watermark_areas.clear()
        self.update_area_list()
        if self.current_frame is not None:
            self.display_frame_with_areas(self.current_frame)
        self.status_var.set("清空所有区域")
    
    def preview_effect(self):
        """
        preview_effect 功能说明:
        # 预览去水印效果
        # 输入: [无] | 输出: [无，显示预览]
        """
        if not self.current_frame is not None or not self.watermark_areas:
            messagebox.showwarning("警告", "请先选择水印区域")
            return
        
        try:
            # 创建自定义水印去除器
            remover = CustomWatermarkRemover(
                threshold=self.threshold_var.get(),
                kernel_size=self.kernel_var.get(),
                watermark_areas=self.watermark_areas
            )
            
            # 处理当前帧
            processed_frame = remover.process_frame(self.current_frame)
            
            # 显示对比窗口
            self.show_comparison(self.current_frame, processed_frame)
            
        except Exception as e:
            messagebox.showerror("错误", f"预览失败: {str(e)}")
            log_error(f"预览失败: {str(e)}")
    
    def show_comparison(self, original: np.ndarray, processed: np.ndarray):
        """
        show_comparison 功能说明:
        # 显示原始和处理后的对比
        # 输入: [original: np.ndarray 原始帧, processed: np.ndarray 处理后帧] | 输出: [无，显示对比窗口]
        """
        # 创建对比窗口
        compare_window = tk.Toplevel(self.root)
        compare_window.title("效果预览对比")
        compare_window.geometry("800x400")
        
        # 创建左右两个Canvas
        left_frame = ttk.LabelFrame(compare_window, text="原始")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_frame = ttk.LabelFrame(compare_window, text="处理后")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left_canvas = tk.Canvas(left_frame, bg="black")
        left_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_canvas = tk.Canvas(right_frame, bg="black")
        right_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 显示图像
        def display_images():
            try:
                # 调整图像大小
                target_size = (350, 250)
                
                original_resized = cv2.resize(original, target_size)
                processed_resized = cv2.resize(processed, target_size)
                
                # 转换为PIL图像
                original_rgb = cv2.cvtColor(original_resized, cv2.COLOR_BGR2RGB)
                processed_rgb = cv2.cvtColor(processed_resized, cv2.COLOR_BGR2RGB)
                
                original_pil = Image.fromarray(original_rgb)
                processed_pil = Image.fromarray(processed_rgb)
                
                original_photo = ImageTk.PhotoImage(original_pil)
                processed_photo = ImageTk.PhotoImage(processed_pil)
                
                # 显示图像
                left_canvas.create_image(175, 125, image=original_photo)
                left_canvas.image = original_photo
                
                right_canvas.create_image(175, 125, image=processed_photo)
                right_canvas.image = processed_photo
                
            except Exception as e:
                log_error(f"显示对比图像失败: {str(e)}")
        
        compare_window.after(100, display_images)
    
    def process_video(self):
        """
        process_video 功能说明:
        # 处理整个视频
        # 输入: [无] | 输出: [无，生成处理后的视频]
        """
        if not self.video_path or not self.watermark_areas:
            messagebox.showwarning("警告", "请先加载视频并选择水印区域")
            return
        
        # 选择输出文件
        output_path = filedialog.asksaveasfilename(
            title="保存处理后的视频",
            defaultextension=".mp4",
            filetypes=[("MP4文件", "*.mp4"), ("所有文件", "*.*")]
        )
        
        if not output_path:
            return
        
        try:
            # 创建自定义水印去除器
            remover = CustomWatermarkRemover(
                threshold=self.threshold_var.get(),
                kernel_size=self.kernel_var.get(),
                watermark_areas=self.watermark_areas
            )
            
            # 创建进度窗口
            progress_window = self.create_progress_window()
            
            # 在新线程中处理视频
            import threading
            
            def process_thread():
                try:
                    success = remover.remove_video_watermark(self.video_path, output_path)
                    
                    self.root.after(0, lambda: self.on_process_complete(success, output_path, progress_window))
                    
                except Exception as e:
                    self.root.after(0, lambda: self.on_process_error(str(e), progress_window))
            
            thread = threading.Thread(target=process_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("错误", f"处理失败: {str(e)}")
            log_error(f"视频处理失败: {str(e)}")
    
    def create_progress_window(self):
        """
        create_progress_window 功能说明:
        # 创建进度显示窗口
        # 输入: [无] | 输出: [progress_window 进度窗口]
        """
        progress_window = tk.Toplevel(self.root)
        progress_window.title("处理进度")
        progress_window.geometry("400x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="正在处理视频，请稍候...", font=("Arial", 12)).pack(pady=20)
        
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        progress_bar.start()
        
        return progress_window
    
    def on_process_complete(self, success: bool, output_path: str, progress_window):
        """
        on_process_complete 功能说明:
        # 处理完成回调
        # 输入: [success: bool 是否成功, output_path: str 输出路径, progress_window 进度窗口] | 输出: [无]
        """
        progress_window.destroy()
        
        if success:
            messagebox.showinfo("成功", f"视频处理完成！\n输出文件: {output_path}")
            self.status_var.set("视频处理完成")
            log_info(f"视频处理完成: {output_path}")
        else:
            messagebox.showerror("失败", "视频处理失败，请查看日志")
            self.status_var.set("视频处理失败")
    
    def on_process_error(self, error_msg: str, progress_window):
        """
        on_process_error 功能说明:
        # 处理错误回调
        # 输入: [error_msg: str 错误信息, progress_window 进度窗口] | 输出: [无]
        """
        progress_window.destroy()
        messagebox.showerror("错误", f"处理失败: {error_msg}")
        self.status_var.set("处理失败")
        log_error(f"视频处理失败: {error_msg}")
    
    def save_config(self):
        """
        save_config 功能说明:
        # 保存当前配置
        # 输入: [无] | 输出: [无，保存配置文件]
        """
        if not self.watermark_areas:
            messagebox.showwarning("警告", "没有水印区域可保存")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存配置文件",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                config = {
                    "watermark_areas": self.watermark_areas,
                    "threshold": self.threshold_var.get(),
                    "kernel_size": self.kernel_var.get()
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("成功", "配置保存成功")
                self.status_var.set(f"配置已保存: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("错误", f"保存配置失败: {str(e)}")
    
    def load_config(self):
        """
        load_config 功能说明:
        # 加载配置文件
        # 输入: [无] | 输出: [无，加载配置]
        """
        file_path = filedialog.askopenfilename(
            title="加载配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 加载水印区域
                self.watermark_areas = config.get("watermark_areas", [])
                self.update_area_list()
                
                # 加载参数
                self.threshold_var.set(config.get("threshold", 60))
                self.kernel_var.set(config.get("kernel_size", 5))
                
                # 更新显示
                if self.current_frame is not None:
                    self.display_frame_with_areas(self.current_frame)
                
                messagebox.showinfo("成功", "配置加载成功")
                self.status_var.set(f"配置已加载: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("错误", f"加载配置失败: {str(e)}")
    
    def run(self):
        """
        run 功能说明:
        # 运行GUI应用
        # 输入: [无] | 输出: [无，启动应用]
        """
        try:
            self.root.mainloop()
        finally:
            if self.cap:
                self.cap.release()


class CustomWatermarkRemover(WatermarkRemover):
    """
    CustomWatermarkRemover 功能说明:
    # 自定义水印去除器，支持指定区域处理
    # 输入: [threshold, kernel_size, watermark_areas] | 输出: [CustomWatermarkRemover实例]
    """
    
    def __init__(self, threshold: int = 60, kernel_size: int = 5, watermark_areas: List[Tuple[int, int, int, int]] = None):
        super().__init__(threshold, kernel_size)
        self.watermark_areas = watermark_areas or []
    
    def create_mask(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        create_mask 功能说明:
        # 根据指定区域创建掩码
        # 输入: [frame: np.ndarray 输入帧] | 输出: [Optional[np.ndarray] 掩码]
        """
        if not self.watermark_areas:
            return super().create_mask(frame)
        
        try:
            h, w = frame.shape[:2]
            mask = np.zeros((h, w), dtype=np.uint8)
            
            # 为每个指定区域创建掩码
            for x1, y1, x2, y2 in self.watermark_areas:
                # 确保坐标在有效范围内
                x1 = max(0, min(x1, w-1))
                y1 = max(0, min(y1, h-1))
                x2 = max(0, min(x2, w-1))
                y2 = max(0, min(y2, h-1))
                
                # 在指定区域创建掩码
                mask[y1:y2, x1:x2] = 255
            
            # 应用形态学操作
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel, iterations=self.iterations)
            
            return mask
            
        except Exception as e:
            print(f"❌ 自定义掩码创建失败: {str(e)}")
            return None


if __name__ == "__main__":
    # 启动GUI应用
    app = WatermarkGUI()
    app.run()

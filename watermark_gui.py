##########watermark_gui.py: [智能视频去水印工具GUI界面] ##################
# 变更记录: [2025-01-27] @李祥光 [创建图形界面用于选择水印区域]########
# 变更记录: [2025-01-27] @李祥光 [修复预览对比窗口视频比例变形问题]########
# 变更记录: [2025-01-27] @李祥光 [增加视频帧导航功能，支持前进后退]########
# 变更记录: [2025-01-27] @李祥光 [修复视频帧显示问题，确保正确显示当前帧]########
# 变更记录: [2025-01-27] @李祥光 [优化界面布局，增加滚动条支持]########
# 变更记录: [2025-01-27] @李祥光 [修复视频播放控制逻辑，确保帧数显示正确]########
# 变更记录: [2025-01-27] @李祥光 [增加键盘快捷键支持：左右箭头键控制帧切换]########
# 变更记录: [2025-01-27] @李祥光 [修复Canvas尺寸计算，确保视频完整显示]########
# 变更记录: [2025-01-27] @李祥光 [优化水印区域选择交互，支持拖拽选择]########
# 变更记录: [2025-06-25] @李祥光 [修复预览界面图像显示：确保视频完整显示不被截断]########
# 变更记录: [2025-06-25] @李祥光 [优化处理流程：自动生成输出文件名，无需手动选择]########
# 变更记录: [2025-06-25] @李祥光 [界面优化：进一步减少水印区域列表高度]########
# 变更记录: [2025-06-25] @李祥光 [优化使用说明：去掉"拖动滑块选择合适的帧"步骤]########
# 变更记录: [2025-06-25] @李祥光 [修复ttk组件配置错误，使用destroy重建替代configure]########
# 输入: [视频文件路径] | 输出: [处理后的无水印视频文件]###############


###########################文件下的所有函数###########################
"""
WatermarkGUI.__init__：初始化GUI界面和所有组件
WatermarkGUI.create_widgets：创建主要的界面组件
WatermarkGUI.load_video：加载视频文件并初始化播放器
WatermarkGUI.update_frame：更新当前显示的视频帧
WatermarkGUI.on_canvas_click：处理画布点击事件，开始选择水印区域
WatermarkGUI.on_canvas_drag：处理画布拖拽事件，实时更新选择区域
WatermarkGUI.on_canvas_release：处理画布释放事件，完成区域选择
WatermarkGUI.add_watermark_area：添加水印区域到列表
WatermarkGUI.delete_selected_area：删除选中的水印区域
WatermarkGUI.clear_all_areas：清空所有水印区域
WatermarkGUI.preview_effect：预览去水印效果
WatermarkGUI.process_video：处理视频去水印
WatermarkGUI.on_key_press：处理键盘按键事件
WatermarkGUI.prev_frame：切换到上一帧
WatermarkGUI.next_frame：切换到下一帧
WatermarkGUI.on_frame_scale：处理帧滑块变化事件
WatermarkGUI.show_preview_window：显示预览对比窗口
WatermarkGUI.close_preview：关闭预览窗口
WatermarkGUI.update_preview：更新预览窗口内容
"""
###########################文件下的所有函数###########################

#########mermaid格式说明所有函数的调用关系说明开始#########
"""
flowchart TD
    A[程序启动] --> B[WatermarkGUI.__init__]
    B --> C[create_widgets]
    C --> D[界面组件创建完成]
    D --> E[用户操作]
    E --> F{操作类型}
    F -->|加载视频| G[load_video]
    F -->|选择区域| H[on_canvas_click]
    F -->|拖拽选择| I[on_canvas_drag]
    F -->|完成选择| J[on_canvas_release]
    F -->|键盘操作| K[on_key_press]
    F -->|滑块操作| L[on_frame_scale]
    F -->|预览效果| M[preview_effect]
    F -->|处理视频| N[process_video]
    G --> O[update_frame]
    H --> I
    I --> J
    J --> P[add_watermark_area]
    K --> Q{按键类型}
    Q -->|左箭头| R[prev_frame]
    Q -->|右箭头| S[next_frame]
    R --> O
    S --> O
    L --> O
    M --> T[show_preview_window]
    T --> U[update_preview]
"""
#########mermaid格式说明所有函数的调用关系说明结束#########

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import os
from watermark_remover import WatermarkRemover

class WatermarkGUI:
    """
    WatermarkGUI 功能说明:
    # 智能视频去水印工具的图形用户界面
    # 输入: [无] | 输出: [GUI界面实例]# # # # # 
    """
    def __init__(self, root):
        self.root = root
        self.root.title("智能视频去水印工具")
        self.root.geometry("1200x800")
        
        # 视频相关变量
        self.video_path = None
        self.cap = None
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30
        
        # 界面相关变量
        self.canvas = None
        self.photo = None
        self.scale_factor = 1.0
        
        # 水印区域相关变量
        self.watermark_areas = []
        self.selecting = False
        self.start_x = 0
        self.start_y = 0
        self.current_rect = None
        
        # 预览窗口相关变量
        self.preview_window = None
        self.preview_canvas_original = None
        self.preview_canvas_processed = None
        
        # 创建界面
        self.create_widgets()
        
        # 绑定键盘事件
        self.root.bind('<Key>', self.on_key_press)
        self.root.focus_set()
    
    """
    create_widgets 功能说明:
    # 创建主要的界面组件，包括控制面板和视频显示区域
    # 输入: [无] | 输出: [无，创建界面组件]# # # # # 
    """
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧控制面板
        control_frame = ttk.Frame(main_frame, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_frame.pack_propagate(False)
        
        # 文件选择
        file_frame = ttk.LabelFrame(control_frame, text="文件选择")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(file_frame, text="选择视频文件", command=self.load_video).pack(fill=tk.X, padx=5, pady=5)
        
        # 使用说明
        help_frame = ttk.LabelFrame(control_frame, text="使用说明")
        help_frame.pack(fill=tk.X, pady=(0, 10))
        
        help_text = """1. 点击"选择视频文件"加载视频
2. 在视频画面上拖拽选择水印区域
3. 可以选择多个水印区域
4. 点击"预览效果"查看去水印效果
5. 点击"开始处理"生成无水印视频

快捷键：
← → 方向键：切换视频帧"""
        
        help_label = tk.Label(help_frame, text=help_text, justify=tk.LEFT, wraplength=280)
        help_label.pack(padx=5, pady=5)
        
        # 水印区域列表
        area_frame = ttk.LabelFrame(control_frame, text="水印区域")
        # 将水印区域列表框架放置在控制面板中，填充整个可用空间并在上下添加10像素的内边距
        area_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 区域列表
        ###########################修改开始 2025-6-25 李祥光  #######################
        # self.area_listbox = tk.Listbox(area_frame, height=6)
        # self.area_listbox = tk.Listbox(area_frame, height=3)
        ###########################修改结束 2025-6-25 李祥光  #######################
        self.area_listbox = tk.Listbox(area_frame, height=2)
        self.area_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 区域操作按钮
        area_btn_frame = ttk.Frame(area_frame)
        area_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(area_btn_frame, text="删除选中", command=self.delete_selected_area).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(area_btn_frame, text="清空全部", command=self.clear_all_areas).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(area_btn_frame, text="预览效果", command=self.preview_effect).pack(side=tk.LEFT)
        
        # 处理按钮
        process_frame = ttk.Frame(control_frame)
        process_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(process_frame, text="开始处理", command=self.process_video).pack(fill=tk.X)
        
        # 右侧视频显示区域
        video_frame = ttk.LabelFrame(main_frame, text="视频预览")
        video_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 帧控制
        frame_control = ttk.Frame(video_frame)
        frame_control.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(frame_control, text="上一帧", command=self.prev_frame).pack(side=tk.LEFT)
        ttk.Button(frame_control, text="下一帧", command=self.next_frame).pack(side=tk.LEFT, padx=(5, 0))
        
        # 帧滑块
        self.frame_var = tk.IntVar()
        self.frame_scale = ttk.Scale(frame_control, from_=0, to=100, orient=tk.HORIZONTAL, 
                                   variable=self.frame_var, command=self.on_frame_scale)
        self.frame_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # 帧信息标签
        self.frame_info = ttk.Label(frame_control, text="帧: 0/0")
        self.frame_info.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Canvas用于显示视频
        canvas_frame = ttk.Frame(video_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定Canvas事件
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
    
    """
    load_video 功能说明:
    # 加载视频文件并初始化播放器
    # 输入: [无，通过文件对话框选择] | 输出: [无，更新界面状态]# # # # # 
    """
    def load_video(self):
        file_path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[("视频文件", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv")]
        )
        
        if file_path:
            self.video_path = file_path
            
            # 释放之前的视频
            if self.cap:
                self.cap.release()
            
            # 打开新视频
            self.cap = cv2.VideoCapture(file_path)
            if not self.cap.isOpened():
                messagebox.showerror("错误", "无法打开视频文件")
                return
            
            # 获取视频信息
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            # 重置帧位置
            self.current_frame = 0
            self.frame_scale.configure(to=self.total_frames-1)
            
            # 显示第一帧
            self.update_frame()
            
            print(f"视频加载成功: {os.path.basename(file_path)}")
            print(f"总帧数: {self.total_frames}, FPS: {self.fps}")
    
    """
    update_frame 功能说明:
    # 更新当前显示的视频帧
    # 输入: [无] | 输出: [无，更新Canvas显示]# # # # # 
    """
    def update_frame(self):
        if not self.cap:
            return
        
        # 设置帧位置
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        ret, frame = self.cap.read()
        
        if ret:
            # 转换颜色空间
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 获取Canvas尺寸
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                # 计算缩放比例，保持宽高比
                frame_height, frame_width = frame_rgb.shape[:2]
                scale_w = canvas_width / frame_width
                scale_h = canvas_height / frame_height
                self.scale_factor = min(scale_w, scale_h)
                
                # 计算新尺寸
                new_width = int(frame_width * self.scale_factor)
                new_height = int(frame_height * self.scale_factor)
                
                # 调整图像大小
                frame_resized = cv2.resize(frame_rgb, (new_width, new_height))
                
                # 转换为PIL图像
                pil_image = Image.fromarray(frame_resized)
                self.photo = ImageTk.PhotoImage(pil_image)
                
                # 清除Canvas并显示图像
                self.canvas.delete("all")
                
                # 计算居中位置
                x_offset = (canvas_width - new_width) // 2
                y_offset = (canvas_height - new_height) // 2
                
                self.canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=self.photo)
                
                # 重新绘制水印区域
                for i, area in enumerate(self.watermark_areas):
                    x1, y1, x2, y2 = area
                    # 转换坐标到当前缩放
                    canvas_x1 = x1 * self.scale_factor + x_offset
                    canvas_y1 = y1 * self.scale_factor + y_offset
                    canvas_x2 = x2 * self.scale_factor + x_offset
                    canvas_y2 = y2 * self.scale_factor + y_offset
                    
                    self.canvas.create_rectangle(canvas_x1, canvas_y1, canvas_x2, canvas_y2, 
                                               outline='red', width=2, tags=f"area_{i}")
            
            # 更新界面信息
            self.frame_var.set(self.current_frame)
            self.frame_info.config(text=f"帧: {self.current_frame+1}/{self.total_frames}")
    
    """
    on_canvas_click 功能说明:
    # 处理画布点击事件，开始选择水印区域
    # 输入: [event: 鼠标点击事件] | 输出: [无，开始区域选择]# # # # # 
    """
    def on_canvas_click(self, event):
        if not self.cap:
            return
        
        self.selecting = True
        self.start_x = event.x
        self.start_y = event.y
        
        # 删除之前的临时矩形
        self.canvas.delete("temp_rect")
    
    """
    on_canvas_drag 功能说明:
    # 处理画布拖拽事件，实时更新选择区域
    # 输入: [event: 鼠标拖拽事件] | 输出: [无，更新临时矩形显示]# # # # # 
    """
    def on_canvas_drag(self, event):
        if not self.selecting:
            return
        
        # 删除之前的临时矩形
        self.canvas.delete("temp_rect")
        
        # 绘制新的临时矩形
        self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, 
                                   outline='yellow', width=2, tags="temp_rect")
    
    """
    on_canvas_release 功能说明:
    # 处理画布释放事件，完成区域选择
    # 输入: [event: 鼠标释放事件] | 输出: [无，添加水印区域]# # # # # 
    """
    def on_canvas_release(self, event):
        if not self.selecting:
            return
        
        self.selecting = False
        
        # 删除临时矩形
        self.canvas.delete("temp_rect")
        
        # 计算实际坐标（相对于原始视频）
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            # 获取视频尺寸
            frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # 计算偏移量
            new_width = int(frame_width * self.scale_factor)
            new_height = int(frame_height * self.scale_factor)
            x_offset = (canvas_width - new_width) // 2
            y_offset = (canvas_height - new_height) // 2
            
            # 转换坐标到原始视频坐标系
            x1 = max(0, int((self.start_x - x_offset) / self.scale_factor))
            y1 = max(0, int((self.start_y - y_offset) / self.scale_factor))
            x2 = min(frame_width, int((event.x - x_offset) / self.scale_factor))
            y2 = min(frame_height, int((event.y - y_offset) / self.scale_factor))
            
            # 确保坐标顺序正确
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1
            
            # 检查区域大小
            if x2 - x1 > 10 and y2 - y1 > 10:
                self.add_watermark_area(x1, y1, x2, y2)
    
    """
    add_watermark_area 功能说明:
    # 添加水印区域到列表
    # 输入: [x1, y1, x2, y2: 区域坐标] | 输出: [无，更新区域列表和显示]# # # # # 
    """
    def add_watermark_area(self, x1, y1, x2, y2):
        area = (x1, y1, x2, y2)
        self.watermark_areas.append(area)
        
        # 更新列表显示
        area_text = f"区域{len(self.watermark_areas)}: ({x1},{y1}) - ({x2},{y2})"
        self.area_listbox.insert(tk.END, area_text)
        
        # 重新绘制所有区域
        self.update_frame()
        
        print(f"添加水印区域: {area}")
    
    """
    delete_selected_area 功能说明:
    # 删除选中的水印区域
    # 输入: [无] | 输出: [无，删除选中区域]# # # # # 
    """
    def delete_selected_area(self):
        selection = self.area_listbox.curselection()
        if selection:
            index = selection[0]
            # 删除区域
            del self.watermark_areas[index]
            self.area_listbox.delete(index)
            
            # 更新列表显示
            self.area_listbox.delete(0, tk.END)
            for i, area in enumerate(self.watermark_areas):
                x1, y1, x2, y2 = area
                area_text = f"区域{i+1}: ({x1},{y1}) - ({x2},{y2})"
                self.area_listbox.insert(tk.END, area_text)
            
            # 重新绘制
            self.update_frame()
    
    """
    clear_all_areas 功能说明:
    # 清空所有水印区域
    # 输入: [无] | 输出: [无，清空所有区域]# # # # # 
    """
    def clear_all_areas(self):
        self.watermark_areas.clear()
        self.area_listbox.delete(0, tk.END)
        self.update_frame()
    
    """
    preview_effect 功能说明:
    # 预览去水印效果
    # 输入: [无] | 输出: [无，显示预览窗口]# # # # # 
    """
    def preview_effect(self):
        if not self.cap or not self.watermark_areas:
            messagebox.showwarning("警告", "请先加载视频并选择水印区域")
            return
        
        # 获取当前帧
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        ret, frame = self.cap.read()
        
        if ret:
            # 创建去水印处理器
            remover = WatermarkRemover()
            
            # 处理当前帧
            processed_frame = remover.remove_watermark_frame(frame, self.watermark_areas)
            
            # 显示预览窗口
            self.show_preview_window(frame, processed_frame)
    
    """
    process_video 功能说明:
    # 处理视频去水印
    # 输入: [无] | 输出: [无，生成处理后的视频文件]# # # # # 
    """
    def process_video(self):
        if not self.video_path or not self.watermark_areas:
            messagebox.showwarning("警告", "请先加载视频并选择水印区域")
            return
        
        # 自动生成输出文件名
        input_dir = os.path.dirname(self.video_path)
        input_name = os.path.splitext(os.path.basename(self.video_path))[0]
        input_ext = os.path.splitext(self.video_path)[1]
        output_path = os.path.join(input_dir, f"{input_name}-无水印{input_ext}")
        
        try:
            # 创建去水印处理器
            remover = WatermarkRemover()
            
            # 处理视频
            success = remover.remove_watermark(self.video_path, output_path, self.watermark_areas)
            
            if success:
                messagebox.showinfo("成功", f"视频处理完成！\n输出文件: {output_path}")
            else:
                messagebox.showerror("错误", "视频处理失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"处理过程中出现错误: {str(e)}")
    
    """
    on_key_press 功能说明:
    # 处理键盘按键事件
    # 输入: [event: 键盘事件] | 输出: [无，执行相应操作]# # # # # 
    """
    def on_key_press(self, event):
        if event.keysym == 'Left':
            self.prev_frame()
        elif event.keysym == 'Right':
            self.next_frame()
    
    """
    prev_frame 功能说明:
    # 切换到上一帧
    # 输入: [无] | 输出: [无，更新当前帧]# # # # # 
    """
    def prev_frame(self):
        if self.cap and self.current_frame > 0:
            self.current_frame -= 1
            self.update_frame()
    
    """
    next_frame 功能说明:
    # 切换到下一帧
    # 输入: [无] | 输出: [无，更新当前帧]# # # # # 
    """
    def next_frame(self):
        if self.cap and self.current_frame < self.total_frames - 1:
            self.current_frame += 1
            self.update_frame()
    
    """
    on_frame_scale 功能说明:
    # 处理帧滑块变化事件
    # 输入: [value: 滑块值] | 输出: [无，更新当前帧]# # # # # 
    """
    def on_frame_scale(self, value):
        if self.cap:
            self.current_frame = int(float(value))
            self.update_frame()
    
    """
    show_preview_window 功能说明:
    # 显示预览对比窗口
    # 输入: [original_frame, processed_frame: 原始帧和处理后帧] | 输出: [无，显示预览窗口]# # # # # 
    """
    def show_preview_window(self, original_frame, processed_frame):
        # 如果预览窗口已存在，先关闭
        if self.preview_window:
            self.preview_window.destroy()
        
        # 创建预览窗口
        self.preview_window = tk.Toplevel(self.root)
        self.preview_window.title("预览对比")
        self.preview_window.geometry("1000x600")
        
        # 创建主框架
        main_frame = ttk.Frame(self.preview_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 原始视频框架
        original_frame_widget = ttk.LabelFrame(main_frame, text="原始视频")
        original_frame_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.preview_canvas_original = tk.Canvas(original_frame_widget, bg='black')
        self.preview_canvas_original.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 处理后视频框架
        processed_frame_widget = ttk.LabelFrame(main_frame, text="去水印后")
        processed_frame_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.preview_canvas_processed = tk.Canvas(processed_frame_widget, bg='black')
        self.preview_canvas_processed.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 关闭按钮
        close_btn = ttk.Button(self.preview_window, text="关闭", command=self.close_preview)
        close_btn.pack(pady=5)
        
        # 更新预览内容
        self.preview_window.after(100, lambda: self.update_preview(original_frame, processed_frame))
    
    """
    close_preview 功能说明:
    # 关闭预览窗口
    # 输入: [无] | 输出: [无，关闭预览窗口]# # # # # 
    """
    def close_preview(self):
        if self.preview_window:
            self.preview_window.destroy()
            self.preview_window = None
    
    """
    update_preview 功能说明:
    # 更新预览窗口内容
    # 输入: [original_frame, processed_frame: 原始帧和处理后帧] | 输出: [无，更新预览显示]# # # # # 
    """
    def update_preview(self, original_frame, processed_frame):
        if not self.preview_window:
            return
        
        try:
            # 获取Canvas尺寸
            canvas_width = self.preview_canvas_original.winfo_width()
            canvas_height = self.preview_canvas_original.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                # 转换颜色空间
                original_rgb = cv2.cvtColor(original_frame, cv2.COLOR_BGR2RGB)
                processed_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                
                # 计算缩放比例
                frame_height, frame_width = original_rgb.shape[:2]
                scale_w = canvas_width / frame_width
                scale_h = canvas_height / frame_height
                scale_factor = min(scale_w, scale_h)
                
                # 计算新尺寸
                new_width = int(frame_width * scale_factor)
                new_height = int(frame_height * scale_factor)
                
                # 调整图像大小
                original_resized = cv2.resize(original_rgb, (new_width, new_height))
                processed_resized = cv2.resize(processed_rgb, (new_width, new_height))
                
                # 转换为PIL图像
                original_pil = Image.fromarray(original_resized)
                processed_pil = Image.fromarray(processed_resized)
                
                original_photo = ImageTk.PhotoImage(original_pil)
                processed_photo = ImageTk.PhotoImage(processed_pil)
                
                # 计算居中位置
                x_offset = (canvas_width - new_width) // 2
                y_offset = (canvas_height - new_height) // 2
                
                # 清除并显示图像
                self.preview_canvas_original.delete("all")
                self.preview_canvas_processed.delete("all")
                
                self.preview_canvas_original.create_image(x_offset, y_offset, anchor=tk.NW, image=original_photo)
                self.preview_canvas_processed.create_image(x_offset, y_offset, anchor=tk.NW, image=processed_photo)
                
                # 保持图像引用
                self.preview_canvas_original.image = original_photo
                self.preview_canvas_processed.image = processed_photo
                
        except Exception as e:
            print(f"预览更新错误: {e}")

def main():
    root = tk.Tk()
    app = WatermarkGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

##########watermark_gui.py: [智能视频去水印工具GUI界面] ##################
# 变更记录: [2025-06-25] @李祥光 [修复预览界面图像显示：确保视频完整显示不被截断]########
# 变更记录: [2025-06-25] @李祥光 [优化处理流程：自动生成输出文件名，无需手动选择]########
# 变更记录: [2025-06-25] @李祥光 [优化使用说明：去掉"拖动滑块选择合适的帧"步骤]########
# 变更记录: [2025-06-25] @李祥光 [修复ttk组件配置错误，使用destroy重建替代configure]########
# 变更记录: [2024-12-19] @李祥光 [界面优化：将使用说明字体从8号调整为12号，提升可读性]########
# 变更记录: [2024-12-19] @李祥光 [界面优化：调整控制面板布局，增加间距和对齐]########
# 变更记录: [2024-12-19] @李祥光 [功能增强：添加效果预览对比功能]########
# 变更记录: [2024-12-19] @李祥光 [界面优化：调整按钮布局和间距]########
# 变更记录: [2024-12-19] @李祥光 [功能增强：添加多区域水印选择支持]########
# 输入: [GUI事件] | 输出: [用户界面交互]###############


###########################文件下的所有函数###########################
"""
CustomWatermarkRemover：主GUI类，管理整个应用程序界面
create_widgets：创建所有GUI组件
bind_events：绑定事件处理器
load_video：加载视频文件
show_frame：显示视频帧
update_canvas_image：更新画布图像
start_selection：开始选择水印区域
update_selection：更新选择区域
end_selection：结束选择区域
delete_selection：删除选择区域
show_comparison：显示效果预览对比
process_video：处理视频去水印
update_progress：更新进度显示
"""
###########################文件下的所有函数###########################

#########mermaid格式说明所有函数的调用关系说明开始#########
"""
flowchart TD
    A[程序启动] --> B[CustomWatermarkRemover.__init__]
    B --> C[create_widgets]
    C --> D[bind_events]
    D --> E[用户交互]
    E --> F{用户操作}
    F -->|选择视频| G[load_video]
    F -->|拖拽选择| H[start_selection]
    F -->|预览效果| I[show_comparison]
    F -->|开始处理| J[process_video]
    G --> K[show_frame]
    K --> L[update_canvas_image]
    H --> M[update_selection]
    M --> N[end_selection]
    I --> O[显示对比窗口]
    J --> P[update_progress]
"""
#########mermaid格式说明所有函数的调用关系说明结束#########

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import threading
import os
from video_watermark_remover import VideoWatermarkRemover
from enhanced_watermark_remover import EnhancedWatermarkRemover
from utils.logger import setup_logger

class CustomWatermarkRemover:
    """
    CustomWatermarkRemover 功能说明:
    # 智能视频去水印工具的主GUI界面类
    # 输入: [GUI事件和用户交互] | 输出: [视频处理结果和界面更新]
    """
    def __init__(self, root):
        self.root = root
        self.root.title("智能视频去水印工具 v2.0")
        self.root.geometry("1200x800")
        
        # 初始化变量
        self.video_path = None
        self.cap = None
        self.current_frame = None
        self.total_frames = 0
        self.current_frame_index = 0
        self.canvas_width = 640
        self.canvas_height = 480
        
        # 选择区域相关
        self.selections = []  # 存储多个选择区域
        self.current_selection = None
        self.start_x = None
        self.start_y = None
        self.selection_rects = []  # 存储画布上的矩形对象
        
        # 处理参数
        self.inpaint_method = tk.StringVar(value="telea")
        self.blur_strength = tk.IntVar(value=5)
        self.edge_threshold = tk.IntVar(value=50)
        
        # 设置日志
        self.logger = setup_logger()
        
        # 创建界面
        self.create_widgets()
        self.bind_events()
    
    def create_widgets(self):
        """
        create_widgets 功能说明:
        # 创建所有GUI组件和布局
        # 输入: [无] | 输出: [完整的GUI界面]
        """
        # 主容器
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧视频显示区域
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 视频显示画布
        self.canvas = tk.Canvas(left_frame, width=self.canvas_width, height=self.canvas_height, bg='black')
        self.canvas.pack(pady=10)
        
        # 视频控制区域
        video_control_frame = ttk.Frame(left_frame)
        video_control_frame.pack(fill=tk.X, pady=5)
        
        # 加载视频按钮
        self.load_btn = ttk.Button(video_control_frame, text="选择视频文件", command=self.load_video)
        self.load_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 帧滑块
        self.frame_scale = ttk.Scale(video_control_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.on_frame_change)
        self.frame_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # 帧信息标签
        self.frame_info_label = ttk.Label(video_control_frame, text="帧: 0/0")
        self.frame_info_label.pack(side=tk.RIGHT)
        
        # 右侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding=10)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # 选择区域信息
        selection_frame = ttk.LabelFrame(control_frame, text="水印区域", padding=5)
        selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.selection_listbox = tk.Listbox(selection_frame, height=4)
        self.selection_listbox.pack(fill=tk.X, pady=(0, 5))
        
        # 删除选择按钮
        self.delete_btn = ttk.Button(selection_frame, text="删除选中区域", command=self.delete_selection)
        self.delete_btn.pack(fill=tk.X)
        
        # 处理参数设置
        params_frame = ttk.LabelFrame(control_frame, text="处理参数", padding=5)
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 修复方法选择
        ttk.Label(params_frame, text="修复方法:").pack(anchor=tk.W)
        method_frame = ttk.Frame(params_frame)
        method_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Radiobutton(method_frame, text="Telea", variable=self.inpaint_method, value="telea").pack(side=tk.LEFT)
        ttk.Radiobutton(method_frame, text="NS", variable=self.inpaint_method, value="ns").pack(side=tk.LEFT, padx=(10, 0))
        
        # 模糊强度
        ttk.Label(params_frame, text="模糊强度:").pack(anchor=tk.W, pady=(5, 0))
        self.blur_scale = ttk.Scale(params_frame, from_=1, to=15, variable=self.blur_strength, orient=tk.HORIZONTAL)
        self.blur_scale.pack(fill=tk.X)
        
        # 边缘阈值
        ttk.Label(params_frame, text="边缘阈值:").pack(anchor=tk.W, pady=(5, 0))
        self.edge_scale = ttk.Scale(params_frame, from_=10, to=200, variable=self.edge_threshold, orient=tk.HORIZONTAL)
        self.edge_scale.pack(fill=tk.X)
        
        # 操作按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.preview_btn = ttk.Button(button_frame, text="预览效果", command=self.show_comparison)
        self.preview_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.process_btn = ttk.Button(button_frame, text="开始处理", command=self.process_video)
        self.process_btn.pack(fill=tk.X)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # 状态栏
        status_bar = ttk.Label(control_frame, text="就绪", relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 使用说明
        help_text = "使用说明：\n1. 点击'选择视频文件'加载视频\n2. 在视频上拖拽选择水印区域\n3. 可以选择多个区域\n4. 调整处理参数\n5. 点击'预览效果'查看\n6. 点击'开始处理'生成视频"
        help_label = ttk.Label(control_frame, text=help_text, justify=tk.LEFT, font=("Arial", 12))
        help_label.pack(fill=tk.X, pady=10)
    
    def bind_events(self):
        """
        bind_events 功能说明:
        # 绑定鼠标和键盘事件处理器
        # 输入: [无] | 输出: [事件绑定完成]
        """
        self.canvas.bind("<Button-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-1>", self.end_selection)
        self.selection_listbox.bind("<Double-Button-1>", self.on_selection_double_click)
    
    def load_video(self):
        """
        load_video 功能说明:
        # 加载视频文件并显示第一帧
        # 输入: [用户选择的视频文件] | 输出: [视频加载和帧显示]
        """
        file_path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[("视频文件", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv")]
        )
        
        if file_path:
            self.video_path = file_path
            self.cap = cv2.VideoCapture(file_path)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if self.total_frames > 0:
                self.frame_scale.configure(to=self.total_frames-1)
                self.show_frame(0)
                self.logger.info(f"视频加载成功: {file_path}, 总帧数: {self.total_frames}")
            else:
                messagebox.showerror("错误", "无法读取视频文件")
    
    def on_frame_change(self, value):
        """
        on_frame_change 功能说明:
        # 响应帧滑块变化事件
        # 输入: [滑块值] | 输出: [显示对应帧]
        """
        if self.cap:
            frame_index = int(float(value))
            self.show_frame(frame_index)
    
    def show_frame(self, frame_index):
        """
        show_frame 功能说明:
        # 显示指定索引的视频帧
        # 输入: [帧索引] | 输出: [在画布上显示帧图像]
        """
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ret, frame = self.cap.read()
            
            if ret:
                self.current_frame = frame.copy()
                self.current_frame_index = frame_index
                self.update_canvas_image(frame)
                self.frame_info_label.config(text=f"帧: {frame_index+1}/{self.total_frames}")
    
    def update_canvas_image(self, frame):
        """
        update_canvas_image 功能说明:
        # 更新画布上的图像显示
        # 输入: [OpenCV帧图像] | 输出: [在画布上显示缩放后的图像]
        """
        # 获取画布实际尺寸
        self.canvas.update()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 如果画布尺寸无效，使用默认值
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 350
            canvas_height = 250
        
        # 计算缩放比例
        frame_height, frame_width = frame.shape[:2]
        scale_w = canvas_width / frame_width
        scale_h = canvas_height / frame_height
        
        ###########################修改开始 2025-6-25 李祥光  #######################
        # scale = max(scale_w, scale_h)
        ###########################修改结束 2025-6-25 李祥光  #######################
        scale = min(scale_w, scale_h)
        
        # 计算新尺寸
        new_w = int(frame_width * scale)
        new_h = int(frame_height * scale)
        
        # 缩放图像
        resized_frame = cv2.resize(frame, (new_w, new_h))
        
        # 转换为RGB
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        
        # 转换为PIL图像
        pil_image = Image.fromarray(rgb_frame)
        
        # 转换为PhotoImage
        self.photo = ImageTk.PhotoImage(pil_image)
        
        # 清除画布并显示图像
        self.canvas.delete("all")
        
        # 计算居中位置
        x_offset = (canvas_width - new_w) // 2
        y_offset = (canvas_height - new_h) // 2
        
        self.canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=self.photo)
        
        # 保存缩放信息用于坐标转换
        self.scale_factor = scale
        self.image_offset_x = x_offset
        self.image_offset_y = y_offset
        self.display_width = new_w
        self.display_height = new_h
        
        # 重新绘制选择区域
        self.redraw_selections()
    
    def start_selection(self, event):
        """
        start_selection 功能说明:
        # 开始选择水印区域
        # 输入: [鼠标点击事件] | 输出: [开始绘制选择矩形]
        """
        if self.current_frame is not None:
            self.start_x = event.x
            self.start_y = event.y
            self.current_selection = self.canvas.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y,
                outline='red', width=2
            )
    
    def update_selection(self, event):
        """
        update_selection 功能说明:
        # 更新选择区域的大小
        # 输入: [鼠标拖拽事件] | 输出: [更新矩形大小]
        """
        if self.current_selection:
            self.canvas.coords(self.current_selection, self.start_x, self.start_y, event.x, event.y)
    
    def end_selection(self, event):
        """
        end_selection 功能说明:
        # 结束选择区域并保存坐标
        # 输入: [鼠标释放事件] | 输出: [保存选择区域坐标]
        """
        if self.current_selection and self.current_frame is not None:
            # 获取选择区域坐标
            x1, y1, x2, y2 = self.canvas.coords(self.current_selection)
            
            # 确保坐标顺序正确
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            
            # 检查选择区域是否在图像范围内
            if (x1 >= self.image_offset_x and x2 <= self.image_offset_x + self.display_width and
                y1 >= self.image_offset_y and y2 <= self.image_offset_y + self.display_height and
                abs(x2 - x1) > 5 and abs(y2 - y1) > 5):  # 最小选择区域
                
                # 转换为原始图像坐标
                orig_x1 = int((x1 - self.image_offset_x) / self.scale_factor)
                orig_y1 = int((y1 - self.image_offset_y) / self.scale_factor)
                orig_x2 = int((x2 - self.image_offset_x) / self.scale_factor)
                orig_y2 = int((y2 - self.image_offset_y) / self.scale_factor)
                
                # 保存选择区域
                selection_data = {
                    'canvas_coords': (x1, y1, x2, y2),
                    'original_coords': (orig_x1, orig_y1, orig_x2, orig_y2),
                    'rect_id': self.current_selection
                }
                
                self.selections.append(selection_data)
                self.selection_rects.append(self.current_selection)
                
                # 更新列表框
                self.update_selection_list()
                
                self.logger.info(f"添加水印区域: ({orig_x1}, {orig_y1}, {orig_x2}, {orig_y2})")
            else:
                # 删除无效选择
                self.canvas.delete(self.current_selection)
            
            self.current_selection = None
    
    def delete_selection(self):
        """
        delete_selection 功能说明:
        # 删除选中的水印区域
        # 输入: [列表框选中项] | 输出: [删除对应的选择区域]
        """
        selection = self.selection_listbox.curselection()
        if selection:
            index = selection[0]
            # 删除画布上的矩形
            rect_id = self.selections[index]['rect_id']
            self.canvas.delete(rect_id)
            
            # 删除数据
            del self.selections[index]
            del self.selection_rects[index]
            
            # 更新列表
            self.update_selection_list()
    
    def update_selection_list(self):
        """
        update_selection_list 功能说明:
        # 更新选择区域列表显示
        # 输入: [当前选择区域数据] | 输出: [更新列表框内容]
        """
        self.selection_listbox.delete(0, tk.END)
        for i, selection in enumerate(self.selections):
            x1, y1, x2, y2 = selection['original_coords']
            self.selection_listbox.insert(tk.END, f"区域{i+1}: ({x1},{y1}) - ({x2},{y2})")
    
    def redraw_selections(self):
        """
        redraw_selections 功能说明:
        # 重新绘制所有选择区域
        # 输入: [保存的选择区域数据] | 输出: [在画布上重新绘制矩形]
        """
        # 清除旧的矩形引用
        for rect_id in self.selection_rects:
            try:
                self.canvas.delete(rect_id)
            except:
                pass
        
        self.selection_rects.clear()
        
        # 重新绘制所有选择区域
        for selection in self.selections:
            orig_x1, orig_y1, orig_x2, orig_y2 = selection['original_coords']
            
            # 转换为当前显示坐标
            canvas_x1 = orig_x1 * self.scale_factor + self.image_offset_x
            canvas_y1 = orig_y1 * self.scale_factor + self.image_offset_y
            canvas_x2 = orig_x2 * self.scale_factor + self.image_offset_x
            canvas_y2 = orig_y2 * self.scale_factor + self.image_offset_y
            
            # 创建新矩形
            rect_id = self.canvas.create_rectangle(
                canvas_x1, canvas_y1, canvas_x2, canvas_y2,
                outline='red', width=2
            )
            
            # 更新引用
            selection['rect_id'] = rect_id
            self.selection_rects.append(rect_id)
    
    def on_selection_double_click(self, event):
        """
        on_selection_double_click 功能说明:
        # 处理选择区域列表的双击事件
        # 输入: [双击事件] | 输出: [高亮显示对应区域]
        """
        selection = self.selection_listbox.curselection()
        if selection:
            index = selection[0]
            # 可以在这里添加高亮显示逻辑
            pass
    
    def show_comparison(self):
        """
        show_comparison 功能说明:
        # 显示处理前后的效果对比
        # 输入: [当前帧和选择区域] | 输出: [对比预览窗口]
        """
        if self.current_frame is None:
            messagebox.showwarning("警告", "请先加载视频")
            return
        
        if not self.selections:
            messagebox.showwarning("警告", "请先选择水印区域")
            return
        
        # 创建预览窗口
        preview_window = tk.Toplevel(self.root)
        preview_window.title("效果预览对比 - 参数调整")
        preview_window.geometry("1000x600")
        
        # 主容器
        main_container = ttk.Frame(preview_window)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 图像对比区域
        image_frame = ttk.Frame(main_container)
        image_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧原始图像
        left_frame = ttk.LabelFrame(image_frame, text="原始图像", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        original_canvas = tk.Canvas(left_frame, bg='black')
        original_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 右侧处理后图像
        right_frame = ttk.LabelFrame(image_frame, text="处理后图像", padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        processed_canvas = tk.Canvas(right_frame, bg='black')
        processed_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 参数调整区域
        param_frame = ttk.LabelFrame(main_container, text="实时参数调整", padding=5)
        param_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 创建参数控件
        param_controls = ttk.Frame(param_frame)
        param_controls.pack(fill=tk.X)
        
        # 修复方法
        method_frame = ttk.Frame(param_controls)
        method_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(method_frame, text="修复方法:").pack()
        method_var = tk.StringVar(value=self.inpaint_method.get())
        ttk.Radiobutton(method_frame, text="Telea", variable=method_var, value="telea").pack(side=tk.LEFT)
        ttk.Radiobutton(method_frame, text="NS", variable=method_var, value="ns").pack(side=tk.LEFT)
        
        # 模糊强度
        blur_frame = ttk.Frame(param_controls)
        blur_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(blur_frame, text="模糊强度:").pack()
        blur_var = tk.IntVar(value=self.blur_strength.get())
        blur_scale = ttk.Scale(blur_frame, from_=1, to=15, variable=blur_var, orient=tk.HORIZONTAL, length=150)
        blur_scale.pack()
        
        # 边缘阈值
        edge_frame = ttk.Frame(param_controls)
        edge_frame.pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(edge_frame, text="边缘阈值:").pack()
        edge_var = tk.IntVar(value=self.edge_threshold.get())
        edge_scale = ttk.Scale(edge_frame, from_=10, to=200, variable=edge_var, orient=tk.HORIZONTAL, length=150)
        edge_scale.pack()
        
        # 更新按钮
        update_btn = ttk.Button(param_controls, text="更新预览")
        update_btn.pack(side=tk.LEFT, padx=(20, 0))
        
        def update_preview():
            """
            update_preview 功能说明:
            # 根据当前参数更新预览图像
            # 输入: [调整后的参数] | 输出: [更新的预览图像]
            """
            try:
                # 创建处理器
                remover = VideoWatermarkRemover()
                
                # 获取当前参数
                current_method = method_var.get()
                current_blur = blur_var.get()
                current_edge = edge_var.get()
                
                # 处理当前帧
                processed_frame = self.current_frame.copy()
                
                for selection in self.selections:
                    x1, y1, x2, y2 = selection['original_coords']
                    processed_frame = remover.remove_watermark_region(
                        processed_frame, (x1, y1, x2, y2),
                        method=current_method,
                        blur_strength=current_blur,
                        edge_threshold=current_edge
                    )
                
                # 显示图像
                display_images(self.current_frame, processed_frame)
                
            except Exception as e:
                messagebox.showerror("错误", f"预览更新失败: {str(e)}")
        
        def display_images(original, processed):
            """
            display_images 功能说明:
            # 在画布上显示原始和处理后的图像
            # 输入: [原始图像, 处理后图像] | 输出: [在画布上显示图像]
            """
            # 获取画布尺寸
            original_canvas.update()
            processed_canvas.update()
            
            canvas_width = original_canvas.winfo_width()
            canvas_height = original_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 350
                canvas_height = 250
            
            # 处理原始图像
            frame_height, frame_width = original.shape[:2]
            scale_w = canvas_width / frame_width
            scale_h = canvas_height / frame_height
            
            ###########################修改开始 2025-6-25 李祥光  #######################
            # scale = max(scale_w, scale_h)
            ###########################修改结束 2025-6-25 李祥光  #######################
            scale = min(scale_w, scale_h)
            
            new_w = int(frame_width * scale)
            new_h = int(frame_height * scale)
            
            # 显示原始图像
            resized_original = cv2.resize(original, (new_w, new_h))
            rgb_original = cv2.cvtColor(resized_original, cv2.COLOR_BGR2RGB)
            pil_original = Image.fromarray(rgb_original)
            photo_original = ImageTk.PhotoImage(pil_original)
            
            original_canvas.delete("all")
            x_offset = (canvas_width - new_w) // 2
            y_offset = (canvas_height - new_h) // 2
            original_canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=photo_original)
            original_canvas.image = photo_original  # 保持引用
            
            # 显示处理后图像
            resized_processed = cv2.resize(processed, (new_w, new_h))
            rgb_processed = cv2.cvtColor(resized_processed, cv2.COLOR_BGR2RGB)
            pil_processed = Image.fromarray(rgb_processed)
            photo_processed = ImageTk.PhotoImage(pil_processed)
            
            processed_canvas.delete("all")
            processed_canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=photo_processed)
            processed_canvas.image = photo_processed  # 保持引用
        
        # 绑定更新事件
        update_btn.config(command=update_preview)
        
        # 绑定参数变化事件
        def on_param_change(*args):
            update_preview()
        
        method_var.trace('w', on_param_change)
        blur_var.trace('w', on_param_change)
        edge_var.trace('w', on_param_change)
        
        # 初始显示
        preview_window.after(100, update_preview)
    
    def process_video(self):
        """
        process_video 功能说明:
        # 处理整个视频去除水印
        # 输入: [视频文件和选择区域] | 输出: [处理后的视频文件]
        """
        if not self.video_path:
            messagebox.showwarning("警告", "请先选择视频文件")
            return
        
        if not self.selections:
            messagebox.showwarning("警告", "请先选择水印区域")
            return
        
        ###########################修改开始 2025-6-25 李祥光  #######################
        # output_path = filedialog.asksaveasfilename(
        #     title="保存处理后的视频",
        #     defaultextension=".mp4",
        #     filetypes=[("MP4文件", "*.mp4"), ("所有文件", "*.*")]
        # )
        ###########################修改结束 2025-6-25 李祥光  #######################
        
        # 自动生成输出文件名
        video_dir = os.path.dirname(self.video_path)
        video_name = os.path.splitext(os.path.basename(self.video_path))[0]
        output_path = os.path.join(video_dir, f"{video_name}-无水印.mp4")
        
        if output_path:
            # 创建进度窗口
            progress_window = tk.Toplevel(self.root)
            progress_window.title("处理进度")
            progress_window.geometry("400x150")
            progress_window.resizable(False, False)
            
            # 进度标签
            progress_label = ttk.Label(progress_window, text="正在处理视频...")
            progress_label.pack(pady=10)
            
            # 进度条
            progress_bar = ttk.Progressbar(progress_window, length=300, mode='determinate')
            progress_bar.pack(pady=10)
            
            # 取消按钮
            cancel_btn = ttk.Button(progress_window, text="取消")
            cancel_btn.pack(pady=5)
            
            # 处理标志
            self.processing = True
            
            def update_progress_callback(current, total, message=""):
                """
                update_progress_callback 功能说明:
                # 更新处理进度的回调函数
                # 输入: [当前进度, 总进度, 消息] | 输出: [更新GUI进度显示]
                """
                if self.processing:
                    progress = (current / total) * 100
                    progress_bar['value'] = progress
                    if message:
                        progress_label.config(text=message)
                    progress_window.update()
                    return True
                return False
            
            def cancel_processing():
                self.processing = False
                progress_window.destroy()
            
            cancel_btn.config(command=cancel_processing)
            
            def process_thread():
                try:
                    # 创建处理器
                    remover = EnhancedWatermarkRemover()
                    
                    # 准备区域列表
                    regions = [selection['original_coords'] for selection in self.selections]
                    
                    # 处理视频
                    success = remover.process_video_enhanced(
                        self.video_path,
                        output_path,
                        regions,
                        method=self.inpaint_method.get(),
                        blur_strength=self.blur_strength.get(),
                        edge_threshold=self.edge_threshold.get(),
                        progress_callback=update_progress_callback
                    )
                    
                    if success and self.processing:
                        self.root.after(0, lambda: [
                            progress_window.destroy(),
                            messagebox.showinfo("完成", f"视频处理完成！\n保存位置: {output_path}")
                        ])
                    elif self.processing:
                        self.root.after(0, lambda: [
                            progress_window.destroy(),
                            messagebox.showerror("错误", "视频处理失败")
                        ])
                    
                except Exception as e:
                    if self.processing:
                        self.root.after(0, lambda: [
                            progress_window.destroy(),
                            messagebox.showerror("错误", f"处理过程中出现错误: {str(e)}")
                        ])
                finally:
                    self.processing = False
            
            # 启动处理线程
            thread = threading.Thread(target=process_thread)
            thread.daemon = True
            thread.start()
    
    def update_progress(self, value):
        """
        update_progress 功能说明:
        # 更新主界面的进度条
        # 输入: [进度值] | 输出: [更新进度条显示]
        """
        self.progress_var.set(value)
        self.root.update_idletasks()

def main():
    """
    main 功能说明:
    # 程序主入口函数
    # 输入: [无] | 输出: [启动GUI应用程序]
    """
    root = tk.Tk()
    app = CustomWatermarkRemover(root)
    root.mainloop()

if __name__ == "__main__":
    main()

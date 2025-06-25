# 智能视频去水印工具

一个功能强大的Python视频去水印处理工具，支持单个文件处理和批量处理。

## 功能特点 ✨

- 🎯 **智能去水印**: 基于阈值分割和形态学操作的水印去除算法
- 📁 **批量处理**: 支持文件夹内所有视频文件的批量处理
- 🔧 **多种配置**: 提供快速、平衡、精确三种预设模式
- 📊 **详细日志**: 完整的处理日志记录和统计信息
- 🎨 **友好界面**: 直观的命令行交互界面
- 📈 **进度显示**: 实时显示处理进度和状态

## 支持格式 📋

- MP4 (.mp4)
- AVI (.avi) 
- MOV (.mov)
- MKV (.mkv)
- FLV (.flv)
- WMV (.wmv)
- M4V (.m4v)
- WebM (.webm)
- 3GP (.3gp)
- MPEG (.mpg, .mpeg)

## 安装说明 🚀

### 1. 克隆项目
```bash
git clone https://github.com/lixiangguang/video-watermark-remover.git
cd video-watermark-remover
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 验证安装
```bash
python enhanced_watermark_remover.py --help
```

## 使用方法 📖

### 交互模式（推荐）

直接运行程序，按照提示操作：

```bash
python enhanced_watermark_remover.py
```

### 命令行模式

#### 处理单个视频文件
```bash
python enhanced_watermark_remover.py input_video.mp4
```

#### 批量处理文件夹
```bash
python enhanced_watermark_remover.py /path/to/video/folder
```

#### 使用特定配置
```bash
python enhanced_watermark_remover.py input_video.mp4 --config fast
```

### Windows用户快速启动

双击运行 `run_watermark_remover.bat` 文件，选择相应的功能。

## 配置选项 ⚙️

### 预设配置模式

| 模式 | 速度 | 质量 | 适用场景 |
|------|------|------|----------|
| fast | 快速 | 一般 | 大批量处理，对质量要求不高 |
| balanced | 中等 | 良好 | 日常使用，平衡处理速度和质量 |
| precise | 较慢 | 优秀 | 重要视频，追求最佳处理效果 |

### 自定义配置

可以通过修改 `config/example_config.json` 来创建自定义配置：

```json
{
  "processing": {
    "threshold": 0.8,
    "kernel_size": 5,
    "iterations": 3,
    "use_gpu": false,
    "batch_size": 1
  },
  "output": {
    "quality": "high",
    "format": "mp4",
    "output_dir": "output"
  }
}
```

## 项目结构 📁

```
video-watermark-remover/
├── video_watermark_remover.py      # 基础版处理工具
├── enhanced_watermark_remover.py   # 增强版主程序
├── requirements.txt                # 项目依赖
├── run_watermark_remover.bat      # Windows启动脚本
├── config/                        # 配置文件目录
│   ├── config.py                 # 配置管理模块
│   └── example_config.json       # 示例配置文件
├── utils/                         # 工具模块
│   ├── __init__.py               # 包初始化
│   └── logger.py                 # 日志工具
├── test/                          # 测试模块
│   └── test_basic.py             # 基础功能测试
├── output/                        # 输出目录
├── logs/                          # 日志目录
└── temp/                          # 临时文件目录
```

## 日志记录 📊

程序会在 `logs/` 目录下生成详细的日志文件，包括：

- 处理进度和状态
- 错误信息和警告
- 性能统计数据
- 批量处理汇总

日志文件命名格式：`watermark_remover_YYYYMMDD_HHMMSS.log`

## 故障排除 🔧

### 常见问题

**Q: 提示缺少依赖库**
```
A: 运行 pip install -r requirements.txt 安装所有依赖
```

**Q: 处理速度很慢**
```
A: 尝试使用 'fast' 配置模式，或检查系统资源使用情况
```

**Q: 输出视频质量不理想**
```
A: 尝试使用 'precise' 配置模式，或调整配置参数
```

**Q: 程序崩溃或异常退出**
```
A: 查看 logs/ 目录下的日志文件，获取详细错误信息
```

### 调试模式

运行测试脚本检查基础功能：
```bash
python test/test_basic.py
```

## 技术实现 🔬

### 核心算法
- **阈值分割**: 基于像素值差异识别水印区域
- **形态学操作**: 使用开运算和闭运算优化水印检测
- **区域填充**: 智能填充算法移除水印内容
- **质量优化**: 后处理提升视频输出质量

### 性能优化
- 多线程处理支持
- 内存使用优化
- 临时文件自动清理
- 批量处理效率提升

## 更新日志 📝

### v1.0.0 (2025-06-25)
- ✨ 初始版本发布
- 🎯 基础水印去除功能
- 📊 完整日志记录系统
- 🔧 交互式用户界面
- 📁 批量处理支持
- ⚙️ 多种预设配置
- 🧪 基础功能测试

## 许可证 📄

本项目采用 MIT 许可证 - 查看 LICENSE 文件了解详情

## 作者 👨‍💻

**李祥光** - 项目创建者和主要开发者

- 📧 Email: 274030396@qq.com
- 🐙 GitHub: [@lixiangguang](https://github.com/lixiangguang)

## 贡献 🤝

欢迎提交Issue和Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 支持项目 ⭐

如果这个项目对你有帮助，请给它一个星标 ⭐

---

*最后更新: 2025-06-25*
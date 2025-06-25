##########config.py: 配置管理模块 ##################
# 变更记录: [2025-06-25] @李祥光 [初始创建配置文件]########
# 输入: [无] | 输出: [配置参数字典]###############


###########################文件下的所有函数###########################
"""
get_default_config：获取默认配置参数
get_supported_formats：获取支持的视频格式列表
get_output_settings：获取输出设置
"""
###########################文件下的所有函数###########################

#########mermaid格式说明所有函数的调用关系说明开始#########
"""
flowchart TD
    A[配置模块] --> B[get_default_config]
    A --> C[get_supported_formats]
    A --> D[get_output_settings]
    B --> E[返回默认参数]
    C --> F[返回支持格式]
    D --> G[返回输出设置]
"""
#########mermaid格式说明所有函数的调用关系说明结束#########


def get_default_config() -> dict:
    """
    get_default_config 功能说明:
    # 获取视频去水印的默认配置参数
    # 输入: [无] | 输出: [dict 配置参数字典]
    """
    return {
        # 水印去除参数
        'threshold': 60,        # 阈值分割灰度值
        'kernel_size': 5,       # 形态学操作核大小
        'iterations': 2,        # 形态学操作迭代次数
        
        # 输出设置
        'output_quality': 'high',  # 输出质量: low, medium, high
        'output_format': 'mp4',    # 输出格式
        'preserve_audio': True,    # 保留音频
        
        # 处理设置
        'batch_size': 1,          # 批处理大小
        'use_gpu': False,         # 是否使用GPU加速
        'temp_cleanup': True,     # 自动清理临时文件
        
        # 日志设置
        'log_level': 'INFO',      # 日志级别
        'log_to_file': True,      # 是否记录到文件
        'log_to_console': True,   # 是否输出到控制台
    }


def get_supported_formats() -> dict:
    """
    get_supported_formats 功能说明:
    # 获取支持的视频格式列表
    # 输入: [无] | 输出: [dict 支持的格式字典]
    """
    return {
        'input_formats': [
            '.mp4', '.avi', '.mov', '.mkv', '.flv', 
            '.wmv', '.m4v', '.webm', '.3gp', '.mpg', '.mpeg'
        ],
        'output_formats': [
            '.mp4', '.avi', '.mov', '.mkv'
        ],
        'preferred_format': '.mp4'  # 推荐输出格式
    }


def get_output_settings() -> dict:
    """
    get_output_settings 功能说明:
    # 获取输出相关设置
    # 输入: [无] | 输出: [dict 输出设置字典]
    """
    return {
        'output_dir': 'output',
        'temp_dir': 'temp',
        'log_dir': 'logs',
        'filename_suffix': '_no_watermark',
        'create_backup': False,
        'overwrite_existing': False
    }


# 预设配置模板
PRESET_CONFIGS = {
    'fast': {
        'threshold': 80,
        'kernel_size': 3,
        'iterations': 1,
        'output_quality': 'medium',
        'use_gpu': False,
        'description': '快速处理模式，适合大批量处理'
    },
    
    'balanced': {
        'threshold': 60,
        'kernel_size': 5,
        'iterations': 2,
        'output_quality': 'high',
        'use_gpu': False,
        'description': '平衡模式，兼顾速度和质量'
    },
    
    'precise': {
        'threshold': 40,
        'kernel_size': 7,
        'iterations': 3,
        'output_quality': 'high',
        'use_gpu': True,
        'description': '精确模式，追求最佳效果'
    }
}


def get_preset_config(preset_name: str) -> dict:
    """
    get_preset_config 功能说明:
    # 获取预设配置
    # 输入: [preset_name: str 预设名称] | 输出: [dict 预设配置字典]
    """
    if preset_name not in PRESET_CONFIGS:
        raise ValueError(f"未知的预设配置: {preset_name}")
    
    # 合并默认配置和预设配置
    config = get_default_config()
    config.update(PRESET_CONFIGS[preset_name])
    
    return config
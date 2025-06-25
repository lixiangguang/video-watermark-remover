##########__init__.py: 工具模块包初始化文件 ##################
# 变更记录: [2025-06-25] @李祥光 [创建工具模块包]########
# 输入: [模块导入] | 输出: [导出工具函数]###############

"""
工具模块包
提供日志记录、文件处理等通用工具函数

主要模块:
- logger: 日志记录工具
"""

# 导入日志相关函数
from .logger import (
    setup_logger,
    log_info,
    log_warning,
    log_error,
    log_processing_start,
    log_processing_end,
    log_batch_summary
)

# 定义包的公开接口
__all__ = [
    'setup_logger',
    'log_info',
    'log_warning', 
    'log_error',
    'log_processing_start',
    'log_processing_end',
    'log_batch_summary'
]

# 包信息
__version__ = '1.0.0'
__author__ = '李祥光'
__email__ = '274030396@qq.com'
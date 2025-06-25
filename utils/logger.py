##########logger.py: 日志记录工具模块 ##################
# 变更记录: [2025-06-25] @李祥光 [创建日志记录工具]########
# 输入: [日志信息] | 输出: [格式化的日志记录]###############


###########################文件下的所有函数###########################
"""
setup_logger：配置和初始化日志记录器
log_info：记录信息级别日志
log_warning：记录警告级别日志
log_error：记录错误级别日志
log_processing_start：记录处理开始日志
log_processing_end：记录处理结束日志
log_batch_summary：记录批量处理汇总日志
"""
###########################文件下的所有函数###########################

#########mermaid格式说明所有函数的调用关系说明开始#########
"""
flowchart TD
    A[日志模块] --> B[setup_logger]
    B --> C[配置日志器]
    A --> D[log_info]
    A --> E[log_warning]
    A --> F[log_error]
    A --> G[log_processing_start]
    A --> H[log_processing_end]
    A --> I[log_batch_summary]
    D --> J[写入日志文件]
    E --> J
    F --> J
    G --> J
    H --> J
    I --> J
"""
#########mermaid格式说明所有函数的调用关系说明结束#########

import logging
import os
from datetime import datetime
from typing import Optional

# 全局日志器实例
_logger: Optional[logging.Logger] = None


def setup_logger(log_dir: str = "logs", log_level: str = "INFO") -> logging.Logger:
    """
    setup_logger 功能说明:
    # 配置和初始化日志记录器
    # 输入: [log_dir: str 日志目录, log_level: str 日志级别] | 输出: [Logger 日志记录器实例]
    """
    global _logger
    
    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    
    # 生成日志文件名（包含时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"watermark_remover_{timestamp}.log"
    log_filepath = os.path.join(log_dir, log_filename)
    
    # 创建日志器
    logger = logging.getLogger("watermark_remover")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 清除已有的处理器
    logger.handlers.clear()
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    file_handler.setLevel(getattr(logging, log_level.upper()))
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 设置格式器
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到日志器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    _logger = logger
    
    # 记录日志系统启动信息
    logger.info(f"日志系统初始化完成 - 日志文件: {log_filepath}")
    
    return logger


def _get_logger() -> logging.Logger:
    """
    获取全局日志器实例，如果未初始化则自动初始化
    """
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger


def log_info(message: str) -> None:
    """
    log_info 功能说明:
    # 记录信息级别的日志
    # 输入: [message: str 日志消息] | 输出: [无，记录到日志文件]
    """
    _get_logger().info(message)


def log_warning(message: str) -> None:
    """
    log_warning 功能说明:
    # 记录警告级别的日志
    # 输入: [message: str 警告消息] | 输出: [无，记录到日志文件]
    """
    _get_logger().warning(message)


def log_error(message: str, exception: Optional[Exception] = None) -> None:
    """
    log_error 功能说明:
    # 记录错误级别的日志
    # 输入: [message: str 错误消息, exception: Exception 异常对象] | 输出: [无，记录到日志文件]
    """
    logger = _get_logger()
    if exception:
        logger.error(f"{message} - 异常详情: {str(exception)}")
    else:
        logger.error(message)


def log_processing_start(filename: str, config: dict) -> None:
    """
    log_processing_start 功能说明:
    # 记录视频处理开始的日志
    # 输入: [filename: str 文件名, config: dict 配置信息] | 输出: [无，记录到日志文件]
    """
    logger = _get_logger()
    logger.info(f"开始处理视频: {filename}")
    logger.info(f"使用配置: {config}")


def log_processing_end(filename: str, success: bool, duration: float, output_path: str = "") -> None:
    """
    log_processing_end 功能说明:
    # 记录视频处理结束的日志
    # 输入: [filename: str 文件名, success: bool 是否成功, duration: float 处理时长, output_path: str 输出路径] | 输出: [无，记录到日志文件]
    """
    logger = _get_logger()
    status = "成功" if success else "失败"
    logger.info(f"处理完成: {filename} - 状态: {status} - 耗时: {duration:.2f}秒")
    if success and output_path:
        logger.info(f"输出文件: {output_path}")


def log_batch_summary(total: int, success: int, failed: int, total_time: float) -> None:
    """
    log_batch_summary 功能说明:
    # 记录批量处理的汇总日志
    # 输入: [total: int 总数, success: int 成功数, failed: int 失败数, total_time: float 总时间] | 输出: [无，记录到日志文件]
    """
    logger = _get_logger()
    logger.info("=" * 50)
    logger.info("批量处理汇总报告")
    logger.info(f"总文件数: {total}")
    logger.info(f"成功处理: {success}")
    logger.info(f"处理失败: {failed}")
    logger.info(f"成功率: {(success/total*100):.1f}%")
    logger.info(f"总耗时: {total_time:.2f}秒")
    logger.info(f"平均耗时: {(total_time/total):.2f}秒/文件")
    logger.info("=" * 50)
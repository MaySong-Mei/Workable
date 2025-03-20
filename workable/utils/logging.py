"""
日志工具 - 配置Workable系统的日志记录
"""

import logging
import sys
from typing import Dict, Optional, Union

def configure_logging(
    logger_name: str = "workable",
    log_level: Union[str, int] = logging.INFO,
    log_file: Optional[str] = None,
    console: bool = True,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> logging.Logger:
    """
    配置日志工具
    
    Args:
        logger_name: 日志记录器名称
        log_level: 日志级别
        log_file: 日志文件路径
        console: 是否输出到控制台
        log_format: 日志格式
        
    Returns:
        配置后的日志记录器
    """
    # 获取或创建日志记录器
    logger = logging.getLogger(logger_name)
    
    # 转换字符串日志级别为整数
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 设置根日志级别
    logging.root.setLevel(log_level)
    # 设置记录器日志级别
    logger.setLevel(log_level)
    
    # 清除现有处理程序
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # 格式化器
    formatter = logging.Formatter(log_format)
    
    # 控制台处理程序
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logging.root.addHandler(console_handler)
    
    # 文件处理程序
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logging.root.addHandler(file_handler)
    
    return logger

def configure_logging_old(
    log_level: Union[str, int] = "INFO",
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_file: Optional[str] = None,
    console_output: bool = True,
    console: Optional[bool] = None
) -> None:
    """
    配置全局日志系统
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)，可以是字符串或整数常量
        log_format: 日志格式字符串
        log_file: 日志文件路径，如果为None则不记录到文件
        console_output: 是否输出到控制台（旧参数名，保持兼容）
        console: 是否输出到控制台（新参数名）
    """
    # 兼容console参数（新参数名优先）
    if console is not None:
        console_output = console
    
    # 转换日志级别
    if isinstance(log_level, str):
        level = getattr(logging, log_level.upper())
    else:
        level = log_level
    
    # 清除之前的处理器
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 设置根日志级别
    root_logger.setLevel(level)
    
    # 创建格式器
    formatter = logging.Formatter(log_format)
    
    # 添加控制台处理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 添加文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 创建各模块专用日志器
    loggers = {
        'workable': logging.getLogger('workable'),
        'content': logging.getLogger('content'),
        'relation': logging.getLogger('relation'),
        'message': logging.getLogger('message'),
        'workable_manager': logging.getLogger('workable_manager'),
        'conversion': logging.getLogger('conversion'),
        'visualizer': logging.getLogger('workable_visualizer')
    }
    
    # 设置所有日志器级别
    for logger in loggers.values():
        logger.setLevel(level)
    
    logging.info("日志系统初始化完成") 
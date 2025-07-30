"""
日志模块，提供统一的日志记录功能
"""

import logging
import os
import sys
from typing import Optional

# 配置日志格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.INFO

# 日志存放路径
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')

# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别，默认为INFO
        
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 如果已经配置过处理器，直接返回
    if logger.handlers:
        return logger
    
    # 设置日志级别
    logger.setLevel(level or LOG_LEVEL)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)
    
    # 创建文件处理器
    log_file = os.path.join(LOG_DIR, f"{name.split('.')[-1]}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)
    
    return logger

# 默认日志记录器
default_logger = get_logger('default') 
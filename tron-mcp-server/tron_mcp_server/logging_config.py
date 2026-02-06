"""统一日志配置模块

在项目初始化时调用 setup_logging() 来统一所有模块的日志级别与格式。
可通过环境变量 LOG_LEVEL 覆盖默认日志级别（默认 INFO）。
"""

import logging
import os


def setup_logging() -> None:
    """配置项目统一的日志级别和格式"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

"""配置模块"""

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


def get_api_token() -> str:
    """获取 GetBlock API Token"""
    return os.getenv("GETBLOCK_API_TOKEN", "")


def get_api_url() -> str:
    """获取 API URL"""
    return os.getenv("TRON_API_URL", "")


def get_timeout() -> float:
    """获取请求超时时间"""
    return float(os.getenv("REQUEST_TIMEOUT", "10.0"))

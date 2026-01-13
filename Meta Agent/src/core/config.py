"""
Configuration settings for META Marketing Agent System
"""


class Config:
    """System configuration"""
    META_API_BASE_URL = "https://graph.facebook.com/v24.0"
    API_TIMEOUT = 30
    MAX_RETRIES = 3
    RATE_LIMIT_WINDOW = 3600  # 1 hour
    RATE_LIMIT_MAX_CALLS = 200

"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    APP_NAME: str = "uni-load-improved"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/uni-load.db"
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["*"]
    
    # 集成服务配置
    GPT_LOAD_MODE: str = "internal"  # internal | external
    GPT_LOAD_URL: str = "http://localhost:3001"
    GPT_LOAD_CONFIG_PATH: str = "./config/gpt-load.yaml"
    
    UNI_API_MODE: str = "internal"  # internal | external
    UNI_API_URL: str = "http://localhost:8000"
    UNI_API_CONFIG_PATH: str = "./config/uni-api.yaml"
    
    # 健康检查配置
    HEALTH_CHECK_ENABLED: bool = True
    HEALTH_CHECK_INTERVAL: int = 300  # 秒
    HEALTH_CHECK_TIMEOUT: int = 30
    HEALTH_CHECK_RETRY: int = 3
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "./logs/uni-load.log"
    
    # 安全配置
    API_KEY: str = ""  # 可选的API密钥
    ENCRYPTION_KEY: str = "your-encryption-key-here-change-in-production"
    
    # 性能配置
    WORKERS: int = 4
    MAX_CONCURRENT_REQUESTS: int = 100
    REQUEST_TIMEOUT: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
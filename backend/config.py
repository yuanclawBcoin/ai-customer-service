import os
from pydantic import BaseModel
from typing import Optional

class Settings(BaseModel):
    # MiniMax API
    minimax_api_key: str = ""
    minimax_api_url: str = "https://api.minimax.chat/v1"
    minimax_model: str = "MiniMax-Text-01"
    
    # Telegram
    tg_api_id: int = 0
    tg_api_hash: str = ""
    tg_session_name: str = "ai_customer"
    
    # 数据库
    database_url: str = "sqlite:///./data/ai客服.db"
    
    # 管理后台
    admin_username: str = "admin"
    admin_password: str = "admin123"
    secret_key: str = "change-this-in-production"
    
    # AI 设置
    max_history_length: int = 20
    memory_forget_hours: int = 24

settings = Settings()

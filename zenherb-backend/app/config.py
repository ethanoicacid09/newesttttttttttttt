import os
from typing import Optional

class Config:
    """Application configuration settings"""
    
    # Security
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "zenherb-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./zenherb.db")
    
    # Email
    SMTP_HOST: str = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER: str = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD: str = os.environ.get("SMTP_PASSWORD", "")
    
    # Frontend URL for CORS and emails
    FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    
    # Pagination
    PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

config = Config()

"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Expense Policy Enforcer"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/expenses.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    RECEIPT_FOLDER: str = "receipts"
    
    # Email (SendGrid)
    SENDGRID_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "noreply@expense-enforcer.com"
    
    # OCR
    OCR_LANG: str = "eng"
    
    class Config:
        env_file = ".env"


settings = Settings()

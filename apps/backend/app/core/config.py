from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # App Info
    APP_NAME: str = "Job Hunter AI"
    VERSION: str = "0.1.0"
    ENV: str = "development"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/database.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # LLM (OpenAI or Anthropic)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "openai"  # "openai" or "anthropic"
    LLM_MODEL: str = "gpt-4o-mini"  # or "claude-3-5-sonnet-20241022"
    
    # Azure Document Intelligence
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT: Optional[str] = None
    AZURE_DOCUMENT_INTELLIGENCE_KEY: Optional[str] = None
    
    # WhatsApp Business API
    WHATSAPP_API_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_BUSINESS_ACCOUNT_ID: Optional[str] = None
    WHATSAPP_VERIFY_TOKEN: Optional[str] = None
    
    # Job Scraping
    MAX_JOBS_PER_SEARCH: int = 50
    SCRAPER_RATE_LIMIT_DELAY: int = 2
    CACHE_TTL_HOURS: int = 24
    
    # Agent Settings
    AGENT_MAX_ITERATIONS: int = 100
    AGENT_TIMEOUT_SECONDS: int = 300
    
    # Scheduler
    DAILY_SEARCH_TIME: str = "09:00"
    DAILY_SUMMARY_TIME: str = "18:00"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env.local"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional, Union
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

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/database.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # LLM (OpenAI or Anthropic)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "openai"  # "openai" or "anthropic"
    LLM_MODEL: str = "gpt-4o-mini"  # or "claude-3-5-sonnet-20241022"
    
    # Azure Document Intelligence
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT: Optional[str] = None
    AZURE_DOCUMENT_INTELLIGENCE_KEY: Optional[str] = None
    
    # WhatsApp Business API
    WHATSAPP_API_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_BUSINESS_ACCOUNT_ID: Optional[str] = None
    WHATSAPP_VERIFY_TOKEN: str = "jobhunter_verify_token"
    
    # Job Scraping
    MAX_JOBS_PER_SEARCH: int = 50
    SCRAPER_RATE_LIMIT_DELAY: int = 2
    CACHE_TTL_HOURS: int = 24
    
    # Pinecone Vector DB
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_INDEX_NAME: str = "job-hunter-ai"
    PINECONE_ENV: str = "us-east-1"  # Optional, depending on Pinecone version
    
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

"""
Application Configuration
Centralized settings management using Pydantic
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "Health Analytics System"
    debug: bool = False
    secret_key: str = "change-this-in-production-min-32-chars"
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./health_analytics.db"
    
    # Groq AI
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_api_url: str = "https://api.groq.com/openai/v1/chat/completions"
    
    # JWT
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173,https://ssbcod.github.io"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()

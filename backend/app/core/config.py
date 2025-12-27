"""
Application Configuration
Centralized configuration management using Pydantic Settings.
All configuration is loaded from environment variables.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses Pydantic's BaseSettings for automatic environment variable parsing.
    """
    
    # ==========================================================================
    # APPLICATION SETTINGS
    # ==========================================================================
    app_name: str = "ClariFi-AI"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # ==========================================================================
    # SERVER CONFIGURATION
    # ==========================================================================
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    # ==========================================================================
    # MONGODB CONFIGURATION
    # ==========================================================================
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "clarifi_ai"
    
    # ==========================================================================
    # JWT AUTHENTICATION
    # ==========================================================================
    jwt_secret_key: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # ==========================================================================
    # OLLAMA CONFIGURATION (Primary LLM)
    # ==========================================================================
    ollama_base_url: str = "http://localhost:11434"
    ollama_fast_model: str = "phi3:mini"
    ollama_detailed_model: str = "llama3.1:8b"
    
    # ==========================================================================
    # GOOGLE GEMINI API (Fallback)
    # ==========================================================================
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    
    # ==========================================================================
    # CHROMADB CONFIGURATION
    # ==========================================================================
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "financial_knowledge"
    
    # ==========================================================================
    # EMBEDDING MODEL
    # ==========================================================================
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # ==========================================================================
    # CACHING
    # ==========================================================================
    cache_ttl_seconds: int = 300
    rate_limit_requests_per_minute: int = 60
    
    # ==========================================================================
    # LOGGING
    # ==========================================================================
    log_level: str = "INFO"
    log_file: str = "logs/clarifi_ai.log"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses LRU cache to avoid reloading settings on every request.
    """
    return Settings()


# Global settings instance
settings = get_settings()

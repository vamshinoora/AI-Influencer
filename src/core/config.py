"""Configuration management for AI Influencer system."""

import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "postgresql://localhost/ai_influencer"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Social Media APIs
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TIKTOK_ACCESS_TOKEN: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None
    
    # System Settings
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Content Generation
    MAX_CONTENT_PER_DAY: int = 15
    DEFAULT_CHARACTER_SEED: int = 42
    
    class Config:
        env_file = ".env"


settings = Settings()

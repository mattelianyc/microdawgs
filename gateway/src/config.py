from pydantic import BaseSettings, AnyHttpUrl
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    # Service URLs
    icon_service_url: str = os.getenv("ICON_SERVICE_URL", "http://icon-service:8001")
    splash_service_url: str = os.getenv("SPLASH_SERVICE_URL", "http://splash-service:8002")
    
    # Security
    jwt_secret: str = os.getenv("JWT_SECRET", "your-secret-key")
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # Rate Limiting
    rate_limit: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "100"))
    
    # Logging and Monitoring
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    enable_tracing: bool = os.getenv("ENABLE_TRACING", "true").lower() == "true"
    enable_metrics: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    
    # Service Configuration
    batch_size: int = int(os.getenv("BATCH_SIZE", "4"))
    model_cache_size: int = int(os.getenv("MODEL_CACHE_SIZE", "2048"))
    
    # Feature Flags
    enable_style_transfer: bool = os.getenv("ENABLE_STYLE_TRANSFER", "true").lower() == "true"
    enable_batch_processing: bool = os.getenv("ENABLE_BATCH_PROCESSING", "true").lower() == "true"

    class Config:
        case_sensitive = True 
from pydantic import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    # Service configuration
    model_path: str = os.getenv("MODEL_PATH", "/app/models/fine_tuned")
    device: str = os.getenv("CUDA_VISIBLE_DEVICES", "0")
    
    # Security
    jwt_secret: str = os.getenv("JWT_SECRET", "your-secret-key")
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # Logging and Monitoring
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    enable_tracing: bool = os.getenv("ENABLE_TRACING", "true").lower() == "true"
    enable_metrics: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    
    # Model Configuration
    batch_size: int = int(os.getenv("BATCH_SIZE", "4"))
    model_cache_size: int = int(os.getenv("MODEL_CACHE_SIZE", "2048"))
    num_inference_steps: int = int(os.getenv("NUM_INFERENCE_STEPS", "50"))
    guidance_scale: float = float(os.getenv("GUIDANCE_SCALE", "7.5"))
    
    # Feature Flags
    enable_style_transfer: bool = os.getenv("ENABLE_STYLE_TRANSFER", "true").lower() == "true"
    enable_layout_control: bool = os.getenv("ENABLE_LAYOUT_CONTROL", "true").lower() == "true"
    enable_ip_adapter: bool = os.getenv("ENABLE_IP_ADAPTER", "true").lower() == "true"

    class Config:
        case_sensitive = True 
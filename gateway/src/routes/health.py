from fastapi import APIRouter
from shared.models.response_schemas import BaseServiceResponse
import psutil
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=BaseServiceResponse)
async def health_check():
    """Basic health check endpoint"""
    return {
        "success": True,
        "message": "Gateway service is healthy",
        "data": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent
        }
    } 
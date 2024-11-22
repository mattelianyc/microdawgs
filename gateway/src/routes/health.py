from fastapi import APIRouter, Depends
from shared.models.response_schemas import BaseServiceResponse
from ..services.orchestrator import ServiceOrchestrator
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

@router.get("/services", response_model=BaseServiceResponse)
async def service_health(
    orchestrator: ServiceOrchestrator = Depends()
):
    """Check health of all dependent services"""
    service_status = await orchestrator.check_services_health()
    
    all_healthy = all(status["healthy"] for status in service_status.values())
    
    return {
        "success": all_healthy,
        "message": "Service health status",
        "data": service_status
    }

@router.get("/ready", response_model=BaseServiceResponse)
async def readiness_check(
    orchestrator: ServiceOrchestrator = Depends()
):
    """Readiness check endpoint"""
    try:
        # Check all critical dependencies
        deps_status = await orchestrator.check_dependencies()
        
        return {
            "success": True,
            "message": "Gateway service is ready",
            "data": deps_status
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {
            "success": False,
            "message": "Gateway service is not ready",
            "data": {"error": str(e)}
        } 
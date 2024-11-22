from fastapi import APIRouter, Depends, HTTPException
from shared.models.response_schemas import BaseServiceResponse
from shared.middleware.auth import JWTAuth
from ..services.orchestrator import ServiceOrchestrator
from ..services.queue import JobQueue
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stats", response_model=BaseServiceResponse)
@JWTAuth.requires_auth(roles=["admin"])
async def get_stats(
    orchestrator: ServiceOrchestrator = Depends()
):
    """Get system statistics"""
    stats = await orchestrator.collect_stats()
    
    return {
        "success": True,
        "message": "System statistics retrieved",
        "data": stats
    }

@router.post("/maintenance", response_model=BaseServiceResponse)
@JWTAuth.requires_auth(roles=["admin"])
async def set_maintenance(
    enabled: bool,
    orchestrator: ServiceOrchestrator = Depends()
):
    """Set maintenance mode"""
    await orchestrator.set_maintenance_mode(enabled)
    
    return {
        "success": True,
        "message": f"Maintenance mode {'enabled' if enabled else 'disabled'}",
        "data": {"maintenance": enabled}
    }

@router.delete("/jobs/{job_id}", response_model=BaseServiceResponse)
@JWTAuth.requires_auth(roles=["admin"])
async def cancel_job(
    job_id: str,
    queue: JobQueue = Depends()
):
    """Cancel processing job"""
    success = await queue.cancel_job(job_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return {
        "success": True,
        "message": "Job cancelled successfully",
        "data": {"job_id": job_id}
    }

@router.post("/reload", response_model=BaseServiceResponse)
@JWTAuth.requires_auth(roles=["admin"])
async def reload_models(
    orchestrator: ServiceOrchestrator = Depends()
):
    """Reload model weights"""
    await orchestrator.reload_models()
    
    return {
        "success": True,
        "message": "Models reloaded successfully"
    } 
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from shared.models.request_schemas import ImageGenerationRequest, BatchProcessingRequest
from shared.models.response_schemas import ImageGenerationResponse, BatchJobResponse
from ..services.orchestrator import ServiceOrchestrator
from ..services.queue import JobQueue
from ..validators.image import validate_image
from ..validators.prompt import validate_prompt
import logging
from ..middleware.rate_limiting import RateLimiter
from ..config import Settings  # Import Settings to access redis_url
from shared.middleware.auth import JWTAuth  # Import JWTAuth

logger = logging.getLogger(__name__)
router = APIRouter()

# Create an instance of RateLimiter with redis_url from settings
settings = Settings()
rate_limiter = RateLimiter(redis_url=settings.redis_url)

# Create an instance of JWTAuth
auth = JWTAuth(secret_key=settings.jwt_secret)

@router.post("/generate", response_model=ImageGenerationResponse)
@rate_limiter.rate_limit()
@auth.requires_auth()  # Use the instance to call requires_auth
async def generate_image(
    request: ImageGenerationRequest,
    orchestrator: ServiceOrchestrator = Depends()
):
    """Generate image from prompt"""
    # Validate prompt
    cleaned_prompt = await validate_prompt(request.prompt)
    request.prompt = cleaned_prompt
    
    # Process generation request
    result = await orchestrator.process_generation(request)
    
    return {
        "success": True,
        "message": "Image generation completed",
        "data": result
    }

@router.post("/batch", response_model=BatchJobResponse)
@rate_limiter.rate_limit()
@auth.requires_auth()  # Use the instance to call requires_auth
async def batch_process(
    request: BatchProcessingRequest,
    queue: JobQueue = Depends()
):
    """Submit batch processing job"""
    # Create and queue job
    job_id = await queue.submit_job(request)
    
    return {
        "success": True,
        "message": "Batch job submitted",
        "job_id": job_id,
        "status": "pending"
    }

@router.get("/batch/{job_id}", response_model=BatchJobResponse)
@auth.requires_auth()  # Use the instance to call requires_auth
async def get_batch_status(
    job_id: str,
    queue: JobQueue = Depends()
):
    """Get batch job status"""
    job_status = await queue.get_job_status(job_id)
    
    if not job_status:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return {
        "success": True,
        "message": "Job status retrieved",
        "data": job_status
    }

@router.post("/upload", response_model=ImageGenerationResponse)
@rate_limiter.rate_limit()
@auth.requires_auth()  # Use the instance to call requires_auth
async def upload_reference(
    file: UploadFile = File(...),
    orchestrator: ServiceOrchestrator = Depends()
):
    """Upload reference image"""
    # Validate uploaded image
    image = await validate_image(file)
    
    # Process reference image
    result = await orchestrator.process_reference(image)
    
    return {
        "success": True,
        "message": "Reference image processed",
        "data": result
    } 
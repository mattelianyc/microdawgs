import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from shared.models.request_schemas import ImageGenerationRequest
from shared.models.response_schemas import ImageGenerationResponse
from ..services.orchestrator import ServiceOrchestrator
from shared.utils.response_formatting import ResponseFormatter
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest, req: Request):
    """Generate image from prompt"""
    try:
        logger.info(f"Received generation request: {request.dict()}")
        
        # Initialize orchestrator using async context manager
        async with ServiceOrchestrator() as orchestrator:
            # Process generation request
            result = await orchestrator.process_generation(request)
            
            logger.info("Generation completed successfully")
            
            # Format and return response
            return ResponseFormatter.success_response(
                data={
                    "image": result.get("image"),
                    "seed": result.get("seed"),
                    "metadata": {
                        "width": request.width,
                        "height": request.height,
                        "prompt": request.prompt,
                        "negative_prompt": request.negative_prompt,
                        "style_strength": request.style_strength,
                        "timestamp": datetime.now().isoformat()
                    }
                },
                message="Image generated successfully"
            )
            
    except Exception as e:
        logger.error(f"Generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
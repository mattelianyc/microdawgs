from fastapi import APIRouter, Depends, HTTPException
from shared.models.request_schemas import ImageGenerationRequest
from shared.models.response_schemas import ImageGenerationResponse
from shared.middleware.auth import JWTAuth
from ..services.sdxl_service import SDXLService
from ..services.style_transfer import StyleTransferService
from ..config import Settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
settings = Settings()

# Initialize services
sdxl_service = SDXLService()
style_service = StyleTransferService()

async def initialize_models():
    """Initialize all required models"""
    await sdxl_service.initialize()
    if settings.enable_style_transfer:
        await style_service.initialize()

async def cleanup():
    """Cleanup model resources"""
    await sdxl_service.cleanup()
    await style_service.cleanup()

@router.post("/icon", response_model=ImageGenerationResponse)
async def generate_icon(
    request: ImageGenerationRequest,
    auth: JWTAuth = Depends()
):
    """Generate icon from prompt"""
    try:
        # Generate base image
        base_image = await sdxl_service.generate(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            num_inference_steps=settings.num_inference_steps,
            guidance_scale=settings.guidance_scale
        )
        
        # Apply style transfer if enabled
        if settings.enable_style_transfer and request.style_preset:
            base_image = await style_service.apply_style(
                image=base_image,
                style_preset=request.style_preset,
                strength=request.style_strength
            )
            
        return {
            "success": True,
            "message": "Icon generated successfully",
            "data": {
                "image": base_image,
                "seed": sdxl_service.last_seed
            }
        }
        
    except Exception as e:
        logger.error(f"Icon generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Icon generation failed"
        )

@router.post("/batch", response_model=ImageGenerationResponse)
async def generate_batch(
    request: ImageGenerationRequest,
    auth: JWTAuth = Depends()
):
    """Generate batch of icons"""
    try:
        images = []
        seeds = []
        
        for _ in range(request.batch_size):
            # Generate base image
            image = await sdxl_service.generate(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                num_inference_steps=settings.num_inference_steps,
                guidance_scale=settings.guidance_scale
            )
            
            # Apply style transfer if enabled
            if settings.enable_style_transfer and request.style_preset:
                image = await style_service.apply_style(
                    image=image,
                    style_preset=request.style_preset,
                    strength=request.style_strength
                )
                
            images.append(image)
            seeds.append(sdxl_service.last_seed)
            
        return {
            "success": True,
            "message": "Batch generation completed",
            "data": {
                "images": images,
                "seeds": seeds
            }
        }
        
    except Exception as e:
        logger.error(f"Batch generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Batch generation failed"
        ) 
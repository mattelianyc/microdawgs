from fastapi import APIRouter, Depends, HTTPException
from shared.models.request_schemas import ImageGenerationRequest
from shared.models.response_schemas import ImageGenerationResponse
from shared.middleware.auth import JWTAuth
from ..services.sdxl_service import SDXLService
from ..services.style_transfer import StyleTransferService
from ..services.ip_adapter_service import IPAdapterService
from ..config import Settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
settings = Settings()

# Initialize services
sdxl_service = SDXLService()
style_service = StyleTransferService()
ip_adapter = IPAdapterService()

async def initialize_models():
    """Initialize all required models"""
    await sdxl_service.initialize()
    if settings.enable_style_transfer:
        await style_service.initialize()
    if settings.enable_ip_adapter:
        await ip_adapter.initialize()

async def cleanup():
    """Cleanup model resources"""
    await sdxl_service.cleanup()
    await style_service.cleanup()
    await ip_adapter.cleanup()

@router.post("/splash", response_model=ImageGenerationResponse)
async def generate_splash(
    request: ImageGenerationRequest,
    auth: JWTAuth = Depends()
):
    """Generate splash image from prompt"""
    try:
        # Process reference image if provided
        if request.reference_image and settings.enable_ip_adapter:
            ip_conditioning = await ip_adapter.process_reference(
                request.reference_image
            )
        else:
            ip_conditioning = None

        # Generate base image
        base_image = await sdxl_service.generate(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            num_inference_steps=settings.num_inference_steps,
            guidance_scale=settings.guidance_scale,
            ip_conditioning=ip_conditioning
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
            "message": "Splash image generated successfully",
            "data": {
                "image": base_image,
                "seed": sdxl_service.last_seed
            }
        }
        
    except Exception as e:
        logger.error(f"Splash generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Splash generation failed"
        ) 
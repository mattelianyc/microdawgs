from fastapi import APIRouter, Depends, HTTPException
from PIL import Image
import numpy as np
from shared.models.request_schemas import ImageGenerationRequest
from shared.models.response_schemas import ImageGenerationResponse
from shared.middleware.auth import JWTAuth
from shared.adapters.controlnet import ControlNetAdapter
from ..config import Settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
settings = Settings()

# Initialize ControlNet adapter
controlnet = ControlNetAdapter(
    model_path=f"{settings.model_path}/controlnet",
    control_type="composition"  # Specialized for splash layouts
)

@router.post("/composition", response_model=ImageGenerationResponse)
async def apply_composition(
    request: ImageGenerationRequest,
    auth: JWTAuth = Depends()
):
    """Apply composition control to generation"""
    if not settings.enable_layout_control:
        raise HTTPException(
            status_code=400,
            detail="Layout control is disabled"
        )
        
    try:
        # Process composition control
        control_signal = await controlnet.preprocess({
            "control_image": request.control_image,
            "composition_type": request.composition_type
        })
        
        # Generate composition conditioning
        conditioning = await controlnet.process({
            "control_signal": control_signal["control_signal"]
        })
        
        return {
            "success": True,
            "message": "Composition control applied",
            "data": {
                "conditioning": conditioning["conditioning"]
            }
        }
        
    except Exception as e:
        logger.error(f"Composition control failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Composition control failed"
        )

@router.post("/analyze", response_model=ImageGenerationResponse)
async def analyze_composition(
    request: ImageGenerationRequest,
    auth: JWTAuth = Depends()
):
    """Analyze image composition"""
    try:
        # Analyze composition features
        composition_data = await _analyze_composition(request.reference_image)
        
        return {
            "success": True,
            "message": "Composition analysis completed",
            "data": composition_data
        }
        
    except Exception as e:
        logger.error(f"Composition analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Composition analysis failed"
        )

async def _analyze_composition(image: Image.Image) -> dict:
    """Analyze image composition and layout"""
    # Convert to numpy array
    img_array = np.array(image)
    
    # Extract composition features
    composition_data = {
        "dimensions": image.size,
        "aspect_ratio": image.size[0] / image.size[1],
        "composition": {
            "focal_points": _detect_focal_points(img_array),
            "balance": _analyze_balance(img_array),
            "visual_flow": _analyze_visual_flow(img_array)
        }
    }
    
    return composition_data

def _detect_focal_points(img_array: np.ndarray) -> list:
    """Detect main focal points in image"""
    # Implementation details...
    return [(0.5, 0.5)]  # Placeholder

def _analyze_balance(img_array: np.ndarray) -> dict:
    """Analyze visual balance"""
    # Implementation details...
    return {"horizontal": 0.8, "vertical": 0.7}  # Placeholder

def _analyze_visual_flow(img_array: np.ndarray) -> dict:
    """Analyze visual flow direction"""
    # Implementation details...
    return {"direction": "diagonal", "strength": 0.6}  # Placeholder 
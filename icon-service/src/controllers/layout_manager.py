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
    model_path=f"{settings.model_path}/controlnet"
)

@router.post("/control", response_model=ImageGenerationResponse)
async def apply_layout_control(
    request: ImageGenerationRequest,
    auth: JWTAuth = Depends()
):
    """Apply layout control to generation"""
    if not settings.enable_layout_control:
        raise HTTPException(
            status_code=400,
            detail="Layout control is disabled"
        )
        
    try:
        # Process control image
        control_signal = await controlnet.preprocess({
            "control_image": request.control_image
        })
        
        # Generate conditioning
        conditioning = await controlnet.process({
            "control_signal": control_signal["control_signal"]
        })
        
        return {
            "success": True,
            "message": "Layout control applied",
            "data": {
                "conditioning": conditioning["conditioning"]
            }
        }
        
    except Exception as e:
        logger.error(f"Layout control failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Layout control failed"
        )

@router.post("/analyze", response_model=ImageGenerationResponse)
async def analyze_layout(
    request: ImageGenerationRequest,
    auth: JWTAuth = Depends()
):
    """Analyze image layout"""
    try:
        # Convert image to layout representation
        layout_data = await _analyze_image_layout(request.reference_image)
        
        return {
            "success": True,
            "message": "Layout analysis completed",
            "data": layout_data
        }
        
    except Exception as e:
        logger.error(f"Layout analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Layout analysis failed"
        )

async def _analyze_image_layout(image: Image.Image) -> dict:
    """Analyze image layout and composition"""
    # Convert to numpy array
    img_array = np.array(image)
    
    # Extract layout features
    layout_data = {
        "dimensions": image.size,
        "aspect_ratio": image.size[0] / image.size[1],
        "composition": {
            "center_of_mass": _calculate_center_of_mass(img_array),
            "rule_of_thirds": _analyze_rule_of_thirds(img_array),
            "symmetry": _analyze_symmetry(img_array)
        }
    }
    
    return layout_data

def _calculate_center_of_mass(img_array: np.ndarray) -> tuple:
    """Calculate image center of mass"""
    # Implementation details...
    return (0.5, 0.5)  # Placeholder

def _analyze_rule_of_thirds(img_array: np.ndarray) -> dict:
    """Analyze rule of thirds composition"""
    # Implementation details...
    return {"score": 0.8}  # Placeholder

def _analyze_symmetry(img_array: np.ndarray) -> dict:
    """Analyze image symmetry"""
    # Implementation details...
    return {"horizontal": 0.7, "vertical": 0.6}  # Placeholder 
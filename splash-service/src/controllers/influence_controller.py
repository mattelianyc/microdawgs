from fastapi import APIRouter, Depends, HTTPException
from PIL import Image
import numpy as np
from shared.models.request_schemas import ImageGenerationRequest
from shared.models.response_schemas import ImageGenerationResponse
from shared.middleware.auth import JWTAuth
from shared.utils.weight_processing import WeightProcessor
from ..config import Settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
settings = Settings()

weight_processor = WeightProcessor()

@router.post("/style", response_model=ImageGenerationResponse)
async def calculate_style_influence(
    request: ImageGenerationRequest,
    auth: JWTAuth = Depends()
):
    """Calculate style influence weights"""
    try:
        # Process style reference
        style_weights = await _process_style_influence(
            request.reference_image,
            request.style_strength
        )
        
        return {
            "success": True,
            "message": "Style influence calculated",
            "data": {
                "weights": style_weights
            }
        }
        
    except Exception as e:
        logger.error(f"Style influence calculation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Style influence calculation failed"
        )

@router.post("/blend", response_model=ImageGenerationResponse)
async def blend_influences(
    request: ImageGenerationRequest,
    auth: JWTAuth = Depends()
):
    """Blend multiple influence sources"""
    try:
        # Process and blend influences
        blended_weights = await _blend_influences(
            request.reference_images,
            request.blend_weights
        )
        
        return {
            "success": True,
            "message": "Influences blended successfully",
            "data": {
                "weights": blended_weights
            }
        }
        
    except Exception as e:
        logger.error(f"Influence blending failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Influence blending failed"
        )

async def _process_style_influence(
    reference_image: Image.Image,
    strength: float
) -> np.ndarray:
    """Process style influence from reference image"""
    # Extract style features
    style_features = _extract_style_features(reference_image)
    
    # Calculate influence weights
    weights = weight_processor.normalize_weights(
        style_features,
        min_val=0.0,
        max_val=strength
    )
    
    return weights

async def _blend_influences(
    reference_images: list,
    blend_weights: list
) -> np.ndarray:
    """Blend multiple influence sources"""
    if len(reference_images) != len(blend_weights):
        raise ValueError("Number of images and weights must match")
        
    # Process each influence
    influence_weights = []
    for image, weight in zip(reference_images, blend_weights):
        weights = await _process_style_influence(image, weight)
        influence_weights.append(weights)
        
    # Blend influences
    blended = weight_processor.blend_weights(
        influence_weights[0],
        influence_weights[1],
        blend_factor=0.5
    )
    
    for weights in influence_weights[2:]:
        blended = weight_processor.blend_weights(
            blended,
            weights,
            blend_factor=0.5
        )
        
    return blended

def _extract_style_features(image: Image.Image) -> np.ndarray:
    """Extract style features from image"""
    # Implementation details...
    return np.random.rand(512)  # Placeholder 
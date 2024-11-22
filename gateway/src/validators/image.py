from fastapi import UploadFile, HTTPException
from PIL import Image
import io
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

async def validate_image(
    file: UploadFile,
    min_size: Tuple[int, int] = (32, 32),
    max_size: Tuple[int, int] = (2048, 2048)
) -> Image.Image:
    """Validate uploaded image"""
    try:
        # Check file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
            
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Check dimensions
        width, height = image.size
        if width < min_size[0] or height < min_size[1]:
            raise HTTPException(
                status_code=400,
                detail=f"Image too small. Minimum size: {min_size[0]}x{min_size[1]}"
            )
            
        if width > max_size[0] or height > max_size[1]:
            raise HTTPException(
                status_code=400,
                detail=f"Image too large. Maximum size: {max_size[0]}x{max_size[1]}"
            )
            
        return image
        
    except Exception as e:
        logger.error(f"Image validation failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Invalid image file"
        ) 
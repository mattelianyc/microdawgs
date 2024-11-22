from PIL import Image
import numpy as np
from typing import Tuple, Optional
import io
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    @staticmethod
    def resize_image(
        image: Image.Image,
        target_size: Tuple[int, int],
        method: str = "lanczos"
    ) -> Image.Image:
        """Resize image while maintaining aspect ratio"""
        if method not in ["lanczos", "bilinear", "bicubic", "nearest"]:
            raise ValueError(f"Unsupported resize method: {method}")
            
        aspect_ratio = image.size[0] / image.size[1]
        target_aspect = target_size[0] / target_size[1]

        if aspect_ratio > target_aspect:
            new_width = target_size[0]
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = target_size[1]
            new_width = int(new_height * aspect_ratio)

        resized = image.resize((new_width, new_height), getattr(Image.Resampling, method.upper()))
        
        # Create new image with padding if needed
        result = Image.new("RGBA", target_size, (0, 0, 0, 0))
        paste_x = (target_size[0] - new_width) // 2
        paste_y = (target_size[1] - new_height) // 2
        result.paste(resized, (paste_x, paste_y))
        
        return result

    @staticmethod
    def convert_format(
        image: Image.Image,
        format: str,
        quality: int = 95
    ) -> bytes:
        """Convert image to specified format"""
        if format.lower() not in ["png", "jpeg", "webp"]:
            raise ValueError(f"Unsupported format: {format}")
            
        buffer = io.BytesIO()
        image.save(buffer, format=format, quality=quality)
        return buffer.getvalue()

    @staticmethod
    def apply_watermark(
        image: Image.Image,
        watermark: Image.Image,
        opacity: float = 0.5,
        position: str = "bottom-right"
    ) -> Image.Image:
        """Apply watermark to image"""
        if opacity < 0 or opacity > 1:
            raise ValueError("Opacity must be between 0 and 1")

        # Resize watermark to reasonable size relative to main image
        max_watermark_width = image.size[0] // 4
        watermark_aspect = watermark.size[0] / watermark.size[1]
        watermark = watermark.resize(
            (max_watermark_width, int(max_watermark_width / watermark_aspect)),
            Image.Resampling.LANCZOS
        )

        # Create transparent version of watermark
        watermark = watermark.convert("RGBA")
        watermark.putalpha(int(255 * opacity))

        # Calculate position
        if position == "bottom-right":
            x = image.size[0] - watermark.size[0] - 10
            y = image.size[1] - watermark.size[1] - 10
        elif position == "bottom-left":
            x = 10
            y = image.size[1] - watermark.size[1] - 10
        else:
            raise ValueError(f"Unsupported position: {position}")

        # Paste watermark
        result = image.copy()
        result.paste(watermark, (x, y), watermark)
        return result

    @staticmethod
    def validate_image(
        image: Image.Image,
        min_size: Tuple[int, int] = (32, 32),
        max_size: Tuple[int, int] = (4096, 4096)
    ) -> bool:
        """Validate image dimensions and format"""
        try:
            if not isinstance(image, Image.Image):
                return False
                
            width, height = image.size
            
            if width < min_size[0] or height < min_size[1]:
                logger.error(f"Image too small: {width}x{height}")
                return False
                
            if width > max_size[0] or height > max_size[1]:
                logger.error(f"Image too large: {width}x{height}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Image validation error: {str(e)}")
            return False 
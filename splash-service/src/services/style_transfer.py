from typing import Optional, Dict, Any
import torch
import torch.nn as nn
from PIL import Image
import numpy as np
from ..config import Settings
import logging

logger = logging.getLogger(__name__)

class StyleTransferService:
    """Style transfer service for splash image customization"""
    def __init__(self):
        self.settings = Settings()
        self.device = f"cuda:{self.settings.device}"
        self.model = None
        self.style_models = {}

    async def initialize(self):
        """Initialize style transfer models"""
        try:
            # Load base style transfer model
            self.model = torch.load(
                f"{self.settings.model_path}/style_transfer/base_model.pt"
            ).to(self.device)
            
            # Load style-specific models
            style_paths = {
                "cinematic": "cinematic_style.pt",
                "digital-art": "digital_art_style.pt",
                "photographic": "photo_style.pt",
                "abstract": "abstract_style.pt"
            }
            
            for style, path in style_paths.items():
                self.style_models[style] = torch.load(
                    f"{self.settings.model_path}/style_transfer/{path}"
                ).to(self.device)
                
        except Exception as e:
            logger.error(f"Style transfer initialization failed: {str(e)}")
            raise

    async def apply_style(
        self,
        image: Image.Image,
        style_preset: str,
        strength: float = 1.0
    ) -> Image.Image:
        """Apply style transfer to image"""
        try:
            # Convert image to tensor
            img_tensor = self._preprocess_image(image)
            
            # Get style model
            style_model = self.style_models.get(style_preset)
            if style_model is None:
                raise ValueError(f"Unknown style preset: {style_preset}")
                
            # Apply style transfer
            with torch.inference_mode():
                styled_tensor = style_model(
                    img_tensor,
                    strength=strength
                )
                
            # Convert back to image
            styled_image = self._postprocess_tensor(styled_tensor)
            
            return styled_image
            
        except Exception as e:
            logger.error(f"Style transfer failed: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup model resources"""
        if self.model is not None:
            del self.model
            for model in self.style_models.values():
                del model
            self.style_models.clear()
            torch.cuda.empty_cache()

    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Convert PIL image to tensor"""
        # Resize to model input size
        image = image.resize((512, 512), Image.Resampling.LANCZOS)
        
        # Convert to tensor
        img_array = np.array(image).transpose(2, 0, 1)
        img_tensor = torch.tensor(img_array, dtype=torch.float32) / 255.0
        
        # Add batch dimension
        img_tensor = img_tensor.unsqueeze(0).to(self.device)
        return img_tensor

    def _postprocess_tensor(self, tensor: torch.Tensor) -> Image.Image:
        """Convert tensor to PIL image"""
        # Convert to numpy array
        img_array = (tensor.squeeze(0).cpu().numpy() * 255).astype(np.uint8)
        img_array = img_array.transpose(1, 2, 0)
        
        # Convert to PIL image
        return Image.fromarray(img_array) 
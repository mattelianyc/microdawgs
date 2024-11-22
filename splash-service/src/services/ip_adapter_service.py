from typing import Optional, Dict, Any
import torch
import torch.nn as nn
from PIL import Image
import numpy as np
from transformers import CLIPVisionModel, CLIPImageProcessor
from ..config import Settings
import logging

logger = logging.getLogger(__name__)

class IPAdapterService:
    """IP-Adapter service for image-prompt fusion"""
    def __init__(self):
        self.settings = Settings()
        self.device = f"cuda:{self.settings.device}"
        self.image_encoder = None
        self.image_processor = None
        self.ip_adapter = None

    async def initialize(self):
        """Initialize IP-Adapter models"""
        try:
            # Load CLIP vision encoder
            self.image_encoder = CLIPVisionModel.from_pretrained(
                "openai/clip-vit-large-patch14"
            ).to(self.device)
            
            self.image_processor = CLIPImageProcessor.from_pretrained(
                "openai/clip-vit-large-patch14"
            )
            
            # Load IP-Adapter weights
            self.ip_adapter = torch.load(
                f"{self.settings.model_path}/ip_adapter/ip_adapter.bin",
                map_location=self.device
            )
            
        except Exception as e:
            logger.error(f"IP-Adapter initialization failed: {str(e)}")
            raise

    async def process_reference(
        self,
        image: Image.Image,
        scale: float = 1.0
    ) -> Dict[str, torch.Tensor]:
        """Process reference image for conditioning"""
        try:
            # Preprocess image
            pixel_values = self.image_processor(
                image,
                return_tensors="pt"
            ).pixel_values.to(self.device)
            
            # Generate image embeddings
            with torch.inference_mode():
                image_embeddings = self.image_encoder(
                    pixel_values
                ).last_hidden_state
                
            # Apply IP-Adapter
            ip_embeddings = self.ip_adapter(
                image_embeddings,
                scale=scale
            )
            
            return {
                "embeddings": ip_embeddings,
                "cross_attention_dim": self.ip_adapter.config.cross_attention_dim
            }
            
        except Exception as e:
            logger.error(f"Reference processing failed: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup model resources"""
        if self.image_encoder is not None:
            del self.image_encoder
        if self.ip_adapter is not None:
            del self.ip_adapter
        torch.cuda.empty_cache() 
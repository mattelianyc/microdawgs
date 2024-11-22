from typing import Dict, Any, Optional, List
import torch
import torch.nn as nn
from PIL import Image
import numpy as np
from .base_adapter import BaseAdapter
from ..utils.image_processing import ImageProcessor

class IPAdapter(BaseAdapter):
    """Image-prompt fusion adapter"""
    def __init__(
        self,
        model_path: str,
        image_encoder_path: str,
        **kwargs
    ):
        super().__init__(model_path, **kwargs)
        self.image_encoder_path = image_encoder_path
        self.image_encoder = None
        self.image_processor = ImageProcessor()

    async def initialize(self) -> None:
        """Initialize IP-Adapter and image encoder"""
        try:
            # Load IP-Adapter model
            self.model = torch.load(self.model_path, map_location=self.device)
            
            # Load image encoder
            self.image_encoder = torch.load(
                self.image_encoder_path,
                map_location=self.device
            )
            
            self.is_initialized = True
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize IP-Adapter: {str(e)}")

    async def preprocess(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess images and prompts"""
        if not self.is_initialized:
            await self.initialize()
            
        image = input_data.get("image")
        if image is not None:
            # Convert to tensor and normalize
            image_tensor = self._prepare_image(image)
            input_data["image_embedding"] = self.image_encoder(image_tensor)
            
        return input_data

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the fusion of image and prompt"""
        image_embedding = input_data.get("image_embedding")
        text_embedding = input_data.get("text_embedding")
        
        if image_embedding is None or text_embedding is None:
            raise ValueError("Missing required embeddings")
            
        # Combine embeddings using attention
        fusion_weights = self.model.get_fusion_weights(
            image_embedding,
            text_embedding
        )
        
        return {"fusion_weights": fusion_weights}

    async def postprocess(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """Postprocess the fusion results"""
        fusion_weights = output_data.get("fusion_weights")
        
        # Apply any necessary scaling or normalization
        if fusion_weights is not None:
            fusion_weights = self._normalize_weights(fusion_weights)
            
        return {"fusion_weights": fusion_weights}

    def _prepare_image(self, image: Image.Image) -> torch.Tensor:
        """Convert PIL image to tensor and preprocess"""
        # Resize and normalize image
        image = self.image_processor.resize_image(image, (224, 224))
        image = np.array(image).transpose(2, 0, 1)
        image = torch.tensor(image, dtype=torch.float32) / 255.0
        
        # Add batch dimension
        image = image.unsqueeze(0).to(self.device)
        return image

    def _normalize_weights(self, weights: torch.Tensor) -> torch.Tensor:
        """Normalize fusion weights"""
        weights = torch.nn.functional.softmax(weights, dim=-1)
        return weights 
from typing import Optional, Dict, Any
import torch
from diffusers import StableDiffusionXLPipeline
from PIL import Image
import numpy as np
from ..config import Settings
import logging

logger = logging.getLogger(__name__)

class SDXLService:
    """SDXL model service for splash image generation"""
    def __init__(self):
        self.settings = Settings()
        self.device = f"cuda:{self.settings.device}"
        self.model = None
        self.last_seed = None

    async def initialize(self):
        """Initialize SDXL model"""
        try:
            self.model = StableDiffusionXLPipeline.from_pretrained(
                "stabilityai/stable-diffusion-xl-base-1.0",
                torch_dtype=torch.float16,
                use_safetensors=True,
                variant="fp16"
            ).to(self.device)
            
            # Enable memory optimization
            self.model.enable_model_cpu_offload()
            self.model.enable_vae_slicing()
            
        except Exception as e:
            logger.error(f"SDXL initialization failed: {str(e)}")
            raise

    async def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        ip_conditioning: Optional[Dict[str, torch.Tensor]] = None
    ) -> Image.Image:
        """Generate image from prompt with optional IP-Adapter conditioning"""
        try:
            # Set seed for reproducibility
            if seed is None:
                seed = torch.randint(0, 2**32 - 1, (1,)).item()
            self.last_seed = seed
            
            generator = torch.Generator(device=self.device).manual_seed(seed)
            
            # Generate image
            with torch.inference_mode():
                # Apply IP-Adapter conditioning if provided
                if ip_conditioning:
                    self.model.unet.config.cross_attention_dim = ip_conditioning["cross_attention_dim"]
                    cross_attention_kwargs = {"ip_conditioning": ip_conditioning["embeddings"]}
                else:
                    cross_attention_kwargs = None
                
                result = self.model(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generator,
                    cross_attention_kwargs=cross_attention_kwargs
                )
                
            return result.images[0]
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup model resources"""
        if self.model is not None:
            del self.model
            torch.cuda.empty_cache() 
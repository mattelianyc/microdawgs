import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import io
import os
import time
from huggingface_hub import snapshot_download, HfFolder
import gc
import logging
from pathlib import Path
from .state import generation_state

class StableDiffusionService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define persistent paths
        self.models_dir = Path("/app/shared/models")
        self.cache_dir = Path("/app/shared/cache")
        self.model_id = "CompVis/stable-diffusion-v1-4"
        
        # Ensure directories exist
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Set HuggingFace cache location
        os.environ['HF_HOME'] = str(self.cache_dir)
        os.environ['TRANSFORMERS_CACHE'] = str(self.cache_dir / "transformers")
        os.environ['DIFFUSERS_CACHE'] = str(self.cache_dir / "diffusers")
        
        self.device = "cpu"
        self.logger.info(f"Using device: {self.device}")
        self.logger.info(f"Cache directory: {self.cache_dir}")
        self.logger.info(f"Models directory: {self.models_dir}")
        
        self._initialize_model()

    def _is_model_cached(self):
        """Check if model files exist in cache"""
        try:
            cache_path = self.cache_dir / "diffusers" / self.model_id.replace('/', '--')
            model_path = self.models_dir / self.model_id.split('/')[-1]
            
            # Check both potential cache locations
            is_in_cache = cache_path.exists() and (cache_path / "model_index.json").exists()
            is_in_models = model_path.exists() and (model_path / "model_index.json").exists()
            
            self.logger.info(f"Model cache status - Cache: {is_in_cache}, Models: {is_in_models}")
            return is_in_cache or is_in_models
            
        except Exception as e:
            self.logger.error(f"Error checking cache: {str(e)}")
            return False

    def _initialize_model(self):
        try:
            if self._is_model_cached():
                self.logger.info("Loading model from cache...")
                # Try loading from models directory first
                try:
                    model_path = self.models_dir / self.model_id.split('/')[-1]
                    self.pipeline = StableDiffusionPipeline.from_pretrained(
                        model_path,
                        local_files_only=True,
                        safety_checker=None,
                        torch_dtype=torch.float32,
                        requires_safety_checking=False
                    )
                except Exception:
                    # Fall back to cache directory
                    cache_path = self.cache_dir / "diffusers" / self.model_id.replace('/', '--')
                    self.pipeline = StableDiffusionPipeline.from_pretrained(
                        cache_path,
                        local_files_only=True,
                        safety_checker=None,
                        torch_dtype=torch.float32,
                        requires_safety_checking=False
                    )
            else:
                self.logger.info("Downloading model for the first time...")
                # Download to cache directory
                self.pipeline = StableDiffusionPipeline.from_pretrained(
                    self.model_id,
                    cache_dir=self.cache_dir / "diffusers",
                    safety_checker=None,
                    torch_dtype=torch.float32,
                    requires_safety_checking=False
                )
                
                # Save to models directory for persistence
                model_path = self.models_dir / self.model_id.split('/')[-1]
                self.pipeline.save_pretrained(model_path)
                
            self.pipeline.to(self.device)
            self.pipeline.enable_attention_slicing()
            gc.collect()
            
        except Exception as e:
            self.logger.error(f"Error initializing model: {str(e)}")
            raise

    def generate_icon(self, prompt: str, **kwargs):
        try:
            self.logger.info(f"Generating icon with prompt: {prompt}")
            generation_state.reset()

            def update_progress(step: int, timestep: int, latents: any):
                progress = int((step / kwargs.get('num_steps', 20)) * 100)
                generation_state.update_progress(
                    progress=progress,
                    message=f"Step {step} of {kwargs.get('num_steps', 20)}"
                )
                self.logger.info(f"Progress: {progress}%")

            # Generate the image
            output = self.pipeline(
                prompt=f"{prompt}, minimalist professional app icon design, clean lines, simple shapes, flat design",
                num_inference_steps=kwargs.get('num_steps', 20),
                guidance_scale=kwargs.get('guidance_scale', 7.5),
                height=512,
                width=512,
                callback=update_progress,
                callback_steps=1
            ).images[0]

            # Convert to bytes
            img_byte_arr = io.BytesIO()
            output.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            # Set final progress
            generation_state.update_progress(100, "Generation complete!")

            return img_byte_arr.getvalue()

        except Exception as e:
            self.logger.error(f"Error generating image: {str(e)}")
            raise 
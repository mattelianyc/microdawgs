import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import io
import os
import time
from huggingface_hub import snapshot_download
import gc
import logging
from pathlib import Path

class StableDiffusionService:
    def __init__(self):
        self.model_id = os.getenv("MODEL_ID", "CompVis/stable-diffusion-v1-4")
        self.device = "cpu"
        self.cache_dir = Path("/root/.cache/huggingface")
        print(f"Using device: {self.device}")
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self._initialize_model()

    def _download_with_retry(self):
        retry_count = 0
        wait_time = 10  # Consistent 10 second wait between retries
        
        while True:  # Keep trying indefinitely
            try:
                retry_count += 1
                self.logger.info(f"Downloading model attempt {retry_count}")
                
                # Download model files with snapshot_download
                snapshot_download(
                    repo_id=self.model_id,
                    cache_dir=self.cache_dir,
                    local_files_only=False,
                    resume_download=True,
                    max_workers=1,  # Reduce concurrent downloads
                    tqdm_class=None
                )
                return True
                
            except Exception as e:
                self.logger.error(f"Download attempt {retry_count} failed: {str(e)}")
                self.logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)  # Consistent wait time
                gc.collect()  # Clean up memory between attempts

    def _initialize_model(self):
        retry_count = 0
        wait_time = 10  # Consistent 10 second wait between retries
        
        while True:  # Keep trying indefinitely
            try:
                # First ensure model is downloaded
                self._download_with_retry()
                
                # Initialize pipeline with minimal components
                self.pipeline = StableDiffusionPipeline.from_pretrained(
                    self.model_id,
                    torch_dtype=torch.float32,
                    safety_checker=None,
                    requires_safety_checking=False,
                    use_safetensors=True,
                    low_cpu_mem_usage=True,
                    cache_dir=self.cache_dir,
                    local_files_only=True  # Use downloaded files
                )
                self.pipeline.to(self.device)

                # Enable memory efficient settings
                self.pipeline.enable_attention_slicing(slice_size="max")
                
                # Clear any unused memory
                gc.collect()
                
                self.logger.info("Model loaded successfully")
                break
                
            except Exception as e:
                retry_count += 1
                self.logger.error(f"Model initialization attempt {retry_count} failed: {str(e)}")
                self.logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)  # Consistent wait time
                gc.collect()  # Clean up memory between attempts

    async def generate_icon(self, prompt: str, reference_image: Image.Image = None, **kwargs):
        try:
            # Set lower inference steps for CPU
            num_steps = min(kwargs.get('num_steps', 20), 30)
            
            # Generate image
            output = self.pipeline(
                prompt=prompt,
                num_inference_steps=num_steps,
                guidance_scale=kwargs.get('guidance_scale', 7.5)
            ).images[0]

            # Convert to bytes
            img_byte_arr = io.BytesIO()
            output.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()

        except Exception as e:
            self.logger.error(f"Error generating image: {str(e)}")
            raise Exception(f"Error generating image: {str(e)}") 
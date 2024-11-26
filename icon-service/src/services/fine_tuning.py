import torch
from pathlib import Path
from diffusers import StableDiffusionPipeline
from datasets import Dataset
import os
import logging
from PIL import Image
import zipfile
import io
import gc
from fastapi import APIRouter, HTTPException

class FineTuningService:
    def __init__(self, model_path="/app/models/fine_tuned"):
        self.logger = logging.getLogger(__name__)
        self.model_path = Path(model_path)
        self.model_path.mkdir(parents=True, exist_ok=True)
        self.device = "cpu"
        self.router = APIRouter()
        self.setup_routes()
        
    def setup_routes(self):
        @self.router.get("/training-status")
        async def get_training_status():
            return {
                "status": training_status.status,
                "progress": training_status.progress,
                "error": training_status.error
            }

        @self.router.post("/start-training")
        async def start_training():
            # Your existing start training code
            pass
        
    async def process_training_images(self, zip_file_bytes):
        """Process uploaded ZIP file containing training images"""
        try:
            # Create temporary directory for extracted images
            temp_dir = Path("/tmp/training_images")
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract ZIP contents
            with zipfile.ZipFile(io.BytesIO(
              zip_file_bytes)) as zip_ref:
                zip_ref.extractall(temp_dir)
            
            processed_images = []
            image_paths = list(temp_dir.glob("*.png"))
            
            for img_path in image_paths:
                try:
                    image = Image.open(img_path).convert('RGB')
                    processed_images.append({
                        "image": image,
                        "text": "a minimalist professional app icon design, clean lines, simple shapes, flat design"
                    })
                except Exception as e:
                    self.logger.error(f"Error processing image {img_path}: {str(e)}")
            
            return processed_images
            
        except Exception as e:
            self.logger.error(f"Error processing training data: {str(e)}")
            raise
            
    async def _load_base_model(self):
        """Load the base model for fine-tuning, using cache if available"""
        self._ensure_cache_dir()
        
        if self._is_model_cached(self.base_model_id):
            self.logger.info("Loading base model from cache...")
            return StableDiffusionPipeline.from_pretrained(
                os.path.join(self.cache_dir, self.base_model_id),
                local_files_only=True
            )
        else:
            self.logger.info("Base model not found in cache. Downloading...")
            return StableDiffusionPipeline.from_pretrained(
                self.base_model_id,
                cache_dir=self.cache_dir
            )
    
    async def fine_tune_model(self, processed_images, num_epochs=20):
        """Fine-tune the model on the icon aesthetic"""
        try:
            dataset = Dataset.from_dict({
                "image": [item["image"] for item in processed_images],
                "text": [item["text"] for item in processed_images]
            })
            
            # Load base model with memory optimizations
            pipeline = await self._load_base_model()
            
            # Enable memory efficient settings
            pipeline.enable_attention_slicing(slice_size="auto")
            
            # Training configuration
            training_args = {
                "output_dir": self.model_path,
                "learning_rate": 1e-5,
                "max_train_steps": num_epochs * len(processed_images),
                "train_batch_size": 1,
                "gradient_accumulation_steps": 4,
                "gradient_checkpointing": True,
                "mixed_precision": "no"
            }
            
            # Train the model
            pipeline.train(
                dataset=dataset,
                **training_args
            )
            
            # Save the fine-tuned model
            pipeline.save_pretrained(self.model_path)
            
            return {
                "status": "success",
                "model_path": str(self.model_path)
            }
            
        except Exception as e:
            self.logger.error(f"Error during fine-tuning: {str(e)}")
            raise
        finally:
            gc.collect()

class TrainingStatus:
    def __init__(self):
        self.status = "idle"
        self.progress = 0
        self.error = None

    def update(self, status, progress=None, error=None):
        self.status = status
        if progress is not None:
            self.progress = progress
        if error is not None:
            self.error = error

training_status = TrainingStatus()
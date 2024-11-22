from typing import Dict, Any, List
import torch
import torch.nn as nn
from torchmetrics.image import FID, SSIM, PSNR
from PIL import Image
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import logging
import json
from tqdm import tqdm

logger = logging.getLogger(__name__)

class ModelEvaluator:
    """Evaluate model performance"""
    def __init__(self, config_path: str = "config/eval_config.json"):
        self.config = self._load_config(config_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.metrics = self._setup_metrics()

    def evaluate(
        self,
        model: nn.Module,
        eval_dataloader: torch.utils.data.DataLoader
    ) -> Dict[str, float]:
        """Evaluate model on test dataset"""
        logger.info("Starting evaluation...")
        model.eval()
        
        metrics_results = {
            "fid": [],
            "ssim": [],
            "psnr": []
        }
        
        with torch.no_grad():
            for batch in tqdm(eval_dataloader, desc="Evaluating"):
                # Generate images
                generated = self._generate_batch(model, batch)
                
                # Calculate metrics
                batch_metrics = self._calculate_metrics(
                    generated["images"],
                    batch["images"]
                )
                
                # Store results
                for key, value in batch_metrics.items():
                    metrics_results[key].append(value)

        # Average metrics
        final_metrics = {
            key: np.mean(values)
            for key, values in metrics_results.items()
        }
        
        # Log results
        self._log_results(final_metrics)
        
        return final_metrics

    def generate_samples(
        self,
        model: nn.Module,
        prompts: List[str],
        num_samples: int = 4
    ) -> List[Image.Image]:
        """Generate sample images for visualization"""
        model.eval()
        samples = []
        
        with torch.no_grad():
            for prompt in prompts:
                for _ in range(num_samples):
                    sample = self._generate_single(model, prompt)
                    samples.append(sample)
                    
        return samples

    def _calculate_metrics(
        self,
        generated: torch.Tensor,
        real: torch.Tensor
    ) -> Dict[str, float]:
        """Calculate evaluation metrics"""
        return {
            "fid": self.metrics["fid"](generated, real),
            "ssim": self.metrics["ssim"](generated, real),
            "psnr": self.metrics["psnr"](generated, real)
        }

    def _setup_metrics(self) -> Dict[str, Any]:
        """Initialize evaluation metrics"""
        return {
            "fid": FID().to(self.device),
            "ssim": SSIM().to(self.device),
            "psnr": PSNR().to(self.device)
        }

    def _generate_batch(
        self,
        model: nn.Module,
        batch: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate images for a batch"""
        return model(
            prompt=batch["prompts"],
            num_inference_steps=self.config["num_inference_steps"],
            guidance_scale=self.config["guidance_scale"]
        )

    def _generate_single(
        self,
        model: nn.Module,
        prompt: str
    ) -> Image.Image:
        """Generate single image"""
        result = model(
            prompt=prompt,
            num_inference_steps=self.config["num_inference_steps"],
            guidance_scale=self.config["guidance_scale"]
        )
        return result.images[0]

    def _log_results(self, metrics: Dict[str, float]):
        """Log evaluation results"""
        logger.info("Evaluation Results:")
        for metric, value in metrics.items():
            logger.info(f"{metric}: {value:.4f}")
            
        # Save results to file
        results_dir = Path(self.config["results_dir"])
        results_dir.mkdir(exist_ok=True)
        
        with open(results_dir / "eval_results.json", "w") as f:
            json.dump(metrics, f, indent=4)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load evaluation configuration"""
        with open(config_path) as f:
            return json.load(f) 
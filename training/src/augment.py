from typing import List, Dict, Any
import torch
from torchvision import transforms
from PIL import Image
import numpy as np
import albumentations as A
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DataAugmenter:
    """Handle data augmentation for training"""
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.transform = self._build_transform()

    def augment_batch(
        self,
        images: List[Image.Image],
        prompts: List[str]
    ) -> Dict[str, Any]:
        """Augment a batch of images and prompts"""
        augmented_images = []
        augmented_prompts = []
        
        for image, prompt in zip(images, prompts):
            # Apply augmentations
            aug_result = self._augment_pair(image, prompt)
            augmented_images.extend(aug_result["images"])
            augmented_prompts.extend(aug_result["prompts"])
            
        return {
            "images": augmented_images,
            "prompts": augmented_prompts
        }

    def _augment_pair(
        self,
        image: Image.Image,
        prompt: str
    ) -> Dict[str, Any]:
        """Augment single image-prompt pair"""
        results = {
            "images": [],
            "prompts": []
        }
        
        # Convert to numpy for albumentations
        image_np = np.array(image)
        
        # Apply each augmentation
        for _ in range(self.config["num_augmentations"]):
            augmented = self.transform(image=image_np)
            aug_image = Image.fromarray(augmented["image"])
            
            results["images"].append(aug_image)
            results["prompts"].append(prompt)  # Keep original prompt
            
        return results

    def _build_transform(self) -> A.Compose:
        """Build augmentation pipeline"""
        return A.Compose([
            A.RandomRotate90(p=0.5),
            A.Flip(p=0.5),
            A.OneOf([
                A.RandomBrightness(limit=0.2),
                A.RandomContrast(limit=0.2),
                A.RandomGamma()
            ], p=0.5),
            A.OneOf([
                A.GaussNoise(var_limit=(10.0, 50.0)),
                A.ISONoise(),
                A.MultiplicativeNoise()
            ], p=0.3),
            A.OneOf([
                A.Blur(blur_limit=3),
                A.GaussianBlur(blur_limit=3),
                A.MotionBlur(blur_limit=3)
            ], p=0.3),
            A.ColorJitter(
                brightness=0.2,
                contrast=0.2,
                saturation=0.2,
                hue=0.1,
                p=0.5
            )
        ], p=1.0)

    def _default_config(self) -> Dict[str, Any]:
        """Default augmentation configuration"""
        return {
            "num_augmentations": 4,
            "min_area_ratio": 0.8,
            "brightness_range": 0.2,
            "contrast_range": 0.2,
            "saturation_range": 0.2,
            "hue_range": 0.1
        } 
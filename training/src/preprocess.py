from typing import Tuple, List
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import numpy as np
from pathlib import Path
import pandas as pd
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)

class ImageTextDataset(Dataset):
    """Dataset for image-text pairs"""
    def __init__(
        self,
        image_paths: List[str],
        prompts: List[str],
        transform=None
    ):
        self.image_paths = image_paths
        self.prompts = prompts
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        # Load image
        image = Image.open(self.image_paths[idx]).convert('RGB')
        prompt = self.prompts[idx]
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
            
        return {
            "image": image,
            "prompt": prompt
        }

class DataPreprocessor:
    """Handle data preprocessing and loading"""
    def __init__(self, image_size: Tuple[int, int] = (512, 512)):
        self.image_size = image_size

    def prepare_data(
        self,
        data_path: str,
        batch_size: int
    ) -> DataLoader:
        """Prepare data for training"""
        # Load and preprocess data
        image_paths, prompts = self._load_data(data_path)
        
        # Create dataset
        dataset = ImageTextDataset(
            image_paths,
            prompts,
            transform=self._get_transforms()
        )
        
        # Create dataloader
        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=4
        )
        
        return dataloader

    def _load_data(self, data_path: str) -> Tuple[List[str], List[str]]:
        """Load image paths and prompts"""
        data_path = Path(data_path)
        metadata_path = data_path / "metadata.csv"
        
        # Load metadata
        df = pd.read_csv(metadata_path)
        
        # Get image paths and prompts
        image_paths = [str(data_path / "images" / p) for p in df["image_name"]]
        prompts = df["prompt"].tolist()
        
        return image_paths, prompts

    def _get_transforms(self):
        """Get image transforms"""
        from torchvision import transforms
        
        return transforms.Compose([
            transforms.Resize(self.image_size),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.5, 0.5, 0.5],
                std=[0.5, 0.5, 0.5]
            )
        ]) 
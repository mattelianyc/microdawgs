import torch
from diffusers import StableDiffusionXLPipeline, UNet2DConditionModel
from transformers import CLIPTextModel
from accelerate import Accelerator
import wandb
from pathlib import Path
import logging
from tqdm import tqdm
import os
from .preprocess import DataPreprocessor
from .augment import DataAugmenter

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, config_path: str = "config/training_config.json"):
        self.config = self._load_config(config_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.accelerator = Accelerator()
        self.preprocessor = DataPreprocessor()
        self.augmenter = DataAugmenter()

    def setup(self):
        """Initialize models and training components"""
        # Load base models
        self.text_encoder = CLIPTextModel.from_pretrained(
            self.config["base_model_path"]
        ).to(self.device)
        
        self.unet = UNet2DConditionModel.from_pretrained(
            self.config["base_model_path"],
            subfolder="unet"
        ).to(self.device)

        # Setup optimizer
        self.optimizer = torch.optim.AdamW(
            self.unet.parameters(),
            lr=self.config["learning_rate"]
        )

        # Initialize wandb
        if self.config["use_wandb"]:
            wandb.init(project=self.config["project_name"])

    def train(self):
        """Main training loop"""
        logger.info("Starting training...")
        
        # Prepare dataset
        train_dataloader = self.preprocessor.prepare_data(
            self.config["data_path"],
            self.config["batch_size"]
        )

        # Training loop
        for epoch in range(self.config["num_epochs"]):
            self.unet.train()
            total_loss = 0
            
            with tqdm(train_dataloader) as pbar:
                for batch in pbar:
                    # Process batch
                    loss = self._training_step(batch)
                    total_loss += loss.item()
                    
                    # Update progress bar
                    pbar.set_description(f"Epoch {epoch}")
                    pbar.set_postfix(loss=loss.item())

            # Log metrics
            avg_loss = total_loss / len(train_dataloader)
            self._log_metrics({"loss": avg_loss}, epoch)
            
            # Save checkpoint
            if (epoch + 1) % self.config["save_every"] == 0:
                self._save_checkpoint(epoch)

    def _training_step(self, batch):
        """Single training step"""
        self.optimizer.zero_grad()
        
        # Get inputs
        images = batch["images"].to(self.device)
        prompts = batch["prompts"]
        
        # Forward pass
        with torch.cuda.amp.autocast():
            # Get text embeddings
            text_embeddings = self.text_encoder(prompts)[0]
            
            # Generate latents
            latents = self.unet(
                images,
                text_embeddings,
                return_dict=False
            )[0]
            
            # Calculate loss
            loss = torch.nn.functional.mse_loss(latents, images)

        # Backward pass
        self.accelerator.backward(loss)
        self.optimizer.step()
        
        return loss

    def _save_checkpoint(self, epoch):
        """Save model checkpoint"""
        checkpoint_dir = Path(self.config["checkpoint_dir"])
        checkpoint_dir.mkdir(exist_ok=True)
        
        checkpoint_path = checkpoint_dir / f"checkpoint_epoch_{epoch}.pt"
        torch.save({
            'epoch': epoch,
            'unet_state_dict': self.unet.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, checkpoint_path)

    def _log_metrics(self, metrics: dict, epoch: int):
        """Log training metrics"""
        if self.config["use_wandb"]:
            wandb.log(metrics, step=epoch)
            
        logger.info(f"Epoch {epoch} metrics: {metrics}")

    def _load_config(self, config_path: str) -> dict:
        """Load training configuration"""
        import json
        with open(config_path) as f:
            return json.load(f)

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize and run trainer
    trainer = ModelTrainer()
    trainer.setup()
    trainer.train() 
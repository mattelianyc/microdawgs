# ./fine_tune_sd.py
import os
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from transformers import AdamW
from diffusers import UNet2DConditionModel, AutoencoderKL
import torch
from torchvision import transforms

class IconDataset(Dataset):
    def __init__(self, image_paths, image_size=(512, 512)):
        self.image_paths = image_paths
        self.transform = transforms.Compose([
            transforms.Resize(image_size),
            transforms.ToTensor(),  # Converts PIL image to PyTorch tensor and scales pixel values to [0, 1]
        ])

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image = Image.open(self.image_paths[idx]).convert("RGB")
        image = self.transform(image)  # Apply transformations
        return image

def fine_tune_model(image_dir):
    # Collect all png images
    image_paths = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith('.png')]

    dataset = IconDataset(image_paths)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

    # Determine if CUDA is available
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Load model components
    vae = AutoencoderKL.from_pretrained("CompVis/stable-diffusion-v1-4", subfolder="vae").to(device)
    unet = UNet2DConditionModel.from_pretrained("CompVis/stable-diffusion-v1-4", subfolder="unet").to(device)

    # Define optimizer
    optimizer = AdamW(unet.parameters(), lr=1e-5)

    # Dummy timestep and encoder_hidden_states
    dummy_timestep = torch.tensor([1.0], device=device)
    dummy_encoder_hidden_states = torch.zeros((1, 77, unet.config.cross_attention_dim), device=device)

    # Training loop
    for epoch in range(5):  # Adjust the number of epochs as needed
        for batch in dataloader:
            batch = batch.to(device)

            # Generate latent space representation using VAE
            latents = vae.encode(batch).latent_dist.sample()
            latents = latents * vae.config.scaling_factor  # Scale the latents

            # Ensure latents are the correct shape (adjust as necessary for your UNet model)
            latents = torch.nn.functional.interpolate(latents, size=(unet.config.sample_size, unet.config.sample_size))

            # Forward pass through UNet with dummy timestep and encoder_hidden_states
            noise_pred = unet(latents, timestep=dummy_timestep, encoder_hidden_states=dummy_encoder_hidden_states)

            # Loss calculation and backpropagation
            loss = torch.nn.functional.mse_loss(noise_pred, latents)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            print(f"Epoch: {epoch}, Loss: {loss.item()}")

    # Save the fine-tuned model
    unet.save_pretrained("fine_tuned_unet")
    return "Fine-tuning complete"

if __name__ == "__main__":
    image_dir = "images"  # Directory containing PNG images
    fine_tune_model(image_dir)

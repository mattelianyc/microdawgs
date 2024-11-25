# /fine_tune_service/fine_tune_sd3.py
import os
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from transformers import CLIPProcessor, CLIPModel
from diffusers import StableDiffusionPipeline
from transformers import AdamW
import torch

class IconDataset(Dataset):
    def __init__(self, image_paths, texts, processor):
        self.image_paths = image_paths
        self.texts = texts
        self.processor = processor

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image = Image.open(self.image_paths[idx]).convert("RGB")
        text = self.texts[idx]
        inputs = self.processor(text=text, images=image, return_tensors="pt", padding=True)
        return inputs

def fine_tune_model(image_paths, texts):
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    dataset = IconDataset(image_paths, texts, processor)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

    # Load models
    text_encoder = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    image_encoder = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-3-medium-diffusers").to("cuda")

    # Define optimizer
    optimizer = AdamW(list(text_encoder.parameters()) + list(image_encoder.parameters()), lr=1e-5)

    # Training loop
    for epoch in range(5):  # Adjust the number of epochs
        for batch in dataloader:
            inputs = {k: v.to("cuda") for k, v in batch.items()}
            optimizer.zero_grad()
            outputs = image_encoder(**inputs)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            print(f"Epoch: {epoch}, Loss: {loss.item()}")

    # Save the fine-tuned model
    text_encoder.save_pretrained("fine_tuned_text_encoder")
    image_encoder.save_pretrained("fine_tuned_image_encoder")

if __name__ == "__main__":
    image_paths = ["path/to/image1.png", "path/to/image2.png"]  # Update with your image paths
    texts = ["description1", "description2"]  # Update with your image descriptions
    fine_tune_model(image_paths, texts)


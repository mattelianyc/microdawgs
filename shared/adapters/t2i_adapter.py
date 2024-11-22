from typing import Dict, Any, Optional
import torch
import torch.nn as nn
from transformers import CLIPTextModel, CLIPTokenizer
from .base_adapter import BaseAdapter

class T2IAdapter(BaseAdapter):
    """Text-to-image adapter"""
    def __init__(
        self,
        model_path: str,
        tokenizer_path: str,
        **kwargs
    ):
        super().__init__(model_path, **kwargs)
        self.tokenizer_path = tokenizer_path
        self.tokenizer = None
        self.max_length = kwargs.get("max_length", 77)

    async def initialize(self) -> None:
        """Initialize text encoder and tokenizer"""
        try:
            self.model = CLIPTextModel.from_pretrained(
                self.model_path
            ).to(self.device)
            self.tokenizer = CLIPTokenizer.from_pretrained(
                self.tokenizer_path
            )
            self.is_initialized = True
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize T2I-Adapter: {str(e)}")

    async def preprocess(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess text input"""
        if not self.is_initialized:
            await self.initialize()
            
        prompt = input_data.get("prompt", "")
        negative_prompt = input_data.get("negative_prompt", "")
        
        # Tokenize inputs
        tokens = self._tokenize_text(prompt)
        neg_tokens = self._tokenize_text(negative_prompt)
        
        return {
            "tokens": tokens,
            "negative_tokens": neg_tokens
        }

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate embeddings from tokens"""
        tokens = input_data.get("tokens")
        neg_tokens = input_data.get("negative_tokens")
        
        # Generate embeddings
        with torch.no_grad():
            text_embeddings = self.model(tokens)[0]
            if neg_tokens is not None:
                neg_embeddings = self.model(neg_tokens)[0]
            else:
                neg_embeddings = None
                
        return {
            "text_embeddings": text_embeddings,
            "negative_embeddings": neg_embeddings
        }

    async def postprocess(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """Postprocess the embeddings"""
        text_embeddings = output_data.get("text_embeddings")
        neg_embeddings = output_data.get("negative_embeddings")
        
        if neg_embeddings is not None:
            # Combine positive and negative embeddings
            embeddings = torch.cat([neg_embeddings, text_embeddings])
        else:
            embeddings = text_embeddings
            
        return {"embeddings": embeddings}

    def _tokenize_text(self, text: str) -> torch.Tensor:
        """Tokenize input text"""
        if not text:
            return None
            
        tokens = self.tokenizer(
            text,
            padding="max_length",
            max_length=self.max_length,
            truncation=True,
            return_tensors="pt"
        )
        
        return tokens.input_ids.to(self.device) 
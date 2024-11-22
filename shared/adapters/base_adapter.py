from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import torch
import logging
from ..models.base import BaseImageModel

logger = logging.getLogger(__name__)

class BaseAdapter(ABC):
    """Abstract base class for all adapters"""
    def __init__(
        self,
        model_path: str,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        **kwargs
    ):
        self.model_path = model_path
        self.device = device
        self.model = None
        self.is_initialized = False
        self.config = kwargs

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the adapter and load models"""
        pass

    @abstractmethod
    async def preprocess(self, input_data: Any) -> Any:
        """Preprocess input data"""
        pass

    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """Process the input and generate output"""
        pass

    @abstractmethod
    async def postprocess(self, output_data: Any) -> Any:
        """Postprocess the output data"""
        pass

    async def cleanup(self) -> None:
        """Clean up resources"""
        if self.model is not None:
            del self.model
            torch.cuda.empty_cache()
        self.is_initialized = False

    async def validate_input(self, input_data: Any) -> bool:
        """Validate input data"""
        return True

    async def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle and format errors"""
        logger.error(f"Adapter error: {str(error)}", exc_info=True)
        return {
            "success": False,
            "error": str(error),
            "error_type": error.__class__.__name__
        } 
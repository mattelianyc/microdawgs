from typing import Dict, Any, Optional
import aiohttp
import asyncio
import logging
from ..config import Settings
from shared.models.request_schemas import ImageGenerationRequest
from shared.utils.error_handling import BaseError
from datetime import datetime
import json
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class ServiceOrchestrator:
    """Orchestrate requests between services"""
    def __init__(self):
        self.settings = Settings()
        self.session = None
        self.services = {
            "icon": self.settings.icon_service_url,
            "splash": self.settings.splash_service_url
        }

    async def initialize(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                json_serialize=lambda obj: json.dumps(obj, default=str)  # Handle datetime serialization
            )

    async def cleanup(self):
        """Cleanup resources"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def process_generation(self, request: ImageGenerationRequest) -> Dict[str, Any]:
        """Process image generation request"""
        await self.initialize()
        
        try:
            # Get icon service URL
            service_url = self.services["icon"]
            logger.info(f"Sending request to icon service at {service_url}")
            
            # Prepare request data
            request_data = request.dict()
            
            # Make request to service
            async with self.session.post(
                f"{service_url}/generate/icon",  # Updated endpoint path
                json=request_data,
                timeout=60  # Increased timeout for generation
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    logger.error(f"Service error: {error_data}")
                    raise HTTPException(
                        status_code=response.status,
                        detail=error_data.get("detail", "Generation failed")
                    )
                    
                result = await response.json()
                logger.info("Successfully received response from icon service")
                return result["data"]
                
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Generation service error: {str(e)}"
            )

    def _get_service_for_request(self, request: ImageGenerationRequest) -> str:
        """Determine appropriate service for request"""
        return "icon"  # Default to icon service for now

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup() 
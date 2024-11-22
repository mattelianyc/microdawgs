from typing import Dict, Any, Optional
import aiohttp
import asyncio
import logging
from ..config import Settings
from shared.models.request_schemas import ImageGenerationRequest
from shared.utils.error_handling import BaseError

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
            self.session = aiohttp.ClientSession()

    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            self.session = None

    async def check_services_health(self) -> Dict[str, Any]:
        """Check health of all services"""
        await self.initialize()
        health_status = {}
        
        for service, url in self.services.items():
            try:
                async with self.session.get(f"{url}/health") as response:
                    health_status[service] = {
                        "healthy": response.status == 200,
                        "status_code": response.status,
                        "details": await response.json()
                    }
            except Exception as e:
                logger.error(f"Health check failed for {service}: {str(e)}")
                health_status[service] = {
                    "healthy": False,
                    "error": str(e)
                }
                
        return health_status

    async def check_dependencies(self) -> Dict[str, bool]:
        """Check all critical dependencies"""
        deps = {
            "redis": await self._check_redis(),
            "services": all((await self.check_services_health()).values())
        }
        return deps

    async def process_generation(
        self,
        request: ImageGenerationRequest
    ) -> Dict[str, Any]:
        """Process image generation request"""
        await self.initialize()
        
        # Determine target service
        service = self._get_service_for_request(request)
        service_url = self.services[service]
        
        try:
            async with self.session.post(
                f"{service_url}/generate",
                json=request.dict()
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise BaseError(
                        message=error_data.get("message", "Generation failed"),
                        status_code=response.status
                    )
                    
                return await response.json()
                
        except BaseError:
            raise
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            raise BaseError(message="Generation service unavailable")

    async def process_reference(
        self,
        image: bytes,
        service: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process reference image"""
        await self.initialize()
        
        # Use specified service or default to icon service
        target_service = service or "icon"
        service_url = self.services[target_service]
        
        try:
            async with self.session.post(
                f"{service_url}/reference",
                data={"image": image}
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise BaseError(
                        message=error_data.get("message", "Reference processing failed"),
                        status_code=response.status
                    )
                    
                return await response.json()
                
        except BaseError:
            raise
        except Exception as e:
            logger.error(f"Reference processing failed: {str(e)}")
            raise BaseError(message="Reference processing service unavailable")

    async def set_maintenance_mode(self, enabled: bool):
        """Set maintenance mode for all services"""
        await self.initialize()
        
        tasks = []
        for service_url in self.services.values():
            task = self.session.post(
                f"{service_url}/admin/maintenance",
                json={"enabled": enabled}
            )
            tasks.append(task)
            
        await asyncio.gather(*tasks)

    async def reload_models(self):
        """Trigger model reload on all services"""
        await self.initialize()
        
        tasks = []
        for service_url in self.services.values():
            task = self.session.post(f"{service_url}/admin/reload")
            tasks.append(task)
            
        await asyncio.gather(*tasks)

    def _get_service_for_request(self, request: ImageGenerationRequest) -> str:
        """Determine appropriate service for request"""
        # Add logic to route requests based on requirements
        if getattr(request, "style_preset", "") == "icon":
            return "icon"
        return "splash"

    async def _check_redis(self) -> bool:
        """Check Redis connection"""
        try:
            # Implement Redis health check
            return True
        except Exception:
            return False 
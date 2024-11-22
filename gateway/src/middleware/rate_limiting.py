from fastapi import Request, HTTPException
from shared.middleware.rate_limiting import RateLimiter
from ..config import Settings
import logging

logger = logging.getLogger(__name__)

class GatewayRateLimiter(RateLimiter):
    """Gateway-specific rate limiting middleware"""
    def __init__(self):
        settings = Settings()
        super().__init__(
            redis_url=settings.redis_url,
            default_limit=settings.rate_limit
        )

    async def check_service_limits(
        self,
        request: Request,
        service_name: str
    ):
        """Check service-specific rate limits"""
        service_key = f"ratelimit:service:{service_name}"
        
        # Get service-specific limits from config/cache
        service_limit = await self._get_service_limit(service_name)
        
        rate_info = await self.check_rate_limit(
            service_key,
            limit=service_limit
        )
        
        if not rate_info["allowed"]:
            raise HTTPException(
                status_code=429,
                detail=f"Service rate limit exceeded for {service_name}"
            )

    async def _get_service_limit(self, service_name: str) -> int:
        """Get service-specific rate limit"""
        # Could be extended to load from database/cache
        service_limits = {
            "icon-service": 50,
            "splash-service": 30
        }
        return service_limits.get(service_name, self.default_limit) 
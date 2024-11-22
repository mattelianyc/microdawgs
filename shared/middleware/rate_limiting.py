from typing import Optional, Dict, Any
import time
import asyncio
from fastapi import Request, HTTPException
import redis
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting middleware using Redis"""
    def __init__(
        self,
        redis_url: str,
        default_limit: int = 100,
        window_seconds: int = 60
    ):
        self.redis = redis.from_url(redis_url)
        self.default_limit = default_limit
        self.window_seconds = window_seconds

    async def check_rate_limit(
        self,
        key: str,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Check rate limit for key"""
        current_limit = limit or self.default_limit
        now = time.time()
        window_start = now - self.window_seconds
        
        pipe = self.redis.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Count requests in window
        pipe.zcard(key)
        
        # Add new request
        pipe.zadd(key, {str(now): now})
        
        # Set expiry on key
        pipe.expire(key, self.window_seconds)
        
        # Execute pipeline
        _, request_count, *_ = pipe.execute()
        
        remaining = max(0, current_limit - request_count)
        reset_time = int(window_start + self.window_seconds)
        
        return {
            "limit": current_limit,
            "remaining": remaining,
            "reset": reset_time,
            "allowed": request_count < current_limit
        }

    def rate_limit(
        self,
        limit: Optional[int] = None,
        key_func: Optional[callable] = None
    ):
        """Rate limiting decorator"""
        def decorator(func):
            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                # Get rate limit key
                if key_func:
                    rate_key = key_func(request)
                else:
                    rate_key = f"ratelimit:{request.client.host}"
                
                # Check rate limit
                rate_info = await self.check_rate_limit(rate_key, limit)
                
                # Set rate limit headers
                request.state.rate_limit = rate_info
                
                if not rate_info["allowed"]:
                    raise HTTPException(
                        status_code=429,
                        detail="Rate limit exceeded"
                    )
                    
                return await func(request, *args, **kwargs)
                
            return wrapper
        return decorator

    async def cleanup(self):
        """Clean up Redis connection"""
        self.redis.close() 
from typing import Optional, Dict, Any
import re
import logging
from datetime import datetime, timedelta
import jwt

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    pass

class Validator:
    @staticmethod
    def validate_prompt(prompt: str, max_length: int = 1000) -> str:
        """Validate and clean prompt text"""
        if not prompt or not isinstance(prompt, str):
            raise ValidationError("Prompt must be non-empty string")
            
        # Remove excessive whitespace
        prompt = " ".join(prompt.split())
        
        if len(prompt) > max_length:
            raise ValidationError(f"Prompt exceeds maximum length of {max_length}")
            
        # Basic content safety check
        unsafe_patterns = [
            r"(?i)(nsfw|porn|xxx)",
            r"(?i)(violence|gore|blood)",
            r"(?i)(hate|racist|discrimination)"
        ]
        
        for pattern in unsafe_patterns:
            if re.search(pattern, prompt):
                raise ValidationError("Prompt contains unsafe content")
                
        return prompt

    @staticmethod
    def validate_token(
        token: str,
        secret: str,
        algorithms: list = ["HS256"]
    ) -> Dict[str, Any]:
        """Validate JWT token"""
        try:
            payload = jwt.decode(token, secret, algorithms=algorithms)
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                raise ValidationError("Token has expired")
                
            return payload
            
        except jwt.InvalidTokenError as e:
            raise ValidationError(f"Invalid token: {str(e)}")

    @staticmethod
    def validate_rate_limit(
        key: str,
        redis_client,
        max_requests: int,
        window_seconds: int = 60
    ) -> bool:
        """Check rate limit for key"""
        try:
            pipe = redis_client.pipeline()
            now = datetime.utcnow().timestamp()
            window_start = now - window_seconds
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count requests in window
            pipe.zcard(key)
            
            # Add new request
            pipe.zadd(key, {str(now): now})
            
            # Set expiry on key
            pipe.expire(key, window_seconds)
            
            _, request_count, *_ = pipe.execute()
            
            return request_count <= max_requests
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            return False 
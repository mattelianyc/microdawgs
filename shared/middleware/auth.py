from typing import Optional, Dict, Any
import jwt
from datetime import datetime, timedelta
import logging
from functools import wraps
from fastapi import Request, HTTPException
from ..utils.error_handling import AuthenticationError

logger = logging.getLogger(__name__)

class JWTAuth:
    """JWT Authentication middleware"""
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        token_expiry: int = 24  # hours
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expiry = token_expiry

    def create_token(
        self,
        user_id: str,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create JWT token"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=self.token_expiry),
            "iat": datetime.utcnow()
        }
        
        if additional_claims:
            payload.update(additional_claims)
            
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")

    def requires_auth(self, roles: Optional[list] = None):
        """Authentication decorator"""
        def decorator(func):
            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                token = request.headers.get("Authorization")
                
                if not token or not token.startswith("Bearer "):
                    raise HTTPException(
                        status_code=401,
                        detail="Missing or invalid authorization header"
                    )
                
                try:
                    token_data = await self.verify_token(token.split(" ")[1])
                    
                    # Check roles if specified
                    if roles and "role" in token_data:
                        if token_data["role"] not in roles:
                            raise HTTPException(
                                status_code=403,
                                detail="Insufficient permissions"
                            )
                            
                    request.state.user = token_data
                    return await func(request, *args, **kwargs)
                    
                except AuthenticationError as e:
                    raise HTTPException(
                        status_code=401,
                        detail=str(e)
                    )
                    
            return wrapper
        return decorator 
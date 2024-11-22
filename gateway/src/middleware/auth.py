from fastapi import Request, HTTPException
from shared.middleware.auth import JWTAuth
from ..config import Settings
import logging

logger = logging.getLogger(__name__)

class GatewayAuth(JWTAuth):
    """Gateway-specific authentication middleware"""
    def __init__(self):
        settings = Settings()
        super().__init__(
            secret_key=settings.jwt_secret
        )

    async def authenticate_service(self, request: Request):
        """Authenticate service-to-service communication"""
        service_token = request.headers.get("X-Service-Token")
        
        if not service_token:
            raise HTTPException(
                status_code=401,
                detail="Missing service token"
            )
            
        try:
            # Verify service token
            token_data = await self.verify_token(service_token)
            
            if token_data.get("service_type") != "internal":
                raise HTTPException(
                    status_code=403,
                    detail="Invalid service token"
                )
                
            request.state.service = token_data.get("service_name")
            
        except Exception as e:
            logger.error(f"Service authentication failed: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Invalid service token"
            ) 
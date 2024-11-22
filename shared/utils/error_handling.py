from typing import Dict, Any, Optional
import traceback
import logging
import sys
from functools import wraps

logger = logging.getLogger(__name__)

class BaseError(Exception):
    """Base error class with status code and error details"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}

class ValidationError(BaseError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )

class AuthenticationError(BaseError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )

def error_handler(func):
    """Decorator for consistent error handling"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except BaseError as e:
            logger.error(f"{e.error_code}: {e.message}", extra=e.details)
            return {
                "error": True,
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details,
                "status_code": e.status_code
            }
        except Exception as e:
            logger.exception("Unexpected error occurred")
            return {
                "error": True,
                "message": "An unexpected error occurred",
                "error_code": "INTERNAL_ERROR",
                "details": {"traceback": traceback.format_exc()},
                "status_code": 500
            }
    return wrapper

def setup_error_handling():
    """Configure global error handling"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        logger.error(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    sys.excepthook = handle_exception 
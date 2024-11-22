from typing import Any, Dict, List, Optional
from datetime import datetime
import json

class ResponseFormatter:
    @staticmethod
    def success_response(
        data: Any,
        message: str = "Success",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format successful response"""
        response = {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if metadata:
            response["metadata"] = metadata
            
        return response

    @staticmethod
    def error_response(
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format error response"""
        response = {
            "success": False,
            "message": message,
            "error_code": error_code,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if details:
            response["details"] = details
            
        return response

    @staticmethod
    def paginated_response(
        data: List[Any],
        page: int,
        page_size: int,
        total: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format paginated response"""
        total_pages = (total + page_size - 1) // page_size
        
        response = {
            "success": True,
            "data": data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if metadata:
            response["metadata"] = metadata
            
        return response

    @staticmethod
    def stream_response(
        data: Any,
        event_type: str = "update",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format Server-Sent Events (SSE) response"""
        response = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if metadata:
            response["metadata"] = metadata
            
        return f"event: {event_type}\ndata: {json.dumps(response)}\n\n" 
from fastapi import HTTPException
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def validate_prompt(
    prompt: str,
    min_length: int = 3,
    max_length: int = 1000
) -> str:
    """Validate and clean generation prompt"""
    try:
        # Check length
        if len(prompt) < min_length:
            raise HTTPException(
                status_code=400,
                detail=f"Prompt too short. Minimum length: {min_length}"
            )
            
        if len(prompt) > max_length:
            raise HTTPException(
                status_code=400,
                detail=f"Prompt too long. Maximum length: {max_length}"
            )
            
        # Clean whitespace
        prompt = " ".join(prompt.split())
        
        # Check for unsafe content
        unsafe_patterns = [
            r"(?i)(nsfw|porn|xxx)",
            r"(?i)(violence|gore|blood)",
            r"(?i)(hate|racist|discrimination)"
        ]
        
        for pattern in unsafe_patterns:
            if re.search(pattern, prompt):
                raise HTTPException(
                    status_code=400,
                    detail="Prompt contains unsafe content"
                )
                
        return prompt
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prompt validation failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Invalid prompt"
        ) 
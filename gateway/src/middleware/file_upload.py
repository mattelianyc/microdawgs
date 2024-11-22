from fastapi import UploadFile, HTTPException
from PIL import Image
import io
import aiofiles
import os
import logging
from typing import Optional
from ..config import Settings

logger = logging.getLogger(__name__)

class FileUploadHandler:
    """Handle file uploads and validation"""
    def __init__(self):
        self.settings = Settings()
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_types = ["image/jpeg", "image/png", "image/webp"]
        self.upload_dir = "/tmp/uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    async def validate_file(
        self,
        file: UploadFile,
        max_size: Optional[int] = None
    ) -> bool:
        """Validate file upload"""
        if not file.content_type in self.allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}"
            )
            
        size_limit = max_size or self.max_file_size
        
        # Check file size
        file_size = 0
        chunk_size = 8192
        
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            file_size += len(chunk)
            if file_size > size_limit:
                raise HTTPException(
                    status_code=400,
                    detail="File too large"
                )
                
            await file.seek(0)
            
        return True

    async def save_file(
        self,
        file: UploadFile,
        filename: Optional[str] = None
    ) -> str:
        """Save uploaded file"""
        if not filename:
            filename = file.filename
            
        file_path = os.path.join(self.upload_dir, filename)
        
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                while chunk := await file.read(8192):
                    await f.write(chunk)
                    
            return file_path
            
        except Exception as e:
            logger.error(f"File save failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to save file"
            )

    async def process_image(self, file: UploadFile) -> Image.Image:
        """Process uploaded image"""
        try:
            # Validate file
            await self.validate_file(file)
            
            # Read image
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))
            
            # Convert to RGB if needed
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGB")
                
            return image
            
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Invalid image file"
            )

    async def cleanup_file(self, file_path: str):
        """Clean up uploaded file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"File cleanup failed: {str(e)}") 
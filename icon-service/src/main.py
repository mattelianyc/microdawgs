from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from starlette.concurrency import run_in_threadpool
from .services.stable_diffusion import StableDiffusionService
from .services.fine_tuning import FineTuningService, training_status
from .services.state import generation_state

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
sd_service = StableDiffusionService()
fine_tuning_service = FineTuningService()

@app.post("/generate")
async def generate_icon(
    prompt: str = Form(...),
    num_steps: int = Form(20),
    guidance_scale: float = Form(7.5)
):
    logger.info(f"Received request to generate icon with prompt: {prompt}")
    try:
        # Reset progress
        generation_state.reset()

        # Run generation in a separate thread
        image_bytes = await run_in_threadpool(
            sd_service.generate_icon,
            prompt=prompt,
            num_steps=min(num_steps, 50),
            guidance_scale=min(guidance_scale, 20.0)
        )
        
        return Response(content=image_bytes, media_type="image/png")

    except Exception as e:
        logger.error(f"Error during icon generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generate/progress")
async def get_generation_progress():
    """Get the current generation progress"""
    return JSONResponse(content=generation_state.get_progress())

@app.get("/health")
async def health_check():
    logger.info("Health check requested.")
    try:
        # Verify services are initialized
        if not sd_service or not fine_tuning_service:
            return {"status": "unhealthy", "detail": "Services not initialized"}
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "detail": str(e)}

@app.post("/train")
async def train_model(
    file: UploadFile = File(...),
    num_epochs: int = Form(20)
):
    try:
        # Update training status
        training_status.update("starting")
        
        # Validate file type
        if not file.filename.endswith('.zip'):
            raise HTTPException(
                status_code=400,
                detail="Please upload a ZIP file containing PNG images"
            )
            
        # Limit file size for CPU processing
        file_size = 0
        file_bytes = bytearray()
        
        # Read file in chunks
        chunk_size = 1024 * 1024  # 1MB chunks
        while chunk := await file.read(chunk_size):
            file_size += len(chunk)
            if file_size > 100 * 1024 * 1024:  # 100MB limit
                training_status.update("error", error="File too large")
                raise HTTPException(
                    status_code=400,
                    detail="File too large. Please limit to 100MB of images."
                )
            file_bytes.extend(chunk)
        
        # Process training images
        training_status.update("processing_images")
        processed_images = await fine_tuning_service.process_training_images(bytes(file_bytes))
        
        if len(processed_images) < 5:
            training_status.update("error", error="Insufficient training images")
            raise HTTPException(
                status_code=400,
                detail="Please provide at least 5 training images"
            )
        
        # Fine-tune the model
        training_status.update("training", progress=0)
        result = await fine_tuning_service.fine_tune_model(
            processed_images,
            num_epochs=min(num_epochs, 50)  # Limit max epochs
        )
        
        training_status.update("completed", progress=100)
        return result
        
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        training_status.update("error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
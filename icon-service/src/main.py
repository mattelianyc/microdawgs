from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import logging
from .services.stable_diffusion import StableDiffusionService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sd_service = StableDiffusionService()

@app.post("/generate")
async def generate_icon(
    prompt: str = Form(...),
    num_steps: int = Form(20),
    guidance_scale: float = Form(7.5)
):
    logger.info("Received request to generate icon with prompt: %s, num_steps: %d, guidance_scale: %.2f", prompt, num_steps, guidance_scale)
    try:
        # Generate icon
        logger.info("Starting icon generation...")
        image_bytes = await sd_service.generate_icon(
            prompt=prompt,
            num_steps=num_steps,
            guidance_scale=guidance_scale
        )
        logger.info("Icon generation successful.")
        return Response(content=image_bytes, media_type="image/png")

    except Exception as e:
        logger.error("Error during icon generation: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    logger.info("Health check requested.")
    return {"status": "healthy"} 
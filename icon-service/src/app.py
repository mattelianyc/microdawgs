from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .config import Settings
from .controllers import icon_generator, layout_manager
from shared.middleware.auth import JWTAuth
from shared.middleware.telemetry import TelemetryMiddleware
import logging

# Load settings
settings = Settings()

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Icon Generation Service",
    description="Service for generating icon images",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize middleware
auth = JWTAuth(secret_key=settings.jwt_secret)
telemetry = TelemetryMiddleware(
    service_name="icon-service",
    enable_tracing=settings.enable_tracing,
    enable_metrics=settings.enable_metrics
)

# Add routes
app.include_router(
    icon_generator.router,
    prefix="/generate",
    tags=["generation"]
)
app.include_router(
    layout_manager.router,
    prefix="/layout",
    tags=["layout"]
)

@app.middleware("http")
async def middleware(request: Request, call_next):
    """Global middleware for all requests"""
    # Add request ID
    request.state.request_id = str(uuid.uuid4())
    
    # Start telemetry
    with telemetry.tracer.start_as_current_span("request") as span:
        span.set_attribute("request_id", request.state.request_id)
        response = await call_next(request)
        
    return response

@app.on_event("startup")
async def startup():
    """Startup event handler"""
    logger.info("Starting icon service")
    # Initialize models and services
    await icon_generator.initialize_models()

@app.on_event("shutdown")
async def shutdown():
    """Shutdown event handler"""
    logger.info("Shutting down icon service")
    # Cleanup resources
    await icon_generator.cleanup() 
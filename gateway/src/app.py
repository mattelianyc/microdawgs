from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .config import Settings
from .routes import health, api_routes, admin_routes
from shared.middleware.auth import JWTAuth
from shared.middleware.rate_limiting import RateLimiter
from shared.middleware.telemetry import TelemetryMiddleware
import logging
import uuid

# Load settings
settings = Settings()

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Image Generation Gateway",
    description="API Gateway for Image Generation Services",
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
rate_limiter = RateLimiter(
    redis_url=settings.redis_url,
    default_limit=settings.rate_limit
)
telemetry = TelemetryMiddleware(
    service_name="gateway",
    enable_tracing=settings.enable_tracing,
    enable_metrics=settings.enable_metrics
)

# Add routes
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(
    api_routes.router,
    prefix="/api/v1",
    tags=["api"]
)
app.include_router(
    admin_routes.router,
    prefix="/admin",
    tags=["admin"]
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
    logger.info("Starting gateway service")
    # Initialize services and connections

@app.on_event("shutdown")
async def shutdown():
    """Shutdown event handler"""
    logger.info("Shutting down gateway service")
    # Cleanup resources 
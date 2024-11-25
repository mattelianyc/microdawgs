from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.config import Settings
from src.routes import health, api_routes, admin_routes
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
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Add routes
app.include_router(
    api_routes.router,
    prefix="/api/v1",
    tags=["api"]
)

app.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

app.include_router(
    admin_routes.router,
    prefix="/admin",
    tags=["admin"]
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Request completed: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise

@app.on_event("startup")
async def startup():
    """Startup event handler"""
    logger.info("Starting gateway service")

@app.on_event("shutdown")
async def shutdown():
    """Shutdown event handler"""
    logger.info("Shutting down gateway service")
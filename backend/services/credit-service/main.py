"""
Cleo Credit Service

Credit score monitoring, credit builder card, and credit coaching.
Helps users build and improve their credit score.
"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add shared module to path
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.append(str(shared_path))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import monitoring, builder, coaching, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application"""
    print("🚀 Credit Service starting up...")
    yield
    print("👋 Credit Service shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Cleo Credit Service",
    description="Credit score monitoring, credit builder, and coaching",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    monitoring.router,
    prefix="/api/v1/credit/monitoring",
    tags=["Credit Monitoring"]
)
app.include_router(
    builder.router,
    prefix="/api/v1/credit/builder",
    tags=["Credit Builder"]
)
app.include_router(
    coaching.router,
    prefix="/api/v1/credit/coaching",
    tags=["Credit Coaching"]
)
app.include_router(
    reports.router,
    prefix="/api/v1/credit/reports",
    tags=["Credit Reports"]
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "credit-service",
        "version": "0.1.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Cleo Credit Service",
        "description": "Build and monitor your credit score",
        "version": "0.1.0",
        "docs": "/docs"
    }

"""
Cleo Advance Service

Handles cash advances with underwriting, eligibility checks, and repayment management.
Provides users with instant cash advances ($20-$250) based on income patterns.
"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add shared module to path
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.append(str(shared_path))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import eligibility, advances, repayments


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application"""
    print("🚀 Advance Service starting up...")
    yield
    print("👋 Advance Service shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Cleo Advance Service",
    description="Cash advances with underwriting and repayment management",
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
    eligibility.router,
    prefix="/api/v1/advances/eligibility",
    tags=["Eligibility"]
)
app.include_router(
    advances.router,
    prefix="/api/v1/advances",
    tags=["Advances"]
)
app.include_router(
    repayments.router,
    prefix="/api/v1/advances/repayments",
    tags=["Repayments"]
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "advance-service",
        "version": "0.1.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Cleo Advance Service",
        "description": "Cash advances with smart underwriting",
        "version": "0.1.0",
        "docs": "/docs"
    }

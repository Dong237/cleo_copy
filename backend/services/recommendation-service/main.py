"""
Cleo Recommendation Service

ML-powered personalized recommendations for spending, savings, and financial wellness.
Uses behavioral analysis and predictive models to provide actionable insights.
"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add shared module to path
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.append(str(shared_path))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import spending, savings, wellness, insights


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application"""
    print("🚀 Recommendation Service starting up...")
    # In production, load ML models here
    yield
    print("👋 Recommendation Service shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Cleo Recommendation Service",
    description="ML-powered personalized financial recommendations",
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
    spending.router,
    prefix="/api/v1/recommendations/spending",
    tags=["Spending Recommendations"]
)
app.include_router(
    savings.router,
    prefix="/api/v1/recommendations/savings",
    tags=["Savings Recommendations"]
)
app.include_router(
    wellness.router,
    prefix="/api/v1/recommendations/wellness",
    tags=["Financial Wellness"]
)
app.include_router(
    insights.router,
    prefix="/api/v1/recommendations/insights",
    tags=["Insights"]
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "recommendation-service",
        "version": "0.1.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Cleo Recommendation Service",
        "description": "ML-powered personalized financial recommendations",
        "version": "0.1.0",
        "docs": "/docs"
    }

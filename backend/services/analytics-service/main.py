"""
Cleo Analytics Service

Data aggregation, user behavior analytics, and business intelligence.
Provides insights across all services and user activities.
"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add shared module to path
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.append(str(shared_path))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import user_analytics, financial_analytics, business_intelligence, exports


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application"""
    print("🚀 Analytics Service starting up...")
    yield
    print("👋 Analytics Service shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Cleo Analytics Service",
    description="Data aggregation, analytics, and business intelligence",
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
    user_analytics.router,
    prefix="/api/v1/analytics/users",
    tags=["User Analytics"]
)
app.include_router(
    financial_analytics.router,
    prefix="/api/v1/analytics/financial",
    tags=["Financial Analytics"]
)
app.include_router(
    business_intelligence.router,
    prefix="/api/v1/analytics/business",
    tags=["Business Intelligence"]
)
app.include_router(
    exports.router,
    prefix="/api/v1/analytics/exports",
    tags=["Data Exports"]
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "analytics-service",
        "version": "0.1.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Cleo Analytics Service",
        "description": "Comprehensive data analytics and business intelligence",
        "version": "0.1.0",
        "docs": "/docs"
    }

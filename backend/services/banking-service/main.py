"""
Banking Service - Plaid integration, account management, transaction sync
"""
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

import sys
import os

# Add parent directory to path to import shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from shared.config import settings
from shared.database import init_db, close_db
from shared.exceptions import CleoException

from app.routes import accounts, transactions, plaid


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events"""
    # Startup
    print("🚀 Starting Banking Service...")
    await init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 Shutting down Banking Service...")
    await close_db()
    print("✅ Connections closed")


# Create FastAPI app
app = FastAPI(
    title="Cleo Banking Service",
    description="Plaid integration, account management, and transaction sync",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(CleoException)
async def cleo_exception_handler(request: Request, exc: CleoException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "banking-service",
        "version": "0.1.0"
    }


# Include routers
app.include_router(plaid.router, prefix="/api/v1/plaid", tags=["Plaid"])
app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["Accounts"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=settings.DEBUG
    )

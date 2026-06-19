"""API module initialization"""
from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.health import router as health_router

# Main API router
api_router = APIRouter(prefix="/api/v1")

# Include sub-routers
api_router.include_router(auth_router)
api_router.include_router(health_router)

__all__ = ["api_router"]

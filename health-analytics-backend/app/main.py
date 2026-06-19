"""
Health Analytics System - Main Application
Intelligent Health Evaluation Platform with AI Integration
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.api import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    print("🚀 Starting Health Analytics System...")
    await init_db()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    await close_db()
    print("✅ Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
## 🏥 Интеллектуальная система аналитической оценки здоровья

AI-powered health analytics platform that combines physical metrics 
with intelligent symptom interpretation.

### Features:
- 📊 BMI calculation and ideal weight analysis
- 🤖 AI-powered symptom interpretation (Groq API)
- 📈 Health Score (0-100) calculation
- 🗓 Personalized weekly health plans
- 📚 Analysis history and progress tracking
- 🌐 Multilingual support (Kazakh, Russian)

### Important Notes:
⚠️ This system does NOT provide medical diagnoses.
All recommendations are for informational purposes only.
Always consult a healthcare professional for medical advice.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with clear messages"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )


# Include API routes
app.include_router(api_router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "auth": {
                "register": "POST /api/v1/auth/register",
                "login": "POST /api/v1/auth/login",
                "profile": "GET /api/v1/auth/profile"
            },
            "health": {
                "analyze": "POST /api/v1/health/analyze",
                "history": "GET /api/v1/health/history",
                "progress": "GET /api/v1/health/progress"
            }
        }
    }


# Health check endpoint
@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Application health check
    """
    return {
        "status": "healthy",
        "database": "connected",
        "ai_service": "groq"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

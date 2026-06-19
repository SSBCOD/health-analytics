"""Schemas module initialization"""
from app.schemas.schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserProfile,
    UserProfileUpdate,
    HealthAnalysisRequest,
    HealthAnalysisResponse,
    HealthAnalysisSummary,
    HealthHistory,
    ProgressComparison,
    IdealState,
    AIAnalysisResult,
    ErrorResponse
)

__all__ = [
    "UserRegister",
    "UserLogin",
    "TokenResponse",
    "UserProfile",
    "UserProfileUpdate",
    "HealthAnalysisRequest",
    "HealthAnalysisResponse",
    "HealthAnalysisSummary",
    "HealthHistory",
    "ProgressComparison",
    "IdealState",
    "AIAnalysisResult",
    "ErrorResponse"
]

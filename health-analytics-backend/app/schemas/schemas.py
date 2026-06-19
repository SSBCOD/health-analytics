"""
Pydantic Schemas for API validation and serialization
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models import Gender, RiskLevel, UrgencyLevel, Language


# ============== AUTH SCHEMAS ==============

class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    full_name: Optional[str] = Field(None, max_length=255)
    preferred_language: Language = Language.KZ


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    full_name: Optional[str]


class UserProfile(BaseModel):
    """User profile data"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    full_name: Optional[str]
    age: Optional[int]
    gender: Optional[Gender]
    height_cm: Optional[float]
    preferred_language: Language
    created_at: datetime


class UserProfileUpdate(BaseModel):
    """Update user profile"""
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=120)
    gender: Optional[Gender] = None
    height_cm: Optional[float] = Field(None, ge=50, le=300)
    preferred_language: Optional[Language] = None


# ============== HEALTH ANALYSIS SCHEMAS ==============

class HealthAnalysisRequest(BaseModel):
    """Request for health analysis"""
    age: int = Field(..., ge=1, le=120, description="Возраст в годах")
    gender: Gender = Field(..., description="Пол (male/female)")
    height_cm: float = Field(..., ge=50, le=300, description="Рост в см")
    weight_kg: float = Field(..., ge=10, le=500, description="Вес в кг")
    symptoms_text: str = Field(
        ..., 
        min_length=10, 
        max_length=5000,
        description="Описание симптомов и состояния"
    )
    language: Language = Field(
        default=Language.KZ,
        description="Язык ответа (kz/ru)"
    )


class IdealState(BaseModel):
    """Ideal health state description"""
    optimal_weight_range: str
    difference: str
    explanation: str


class HealthAnalysisResponse(BaseModel):
    """Complete health analysis response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    
    # Input echo
    age: int
    gender: Gender
    height_cm: float
    weight_kg: float
    language: Language
    
    # Calculated metrics
    bmi: float
    bmi_category: str
    ideal_weight_min: float
    ideal_weight_max: float
    weight_difference: float
    
    # AI Analysis
    health_score: int = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    urgency_level: UrgencyLevel
    
    # Interpretations
    interpretation: str
    ideal_state: IdealState
    weekly_plan: Optional[List[str]]
    doctor_recommendation: Optional[str]
    positive_feedback: str
    disclaimer: str
    
    created_at: datetime


class HealthAnalysisSummary(BaseModel):
    """Summary for history list"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    health_score: int
    bmi: float
    risk_level: RiskLevel
    urgency_level: UrgencyLevel
    weight_kg: float
    created_at: datetime


class HealthHistory(BaseModel):
    """User's health analysis history"""
    total: int
    analyses: List[HealthAnalysisSummary]


class ProgressComparison(BaseModel):
    """Compare two analyses for progress"""
    previous: HealthAnalysisSummary
    current: HealthAnalysisSummary
    
    # Changes
    health_score_change: int
    bmi_change: float
    weight_change: float
    
    # Progress interpretation
    progress_summary: str
    is_improving: bool


# ============== AI SCHEMAS ==============

class AIAnalysisResult(BaseModel):
    """Schema for AI response validation"""
    language: Language
    bmi: float
    health_score: int = Field(..., ge=0, le=100)
    ideal_state: IdealState
    interpretation: str
    risk_level: RiskLevel
    urgency_level: UrgencyLevel
    weekly_plan: Optional[List[str]] = None
    doctor_recommendation: Optional[str] = None
    positive_feedback: str
    disclaimer: str


# ============== ERROR SCHEMAS ==============

class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    error_code: Optional[str] = None

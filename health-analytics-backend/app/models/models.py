"""
Database Models
User and HealthAnalysis entities
"""
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, 
    ForeignKey, Enum, JSON
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
import enum

from app.core.database import Base


class Gender(str, enum.Enum):
    """Gender enumeration"""
    MALE = "male"
    FEMALE = "female"


class RiskLevel(str, enum.Enum):
    """Health risk level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UrgencyLevel(str, enum.Enum):
    """Action urgency level"""
    NO_ACTION = "no_action"
    VISIT_DOCTOR = "visit_doctor"
    URGENT = "urgent"


class Language(str, enum.Enum):
    """Supported languages"""
    KZ = "kz"  # Казахский
    RU = "ru"  # Русский


class User(Base):
    """User model for authentication and profile"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Profile data (optional, can be pre-filled in analysis)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[Gender]] = mapped_column(Enum(Gender), nullable=True)
    height_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Preferences
    preferred_language: Mapped[Language] = mapped_column(
        Enum(Language), 
        default=Language.KZ,
        nullable=False
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    health_analyses: Mapped[List["HealthAnalysis"]] = relationship(
        "HealthAnalysis",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class HealthAnalysis(Base):
    """Health analysis record with AI evaluation results"""
    __tablename__ = "health_analyses"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Input data
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=False)
    height_cm: Mapped[float] = mapped_column(Float, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    symptoms_text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[Language] = mapped_column(Enum(Language), default=Language.KZ)
    
    # Calculated metrics (физические вычисления)
    bmi: Mapped[float] = mapped_column(Float, nullable=False)
    bmi_category: Mapped[str] = mapped_column(String(50), nullable=False)
    ideal_weight_min: Mapped[float] = mapped_column(Float, nullable=False)
    ideal_weight_max: Mapped[float] = mapped_column(Float, nullable=False)
    weight_difference: Mapped[float] = mapped_column(Float, nullable=False)  # + excess, - deficit
    
    # AI Analysis results
    health_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-100
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), nullable=False)
    urgency_level: Mapped[UrgencyLevel] = mapped_column(Enum(UrgencyLevel), nullable=False)
    
    # AI interpretations (JSON for flexibility)
    interpretation: Mapped[str] = mapped_column(Text, nullable=False)
    ideal_state_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    weekly_plan: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # 7-day plan
    doctor_recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    positive_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    disclaimer: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Full AI response (for debugging)
    raw_ai_response: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="health_analyses")

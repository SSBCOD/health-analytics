"""
Health Analysis API Routes
Core health evaluation and history management
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, get_current_user_id
from app.models import User, HealthAnalysis, Language
from app.schemas import (
    HealthAnalysisRequest,
    HealthAnalysisResponse,
    HealthAnalysisSummary,
    HealthHistory,
    ProgressComparison,
    IdealState,
    ErrorResponse
)
from app.services import (
    calculate_health_metrics,
    analyze_health_with_ai,
    generate_progress_summary
)

router = APIRouter(prefix="/health", tags=["Health Analysis"])


@router.post(
    "/analyze",
    response_model=HealthAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        500: {"model": ErrorResponse, "description": "AI analysis failed"}
    }
)
async def analyze_health(
    data: HealthAnalysisRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform comprehensive health analysis
    
    Combines physical calculations with AI-powered symptom interpretation
    
    Steps:
    1. Calculate BMI and physical metrics
    2. Send data to AI for symptom analysis
    3. Generate health score and recommendations
    4. Store analysis in history
    """
    # Step 1: Physical calculations
    bmi_result = calculate_health_metrics(
        weight_kg=data.weight_kg,
        height_cm=data.height_cm,
        gender=data.gender,
        language=data.language
    )
    
    # Step 2: AI Analysis
    try:
        ai_result = await analyze_health_with_ai(
            age=data.age,
            gender=data.gender,
            height_cm=data.height_cm,
            weight_kg=data.weight_kg,
            symptoms=data.symptoms_text,
            bmi_result=bmi_result,
            language=data.language
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}"
        )
    
    # Step 3: Create database record
    analysis = HealthAnalysis(
        user_id=user_id,
        age=data.age,
        gender=data.gender,
        height_cm=data.height_cm,
        weight_kg=data.weight_kg,
        symptoms_text=data.symptoms_text,
        language=data.language,
        
        # Physical metrics
        bmi=bmi_result.bmi,
        bmi_category=bmi_result.category,
        ideal_weight_min=bmi_result.ideal_weight_min,
        ideal_weight_max=bmi_result.ideal_weight_max,
        weight_difference=bmi_result.weight_difference,
        
        # AI results
        health_score=ai_result.health_score,
        risk_level=ai_result.risk_level,
        urgency_level=ai_result.urgency_level,
        interpretation=ai_result.interpretation,
        ideal_state_explanation=ai_result.ideal_state.explanation,
        weekly_plan=ai_result.weekly_plan,
        doctor_recommendation=ai_result.doctor_recommendation,
        positive_feedback=ai_result.positive_feedback,
        disclaimer=ai_result.disclaimer,
        
        # Raw response for debugging
        raw_ai_response=ai_result.model_dump()
    )
    
    db.add(analysis)
    await db.flush()
    await db.refresh(analysis)
    
    # Step 4: Build response
    return HealthAnalysisResponse(
        id=analysis.id,
        age=analysis.age,
        gender=analysis.gender,
        height_cm=analysis.height_cm,
        weight_kg=analysis.weight_kg,
        language=analysis.language,
        bmi=analysis.bmi,
        bmi_category=analysis.bmi_category,
        ideal_weight_min=analysis.ideal_weight_min,
        ideal_weight_max=analysis.ideal_weight_max,
        weight_difference=analysis.weight_difference,
        health_score=analysis.health_score,
        risk_level=analysis.risk_level,
        urgency_level=analysis.urgency_level,
        interpretation=analysis.interpretation,
        ideal_state=IdealState(
            optimal_weight_range=ai_result.ideal_state.optimal_weight_range,
            difference=ai_result.ideal_state.difference,
            explanation=analysis.ideal_state_explanation
        ),
        weekly_plan=analysis.weekly_plan,
        doctor_recommendation=analysis.doctor_recommendation,
        positive_feedback=analysis.positive_feedback,
        disclaimer=analysis.disclaimer,
        created_at=analysis.created_at
    )


@router.get(
    "/history",
    response_model=HealthHistory,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
async def get_health_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's health analysis history
    
    Returns paginated list of past analyses sorted by date (newest first)
    """
    # Count total
    count_result = await db.execute(
        select(HealthAnalysis).where(HealthAnalysis.user_id == user_id)
    )
    total = len(count_result.scalars().all())
    
    # Fetch analyses
    result = await db.execute(
        select(HealthAnalysis)
        .where(HealthAnalysis.user_id == user_id)
        .order_by(desc(HealthAnalysis.created_at))
        .offset(offset)
        .limit(limit)
    )
    analyses = result.scalars().all()
    
    summaries = [
        HealthAnalysisSummary(
            id=a.id,
            health_score=a.health_score,
            bmi=a.bmi,
            risk_level=a.risk_level,
            urgency_level=a.urgency_level,
            weight_kg=a.weight_kg,
            created_at=a.created_at
        )
        for a in analyses
    ]
    
    return HealthHistory(total=total, analyses=summaries)


@router.get(
    "/analysis/{analysis_id}",
    response_model=HealthAnalysisResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Analysis not found"}
    }
)
async def get_analysis(
    analysis_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific health analysis by ID
    """
    result = await db.execute(
        select(HealthAnalysis)
        .where(
            HealthAnalysis.id == analysis_id,
            HealthAnalysis.user_id == user_id
        )
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    # Reconstruct ideal_state from stored data
    raw_response = analysis.raw_ai_response or {}
    ideal_state_data = raw_response.get("ideal_state", {})
    
    return HealthAnalysisResponse(
        id=analysis.id,
        age=analysis.age,
        gender=analysis.gender,
        height_cm=analysis.height_cm,
        weight_kg=analysis.weight_kg,
        language=analysis.language,
        bmi=analysis.bmi,
        bmi_category=analysis.bmi_category,
        ideal_weight_min=analysis.ideal_weight_min,
        ideal_weight_max=analysis.ideal_weight_max,
        weight_difference=analysis.weight_difference,
        health_score=analysis.health_score,
        risk_level=analysis.risk_level,
        urgency_level=analysis.urgency_level,
        interpretation=analysis.interpretation,
        ideal_state=IdealState(
            optimal_weight_range=ideal_state_data.get(
                "optimal_weight_range",
                f"{analysis.ideal_weight_min}-{analysis.ideal_weight_max} кг"
            ),
            difference=ideal_state_data.get("difference", ""),
            explanation=analysis.ideal_state_explanation
        ),
        weekly_plan=analysis.weekly_plan,
        doctor_recommendation=analysis.doctor_recommendation,
        positive_feedback=analysis.positive_feedback,
        disclaimer=analysis.disclaimer,
        created_at=analysis.created_at
    )


@router.get(
    "/progress",
    response_model=Optional[ProgressComparison],
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
async def get_progress(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare latest two analyses to show progress
    
    Returns None if user has less than 2 analyses
    """
    # Get user's preferred language
    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = user_result.scalar_one_or_none()
    language = user.preferred_language if user else Language.KZ
    
    # Get last 2 analyses
    result = await db.execute(
        select(HealthAnalysis)
        .where(HealthAnalysis.user_id == user_id)
        .order_by(desc(HealthAnalysis.created_at))
        .limit(2)
    )
    analyses = result.scalars().all()
    
    if len(analyses) < 2:
        return None
    
    current = analyses[0]
    previous = analyses[1]
    
    # Generate progress summary
    summary, is_improving = generate_progress_summary(
        prev_score=previous.health_score,
        curr_score=current.health_score,
        prev_bmi=previous.bmi,
        curr_bmi=current.bmi,
        language=language
    )
    
    return ProgressComparison(
        previous=HealthAnalysisSummary(
            id=previous.id,
            health_score=previous.health_score,
            bmi=previous.bmi,
            risk_level=previous.risk_level,
            urgency_level=previous.urgency_level,
            weight_kg=previous.weight_kg,
            created_at=previous.created_at
        ),
        current=HealthAnalysisSummary(
            id=current.id,
            health_score=current.health_score,
            bmi=current.bmi,
            risk_level=current.risk_level,
            urgency_level=current.urgency_level,
            weight_kg=current.weight_kg,
            created_at=current.created_at
        ),
        health_score_change=current.health_score - previous.health_score,
        bmi_change=round(current.bmi - previous.bmi, 1),
        weight_change=round(current.weight_kg - previous.weight_kg, 1),
        progress_summary=summary,
        is_improving=is_improving
    )


@router.delete(
    "/analysis/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Analysis not found"}
    }
)
async def delete_analysis(
    analysis_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a health analysis from history
    """
    result = await db.execute(
        select(HealthAnalysis)
        .where(
            HealthAnalysis.id == analysis_id,
            HealthAnalysis.user_id == user_id
        )
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    await db.delete(analysis)

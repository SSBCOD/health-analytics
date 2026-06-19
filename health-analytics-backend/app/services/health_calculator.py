"""
Health Metrics Calculator Service
Physical calculations for BMI, ideal weight, and health categories
"""
from dataclasses import dataclass
from typing import Tuple
from app.models import Gender, Language


@dataclass
class BMIResult:
    """BMI calculation result"""
    bmi: float
    category: str
    ideal_weight_min: float
    ideal_weight_max: float
    weight_difference: float  # + excess, - deficit
    

# BMI Categories with ranges
BMI_CATEGORIES = {
    "kz": {
        "severe_underweight": "Ауыр салмақ жетіспеушілігі",
        "underweight": "Салмақ жетіспеушілігі", 
        "normal": "Қалыпты салмақ",
        "overweight": "Артық салмақ",
        "obese_1": "Семіздік (1-дәреже)",
        "obese_2": "Семіздік (2-дәреже)",
        "obese_3": "Семіздік (3-дәреже)"
    },
    "ru": {
        "severe_underweight": "Выраженный дефицит массы тела",
        "underweight": "Недостаточная масса тела",
        "normal": "Нормальный вес",
        "overweight": "Избыточная масса тела",
        "obese_1": "Ожирение 1 степени",
        "obese_2": "Ожирение 2 степени",
        "obese_3": "Ожирение 3 степени"
    }
}


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """
    Calculate Body Mass Index
    
    Formula: BMI = weight(kg) / height(m)²
    """
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)


def get_bmi_category(bmi: float, language: Language) -> str:
    """
    Get BMI category based on WHO classification
    
    Categories:
    - < 16.0: Severe underweight
    - 16.0-18.4: Underweight
    - 18.5-24.9: Normal
    - 25.0-29.9: Overweight
    - 30.0-34.9: Obese Class I
    - 35.0-39.9: Obese Class II
    - ≥ 40.0: Obese Class III
    """
    lang = language.value
    categories = BMI_CATEGORIES[lang]
    
    if bmi < 16.0:
        return categories["severe_underweight"]
    elif bmi < 18.5:
        return categories["underweight"]
    elif bmi < 25.0:
        return categories["normal"]
    elif bmi < 30.0:
        return categories["overweight"]
    elif bmi < 35.0:
        return categories["obese_1"]
    elif bmi < 40.0:
        return categories["obese_2"]
    else:
        return categories["obese_3"]


def calculate_ideal_weight_range(height_cm: float, gender: Gender) -> Tuple[float, float]:
    """
    Calculate ideal weight range based on height and gender
    
    Uses BMI range 18.5-24.9 for normal weight
    Adjusts slightly for gender differences
    """
    height_m = height_cm / 100
    
    # Standard BMI range for normal weight
    bmi_min = 18.5
    bmi_max = 24.9
    
    # Slight adjustment for gender (men tend to have more muscle mass)
    if gender == Gender.MALE:
        bmi_min = 19.0
        bmi_max = 25.0
    
    weight_min = bmi_min * (height_m ** 2)
    weight_max = bmi_max * (height_m ** 2)
    
    return round(weight_min, 1), round(weight_max, 1)


def calculate_weight_difference(
    current_weight: float,
    ideal_min: float,
    ideal_max: float
) -> float:
    """
    Calculate difference from ideal weight range
    
    Returns:
        Positive: excess weight (kg above ideal max)
        Negative: deficit weight (kg below ideal min)
        Zero: within ideal range
    """
    if current_weight > ideal_max:
        return round(current_weight - ideal_max, 1)
    elif current_weight < ideal_min:
        return round(current_weight - ideal_min, 1)
    else:
        return 0.0


def calculate_health_metrics(
    weight_kg: float,
    height_cm: float,
    gender: Gender,
    language: Language
) -> BMIResult:
    """
    Complete health metrics calculation
    
    Performs all physical calculations:
    - BMI
    - BMI category
    - Ideal weight range
    - Weight difference from ideal
    """
    bmi = calculate_bmi(weight_kg, height_cm)
    category = get_bmi_category(bmi, language)
    ideal_min, ideal_max = calculate_ideal_weight_range(height_cm, gender)
    weight_diff = calculate_weight_difference(weight_kg, ideal_min, ideal_max)
    
    return BMIResult(
        bmi=bmi,
        category=category,
        ideal_weight_min=ideal_min,
        ideal_weight_max=ideal_max,
        weight_difference=weight_diff
    )


def estimate_base_health_score(bmi: float, age: int) -> int:
    """
    Estimate baseline health score from physical metrics only
    
    This provides a starting point that AI will adjust based on symptoms
    
    Returns: Score 0-100
    """
    score = 100
    
    # BMI impact (up to -40 points)
    if bmi < 16.0:
        score -= 40
    elif bmi < 18.5:
        score -= 20
    elif bmi < 25.0:
        score -= 0  # Normal
    elif bmi < 30.0:
        score -= 15
    elif bmi < 35.0:
        score -= 25
    elif bmi < 40.0:
        score -= 35
    else:
        score -= 40
    
    # Age factor (slight adjustment for extreme ages)
    if age < 18:
        score -= 5  # Children/teens need special attention
    elif age > 70:
        score -= 10  # Elderly more vulnerable
    
    return max(0, min(100, score))

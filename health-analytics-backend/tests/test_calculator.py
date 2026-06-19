"""
Tests for Health Calculator Service
"""
import pytest
from app.services.health_calculator import (
    calculate_bmi,
    get_bmi_category,
    calculate_ideal_weight_range,
    calculate_weight_difference,
    calculate_health_metrics,
    estimate_base_health_score
)
from app.models import Gender, Language


class TestBMICalculation:
    """Test BMI calculation functions"""
    
    def test_normal_bmi(self):
        """Test BMI calculation for normal weight"""
        # 70kg, 175cm -> BMI ≈ 22.9
        bmi = calculate_bmi(70, 175)
        assert 22.0 <= bmi <= 23.5
    
    def test_underweight_bmi(self):
        """Test BMI for underweight person"""
        # 50kg, 175cm -> BMI ≈ 16.3
        bmi = calculate_bmi(50, 175)
        assert bmi < 18.5
    
    def test_overweight_bmi(self):
        """Test BMI for overweight person"""
        # 90kg, 170cm -> BMI ≈ 31.1
        bmi = calculate_bmi(90, 170)
        assert bmi >= 30.0


class TestBMICategories:
    """Test BMI category classification"""
    
    def test_normal_category_kz(self):
        """Test normal BMI category in Kazakh"""
        category = get_bmi_category(22.0, Language.KZ)
        assert "Қалыпты" in category
    
    def test_normal_category_ru(self):
        """Test normal BMI category in Russian"""
        category = get_bmi_category(22.0, Language.RU)
        assert "Нормальный" in category
    
    def test_overweight_category(self):
        """Test overweight BMI category"""
        category = get_bmi_category(27.0, Language.RU)
        assert "Избыточная" in category
    
    def test_obese_category(self):
        """Test obese BMI category"""
        category = get_bmi_category(35.0, Language.RU)
        assert "Ожирение" in category


class TestIdealWeightRange:
    """Test ideal weight range calculation"""
    
    def test_male_ideal_weight(self):
        """Test ideal weight for male"""
        min_w, max_w = calculate_ideal_weight_range(180, Gender.MALE)
        # For 180cm male: ~62-81 kg
        assert 60 <= min_w <= 65
        assert 78 <= max_w <= 85
    
    def test_female_ideal_weight(self):
        """Test ideal weight for female"""
        min_w, max_w = calculate_ideal_weight_range(165, Gender.FEMALE)
        # For 165cm female: ~50-68 kg
        assert 48 <= min_w <= 55
        assert 65 <= max_w <= 72


class TestWeightDifference:
    """Test weight difference calculation"""
    
    def test_normal_weight(self):
        """Test within normal range"""
        diff = calculate_weight_difference(70, 60, 80)
        assert diff == 0.0
    
    def test_excess_weight(self):
        """Test excess weight"""
        diff = calculate_weight_difference(90, 60, 80)
        assert diff == 10.0  # 10kg above max
    
    def test_deficit_weight(self):
        """Test weight deficit"""
        diff = calculate_weight_difference(50, 60, 80)
        assert diff == -10.0  # 10kg below min


class TestHealthMetrics:
    """Test complete health metrics calculation"""
    
    def test_complete_metrics(self):
        """Test all metrics calculated together"""
        result = calculate_health_metrics(
            weight_kg=75,
            height_cm=175,
            gender=Gender.MALE,
            language=Language.KZ
        )
        
        assert result.bmi > 0
        assert result.category != ""
        assert result.ideal_weight_min > 0
        assert result.ideal_weight_max > result.ideal_weight_min


class TestHealthScore:
    """Test base health score estimation"""
    
    def test_normal_score(self):
        """Test health score for normal BMI"""
        score = estimate_base_health_score(22.0, 30)
        assert score >= 80
    
    def test_overweight_score(self):
        """Test health score for overweight"""
        score = estimate_base_health_score(28.0, 30)
        assert 60 <= score <= 90
    
    def test_obese_score(self):
        """Test health score for obese"""
        score = estimate_base_health_score(35.0, 30)
        assert score <= 80
    
    def test_elderly_adjustment(self):
        """Test score adjustment for elderly"""
        young_score = estimate_base_health_score(22.0, 30)
        elderly_score = estimate_base_health_score(22.0, 75)
        assert elderly_score < young_score

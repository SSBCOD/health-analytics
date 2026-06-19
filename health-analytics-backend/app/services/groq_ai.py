"""
Groq AI Integration Service
AI-powered health analysis and symptom interpretation
"""
import json
import httpx
from typing import Optional

from app.core.config import get_settings
from app.models import Gender, Language, RiskLevel, UrgencyLevel
from app.schemas import AIAnalysisResult, IdealState
from app.services.health_calculator import BMIResult, estimate_base_health_score

settings = get_settings()


# System prompt templates
SYSTEM_PROMPTS = {
    "kz": """Сен медициналық AI көмекшісі. Сенің міндетің - пайдаланушының денсаулық жағдайын талдау.

МАҢЫЗДЫ ЕРЕЖЕЛЕР:
1. Сен ЕШҚАШАН диагноз қоймайсың
2. Тек аналитикалық бағалау жасайсың
3. Жауабың ҚАТАҢ JSON форматында болуы керек
4. Симптомдардың ұзақтығын ескеруің керек - ұзақ болған сайын қауіп жоғары
5. Егер бәрі жақсы болса - міндетті түрде позитивті хабарлама қайтар

Health Score бағалау:
- 80-100: Жақсы жағдай, елеулі мәселелер жоқ
- 50-79: Орташа ауытқулар, назар аудару керек  
- 0-49: Жоғары қауіп, дәрігерге жүгіну керек

Шұғылдық деңгейлері:
- no_action: Емделу қажет емес, тек өмір салтын жақсарту
- visit_doctor: Жақын арада дәрігерге бару керек
- urgent: Шұғыл медициналық көмек керек""",

    "ru": """Ты медицинский AI-помощник. Твоя задача - анализ состояния здоровья пользователя.

ВАЖНЫЕ ПРАВИЛА:
1. Ты НИКОГДА не ставишь диагнозы
2. Только аналитическая оценка
3. Ответ СТРОГО в формате JSON
4. Учитывай длительность симптомов - чем дольше, тем выше риск
5. Если всё хорошо - обязательно верни позитивное сообщение

Оценка Health Score:
- 80-100: Хорошее состояние, значительных проблем нет
- 50-79: Умеренные отклонения, требуется внимание
- 0-49: Повышенный риск, необходим визит к врачу

Уровни срочности:
- no_action: Лечение не требуется, только улучшение образа жизни
- visit_doctor: Необходимо посетить врача в ближайшее время
- urgent: Требуется срочная медицинская помощь"""
}


USER_PROMPT_TEMPLATES = {
    "kz": """Пайдаланушы деректері:
- Жасы: {age} жас
- Жынысы: {gender}
- Бойы: {height_cm} см
- Салмағы: {weight_kg} кг
- BMI: {bmi} ({bmi_category})
- Қалыпты салмақ диапазоны: {ideal_min}-{ideal_max} кг
- Салмақ айырмашылығы: {weight_diff} кг

Симптомдар мен жағдай сипаттамасы:
{symptoms}

Осы деректерді талдап, келесі JSON форматында жауап бер:
{{
  "language": "kz",
  "bmi": {bmi},
  "health_score": <0-100 сан>,
  "ideal_state": {{
    "optimal_weight_range": "{ideal_min}-{ideal_max} кг",
    "difference": "<қанша кг артық/жетіспейді/нормада>",
    "explanation": "<қарапайым тілмен түсіндірме>"
  }},
  "interpretation": "<симптомдар мен физиологиялық деректердің толық талдауы>",
  "risk_level": "<low|medium|high>",
  "urgency_level": "<no_action|visit_doctor|urgent>",
  "weekly_plan": ["<1-күн>", "<2-күн>", ..., "<7-күн>"] немесе null (қауіп жоғары болса),
  "doctor_recommendation": "<қай дәрігерге бару керек>" немесе null,
  "positive_feedback": "<позитивті, тыныштандыратын хабарлама>",
  "disclaimer": "<бұл диагноз емес деген ескерту>"
}}""",

    "ru": """Данные пользователя:
- Возраст: {age} лет
- Пол: {gender}
- Рост: {height_cm} см
- Вес: {weight_kg} кг
- BMI: {bmi} ({bmi_category})
- Диапазон нормального веса: {ideal_min}-{ideal_max} кг
- Разница от нормы: {weight_diff} кг

Описание симптомов и состояния:
{symptoms}

Проанализируй эти данные и ответь в формате JSON:
{{
  "language": "ru",
  "bmi": {bmi},
  "health_score": <число 0-100>,
  "ideal_state": {{
    "optimal_weight_range": "{ideal_min}-{ideal_max} кг",
    "difference": "<сколько кг лишних/не хватает/в норме>",
    "explanation": "<объяснение простым языком>"
  }},
  "interpretation": "<полный анализ симптомов и физиологических данных>",
  "risk_level": "<low|medium|high>",
  "urgency_level": "<no_action|visit_doctor|urgent>",
  "weekly_plan": ["<день-1>", "<день-2>", ..., "<день-7>"] или null (если риск высокий),
  "doctor_recommendation": "<к какому врачу обратиться>" или null,
  "positive_feedback": "<позитивное, успокаивающее сообщение>",
  "disclaimer": "<предупреждение что это не диагноз>"
}}"""
}


def _build_prompts(
    age: int,
    gender: Gender,
    height_cm: float,
    weight_kg: float,
    symptoms: str,
    bmi_result: BMIResult,
    language: Language
) -> tuple[str, str]:
    """Build system and user prompts for AI"""
    lang = language.value
    
    gender_text = {
        "kz": {"male": "Ер", "female": "Әйел"},
        "ru": {"male": "Мужской", "female": "Женский"}
    }
    
    system_prompt = SYSTEM_PROMPTS[lang]
    
    # Format weight difference text
    if bmi_result.weight_difference > 0:
        weight_diff_text = {
            "kz": f"+{bmi_result.weight_difference} кг (артық)",
            "ru": f"+{bmi_result.weight_difference} кг (избыток)"
        }[lang]
    elif bmi_result.weight_difference < 0:
        weight_diff_text = {
            "kz": f"{bmi_result.weight_difference} кг (жетіспеушілік)",
            "ru": f"{bmi_result.weight_difference} кг (дефицит)"
        }[lang]
    else:
        weight_diff_text = {
            "kz": "норма диапазонында",
            "ru": "в пределах нормы"
        }[lang]
    
    user_prompt = USER_PROMPT_TEMPLATES[lang].format(
        age=age,
        gender=gender_text[lang][gender.value],
        height_cm=height_cm,
        weight_kg=weight_kg,
        bmi=bmi_result.bmi,
        bmi_category=bmi_result.category,
        ideal_min=bmi_result.ideal_weight_min,
        ideal_max=bmi_result.ideal_weight_max,
        weight_diff=weight_diff_text,
        symptoms=symptoms
    )
    
    return system_prompt, user_prompt


def _parse_ai_response(response_text: str, language: Language) -> AIAnalysisResult:
    """
    Parse and validate AI JSON response
    Includes fallback handling for malformed responses
    """
    # Try to extract JSON from response
    try:
        # Sometimes AI wraps JSON in markdown code blocks
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        
        data = json.loads(response_text)
        
        # Validate and create result
        return AIAnalysisResult(
            language=Language(data.get("language", language.value)),
            bmi=float(data.get("bmi", 0)),
            health_score=max(0, min(100, int(data.get("health_score", 50)))),
            ideal_state=IdealState(
                optimal_weight_range=data.get("ideal_state", {}).get("optimal_weight_range", ""),
                difference=data.get("ideal_state", {}).get("difference", ""),
                explanation=data.get("ideal_state", {}).get("explanation", "")
            ),
            interpretation=data.get("interpretation", ""),
            risk_level=RiskLevel(data.get("risk_level", "low")),
            urgency_level=UrgencyLevel(data.get("urgency_level", "no_action")),
            weekly_plan=data.get("weekly_plan"),
            doctor_recommendation=data.get("doctor_recommendation"),
            positive_feedback=data.get("positive_feedback", ""),
            disclaimer=data.get("disclaimer", "")
        )
        
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        # Return fallback response if parsing fails
        fallback_messages = {
            "kz": {
                "interpretation": "AI талдауы қазір қол жетімсіз. Қайта көріңіз.",
                "positive_feedback": "Сіздің денсаулығыңыз маңызды. Қайта талдауды сұраңыз.",
                "disclaimer": "Бұл медициналық кеңес емес."
            },
            "ru": {
                "interpretation": "AI анализ временно недоступен. Попробуйте снова.",
                "positive_feedback": "Ваше здоровье важно. Запросите повторный анализ.",
                "disclaimer": "Это не медицинская консультация."
            }
        }
        
        lang = language.value
        return AIAnalysisResult(
            language=language,
            bmi=0,
            health_score=50,
            ideal_state=IdealState(
                optimal_weight_range="",
                difference="",
                explanation=""
            ),
            interpretation=fallback_messages[lang]["interpretation"],
            risk_level=RiskLevel.MEDIUM,
            urgency_level=UrgencyLevel.VISIT_DOCTOR,
            weekly_plan=None,
            doctor_recommendation=None,
            positive_feedback=fallback_messages[lang]["positive_feedback"],
            disclaimer=fallback_messages[lang]["disclaimer"]
        )


async def analyze_health_with_ai(
    age: int,
    gender: Gender,
    height_cm: float,
    weight_kg: float,
    symptoms: str,
    bmi_result: BMIResult,
    language: Language
) -> AIAnalysisResult:
    """
    Perform AI-powered health analysis using Groq API
    
    Combines physical metrics with symptom interpretation
    to generate comprehensive health assessment
    """
    system_prompt, user_prompt = _build_prompts(
        age=age,
        gender=gender,
        height_cm=height_cm,
        weight_kg=weight_kg,
        symptoms=symptoms,
        bmi_result=bmi_result,
        language=language
    )
    
    # Call Groq API
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                settings.groq_api_url,
                headers={
                    "Authorization": f"Bearer {settings.groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.groq_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.3,  # Lower for more consistent outputs
                    "max_tokens": 2000,
                    "response_format": {"type": "json_object"}
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            ai_text = result["choices"][0]["message"]["content"]
            return _parse_ai_response(ai_text, language)
            
        except httpx.HTTPStatusError as e:
            print(f"Groq API HTTP error: {e.response.status_code}")
            raise
        except httpx.RequestError as e:
            print(f"Groq API request error: {e}")
            raise
        except Exception as e:
            print(f"Groq API unexpected error: {e}")
            raise


def generate_progress_summary(
    prev_score: int,
    curr_score: int,
    prev_bmi: float,
    curr_bmi: float,
    language: Language
) -> tuple[str, bool]:
    """
    Generate progress comparison summary between two analyses
    
    Returns: (summary_text, is_improving)
    """
    is_improving = curr_score >= prev_score and curr_bmi <= prev_bmi
    
    score_diff = curr_score - prev_score
    bmi_diff = round(curr_bmi - prev_bmi, 1)
    
    if language == Language.KZ:
        if is_improving:
            summary = f"Тамаша! Сіздің денсаулық көрсеткіштеріңіз жақсарды. Health Score: {'+' if score_diff > 0 else ''}{score_diff}, BMI: {'+' if bmi_diff > 0 else ''}{bmi_diff}"
        else:
            summary = f"Назар аударыңыз. Көрсеткіштер өзгерді. Health Score: {'+' if score_diff > 0 else ''}{score_diff}, BMI: {'+' if bmi_diff > 0 else ''}{bmi_diff}"
    else:
        if is_improving:
            summary = f"Отлично! Ваши показатели улучшились. Health Score: {'+' if score_diff > 0 else ''}{score_diff}, BMI: {'+' if bmi_diff > 0 else ''}{bmi_diff}"
        else:
            summary = f"Обратите внимание. Показатели изменились. Health Score: {'+' if score_diff > 0 else ''}{score_diff}, BMI: {'+' if bmi_diff > 0 else ''}{bmi_diff}"
    
    return summary, is_improving

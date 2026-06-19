# 🏥 Health Analytics System - Backend

Интеллектуальная система аналитической оценки здоровья с AI интеграцией.

## 📋 Возможности

- ✅ **BMI калькулятор** - расчет индекса массы тела
- ✅ **Health Score** (0-100) - комплексная оценка здоровья
- ✅ **AI анализ симптомов** - интерпретация через Groq API
- ✅ **Идеальный вес** - расчет оптимального диапазона
- ✅ **7-дневный план** - персональные рекомендации
- ✅ **История анализов** - отслеживание прогресса
- ✅ **Мультиязычность** - казахский и русский языки

## 🛠 Технологии

- **FastAPI** - современный async web framework
- **SQLAlchemy 2.0** - ORM с async поддержкой
- **SQLite/PostgreSQL** - база данных
- **Groq AI** - LLaMA для анализа симптомов
- **JWT** - аутентификация
- **Pydantic v2** - валидация данных

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
cd health-analytics-backend
pip install -r requirements.txt
```

### 2. Настройка окружения

```bash
cp .env.example .env
# Отредактируйте .env и добавьте ваш GROQ_API_KEY
```

### 3. Запуск сервера

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Документация API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📡 API Endpoints

### Аутентификация

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/v1/auth/register` | Регистрация |
| POST | `/api/v1/auth/login` | Вход |
| GET | `/api/v1/auth/profile` | Профиль пользователя |
| PATCH | `/api/v1/auth/profile` | Обновление профиля |

### Анализ здоровья

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/v1/health/analyze` | Новый анализ |
| GET | `/api/v1/health/history` | История анализов |
| GET | `/api/v1/health/analysis/{id}` | Детали анализа |
| GET | `/api/v1/health/progress` | Сравнение прогресса |
| DELETE | `/api/v1/health/analysis/{id}` | Удалить анализ |

## 📝 Примеры запросов

### Регистрация

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "Иван Иванов",
    "preferred_language": "ru"
  }'
```

### Анализ здоровья

```bash
curl -X POST http://localhost:8000/api/v1/health/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "age": 35,
    "gender": "male",
    "height_cm": 178,
    "weight_kg": 82,
    "symptoms_text": "Последние 2 недели чувствую усталость, особенно после обеда. Сон нормальный, около 7 часов. Иногда болит голова к вечеру.",
    "language": "ru"
  }'
```

### Пример ответа

```json
{
  "id": 1,
  "age": 35,
  "gender": "male",
  "height_cm": 178,
  "weight_kg": 82,
  "language": "ru",
  "bmi": 25.9,
  "bmi_category": "Избыточная масса тела",
  "ideal_weight_min": 60.2,
  "ideal_weight_max": 79.5,
  "weight_difference": 2.5,
  "health_score": 72,
  "risk_level": "medium",
  "urgency_level": "no_action",
  "interpretation": "Ваш BMI указывает на небольшой избыток веса...",
  "ideal_state": {
    "optimal_weight_range": "60.2-79.5 кг",
    "difference": "2.5 кг выше нормы",
    "explanation": "Для вашего роста оптимальный вес..."
  },
  "weekly_plan": [
    "День 1: Начните с 30 минут ходьбы...",
    "День 2: Увеличьте потребление воды до 2л...",
    ...
  ],
  "doctor_recommendation": null,
  "positive_feedback": "Ваше состояние в целом хорошее!...",
  "disclaimer": "Данный анализ не является медицинским диагнозом...",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## 🧪 Тестирование

```bash
pytest tests/ -v
```

## 📁 Структура проекта

```
health-analytics-backend/
├── app/
│   ├── api/              # API роутеры
│   │   ├── auth.py       # Аутентификация
│   │   └── health.py     # Анализ здоровья
│   ├── core/             # Ядро приложения
│   │   ├── config.py     # Конфигурация
│   │   ├── database.py   # Подключение к БД
│   │   └── security.py   # JWT, пароли
│   ├── models/           # SQLAlchemy модели
│   │   └── models.py     # User, HealthAnalysis
│   ├── schemas/          # Pydantic схемы
│   │   └── schemas.py    # Request/Response
│   ├── services/         # Бизнес-логика
│   │   ├── health_calculator.py  # BMI расчеты
│   │   └── groq_ai.py    # AI интеграция
│   └── main.py           # Точка входа
├── tests/                # Тесты
├── requirements.txt
├── .env.example
└── README.md
```

## ⚠️ Важно

**Эта система НЕ ставит медицинских диагнозов.**

Все результаты носят информационный характер.
При наличии симптомов обязательно обратитесь к врачу.

## 📄 Лицензия

MIT License

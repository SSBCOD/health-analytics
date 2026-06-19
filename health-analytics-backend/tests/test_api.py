"""
API Tests for Health Analytics System
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_root_endpoint():
    """Test root endpoint returns API info"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["status"] == "running"


@pytest.mark.anyio
async def test_health_check():
    """Test health check endpoint"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.anyio
async def test_register_user():
    """Test user registration"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
                "full_name": "Test User",
                "preferred_language": "kz"
            }
        )
        # May return 201 (created) or 400 (if already exists)
        assert response.status_code in [201, 400]
        
        if response.status_code == 201:
            data = response.json()
            assert "access_token" in data
            assert data["email"] == "test@example.com"


@pytest.mark.anyio
async def test_analyze_without_auth():
    """Test that analyze endpoint requires authentication"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/health/analyze",
            json={
                "age": 30,
                "gender": "male",
                "height_cm": 175,
                "weight_kg": 75,
                "symptoms_text": "Feeling tired",
                "language": "kz"
            }
        )
        assert response.status_code == 403  # Forbidden without auth

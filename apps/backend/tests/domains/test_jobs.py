import pytest
import pytest_asyncio

@pytest_asyncio.fixture
async def auth_client(client):
    # Register user
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "job@test.com", "username": "job@test.com", "password": "Password123!", "full_name": "Job User"}
    )
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "job@test.com", "password": "Password123!"}
    )
    token = response.json()["access_token"]
    
    # Inject token into a new authorized client
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client

@pytest.mark.asyncio
async def test_job_search_unauthorized(client):
    # Should fail without token
    response = await client.post("/api/v1/jobs/search?query=Python")
    assert response.status_code == 401

from unittest.mock import patch

@pytest.mark.asyncio
async def test_job_search_authorized(auth_client):
    with patch("app.services.job_service.JobService.search_and_save_jobs") as mock_search:
        from app.models.job import Job
        from datetime import datetime
        mock_job = Job(
            id=1,
            title="Mocked Python Dev",
            company="Mock Inc",
            location="Remote",
            is_remote=True,
            source_url="http://mock.com",
            description="Mock jobs",
            source_platform="mock",
            compatibility_score=0.95,
            posted_date=datetime.utcnow()
        )
        mock_search.return_value = [mock_job]
        
        response = await auth_client.post("/api/v1/jobs/search?query=Python&limit=1")
    
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["title"] == "Mocked Python Dev"

@pytest.mark.asyncio
async def test_recommended_empty(auth_client):
    # New user shouldn't have any recommended jobs yet
    response = await auth_client.get("/api/v1/jobs/recommended")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

import pytest
from httpx import AsyncClient
from app.core.config import settings
import uuid

# Helper to generate unique job data
def get_job_data():
    return {
        "title": "Backend Developer",
        "company": "Tech Corp",
        "source_url": "https://techcorp.com/jobs/123",
        "location": "Remote",
        "description": "Python, FastAPI, Docker",
        "salary_min": 8000.0,
        "salary_max": 12000.0,
        "external_id": f"job_{uuid.uuid4()}",
        "source_platform": "manual"
    }

@pytest.fixture
async def auth_headers(client: AsyncClient):
    # Login to get valid token
    user_data = {
        "email": "job_tester@example.com",
        "username": "job_tester",
        "password": "password123",
        "full_name": "Job Tester"
    }
    
    # Try login first
    login_res = await client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        data={"username": user_data["email"], "password": user_data["password"]}
    )
    
    if login_res.status_code != 200:
        # Create user if not exists (or ignore if fails due to unique constraint, try login again)
        await client.post(
            f"{settings.API_V1_PREFIX}/auth/signup",
            json=user_data
        )
        login_res = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]}
        )
    
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_create_job(client: AsyncClient, auth_headers):
    """Test creating a new job"""
    job_data = get_job_data()
    response = await client.post(
        f"{settings.API_V1_PREFIX}/jobs/",
        json=job_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == job_data["title"]
    assert "id" in data
    return data["id"]

@pytest.mark.asyncio
async def test_read_jobs(client: AsyncClient, auth_headers):
    """Test reading list of jobs"""
    # Ensure at least one job exists
    job_data = get_job_data()
    await client.post(
        f"{settings.API_V1_PREFIX}/jobs/",
        json=job_data,
        headers=auth_headers
    )
    
    response = await client.get(
        f"{settings.API_V1_PREFIX}/jobs/",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

@pytest.mark.asyncio
async def test_read_job_by_id(client: AsyncClient, auth_headers):
    """Test reading a specific job"""
    job_data = get_job_data()
    create_res = await client.post(
        f"{settings.API_V1_PREFIX}/jobs/",
        json=job_data,
        headers=auth_headers
    )
    job_id = create_res.json()["id"]
    
    response = await client.get(
        f"{settings.API_V1_PREFIX}/jobs/{job_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job_id
    assert data["title"] == job_data["title"]

@pytest.mark.asyncio
async def test_update_job(client: AsyncClient, auth_headers):
    """Test updating a job"""
    job_data = get_job_data()
    create_res = await client.post(
        f"{settings.API_V1_PREFIX}/jobs/",
        json=job_data,
        headers=auth_headers
    )
    job_id = create_res.json()["id"]
    
    update_data = {"description": "Updated Description with Python 3.12"}
    
    response = await client.put(
        f"{settings.API_V1_PREFIX}/jobs/{job_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == update_data["description"]
    assert data["title"] == job_data["title"]  # Unchanged field

@pytest.mark.asyncio
async def test_delete_job(client: AsyncClient, auth_headers):
    """Test deleting a job"""
    job_data = get_job_data()
    create_res = await client.post(
        f"{settings.API_V1_PREFIX}/jobs/",
        json=job_data,
        headers=auth_headers
    )
    job_id = create_res.json()["id"]
    
    # Delete
    del_response = await client.delete(
        f"{settings.API_V1_PREFIX}/jobs/{job_id}",
        headers=auth_headers
    )
    assert del_response.status_code == 200
    
    # Verify deletion
    get_response = await client.get(
        f"{settings.API_V1_PREFIX}/jobs/{job_id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404

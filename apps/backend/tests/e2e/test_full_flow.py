import pytest
import pytest_asyncio
import io
from unittest.mock import patch, MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_end_to_end_user_journey(client):
    """
    Simulates a complete user journey:
    1. Register
    2. Login
    3. Upload Resume
    4. Search Jobs (mocked scrapers)
    5. Check Dashboard Stats
    """
    
    # 1. Register User
    signup_data = {
        "email": "e2e_user@test.com",
        "username": "e2e_user@test.com",
        "password": "Password123!",
        "full_name": "E2E Test User"
    }
    resp = await client.post("/api/v1/auth/signup", json=signup_data)
    assert resp.status_code == 201
    
    # 2. Login
    login_data = {"username": "e2e_user@test.com", "password": "Password123!"}
    resp = await client.post("/api/v1/auth/login", data=login_data)
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Upload Resume
    file_content = b"E2E Resume Name, Java Developer"
    resp = await client.post(
        "/api/v1/resumes",
        headers=headers,
        files={"file": ("e2e_resume.pdf", io.BytesIO(file_content), "application/pdf")},
        follow_redirects=True
    )
    assert resp.status_code == 200
    resume_data = resp.json()
    assert resume_data["filename"] == "e2e_resume.pdf"
    
    # 4. Search Jobs (Mocking the JobService to avoid live scraping)
    with patch("app.services.job_service.JobService.search_and_save_jobs", new_callable=AsyncMock) as mock_search:
        mock_job = MagicMock()
        mock_job.id = 1
        mock_job.title = "Java Developer"
        mock_job.company = "E2E Tech"
        mock_job.location = "Remote"
        mock_job.is_remote = True
        mock_job.source_url = "http://e2e.com/job/1"
        mock_job.external_id = "mock_e2e_1"
        mock_job.source_platform = "mock"
        mock_job.is_active = True
        mock_job.is_favorite = False
        mock_job.is_hidden = False
        mock_job.description = "E2E Mock description"
        mock_job.requirements = None
        mock_job.salary_min = None
        mock_job.salary_max = None
        mock_job.salary_currency = "BRL"
        mock_job.compatibility_score = 0.99
        mock_job.culture_fit_score = 0.95
        mock_job.extracted_technologies = ["Java"]
        mock_job.pros = ["Remote"]
        mock_job.cons = ["Testing"]
        from datetime import datetime
        mock_job.posted_date = datetime.utcnow()
        mock_job.found_date = datetime.utcnow()
        mock_job.analyzed_date = datetime.utcnow()
        mock_job.created_at = datetime.utcnow()
        mock_search.return_value = [mock_job]
        
        # In the actual API, /api/v1/jobs/search takes query params
        resp = await client.post("/api/v1/jobs/search?query=Java&limit=1", headers=headers)
        assert resp.status_code == 200
        jobs = resp.json()
        assert len(jobs) == 1
        assert jobs[0]["title"] == "Java Developer"
        
    # 5. Check Dashboard Stats
    resp = await client.get("/api/v1/stats", headers=headers, follow_redirects=True)
    # If the stats route correctly aggregates data, it should return 200 OK
    assert resp.status_code == 200
    stats = resp.json()
    assert "total_jobs_available" in stats

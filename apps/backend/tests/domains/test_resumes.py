import pytest
import pytest_asyncio
import io

@pytest_asyncio.fixture
async def auth_client(client):
    # Register user
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "resume@test.com", "username": "resume@test.com", "password": "Password123!", "full_name": "Resume User"}
    )
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "resume@test.com", "password": "Password123!"}
    )
    token = response.json()["access_token"]
    
    # Inject token
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client

@pytest.mark.asyncio
async def test_resume_upload_unauthorized(client):
    # Missing token
    file_content = b"Mock Resume Content"
    response = await client.post(
        "/api/v1/resumes",
        files={"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")},
        follow_redirects=True
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_resume_upload_authorized(auth_client):
    file_content = b"Mock Resume Content PDF"
    response = await auth_client.post(
        "/api/v1/resumes",
        files={"file": ("test_resume.pdf", io.BytesIO(file_content), "application/pdf")},
        follow_redirects=True
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_resume.pdf"
    assert "upload_id" in data or "id" in data
    assert "is_analyzed" in data

@pytest.mark.asyncio
async def test_resume_status_missing(auth_client):
    # Query status of a non-existent upload id
    response = await auth_client.get("/api/v1/resumes/status/99999")
    assert response.status_code == 404

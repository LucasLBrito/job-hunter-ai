import pytest
from httpx import AsyncClient
from app.core.config import settings

# Dados de teste
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_USER_USERNAME = "testuser"

@pytest.mark.asyncio
async def test_signup(client: AsyncClient):
    """Test user registration"""
    response = await client.post(
        f"{settings.API_V1_PREFIX}/auth/signup",
        json={
            "email": TEST_USER_EMAIL,
            "username": TEST_USER_USERNAME,
            "password": TEST_USER_PASSWORD,
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == TEST_USER_EMAIL
    assert "id" in data
    assert "hashed_password" not in data  # Security check

@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """Test login and token retrieval"""
    # First create user (depend on test_signup working or create fixture)
    # For isolation, let's just create it again (DB is reset per test ideally or we handle conflict)
    # Since fixtures reuse DB per session in this simple setup, user might exist
    
    # Try to login
    response = await client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        data={
            "username": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # If user doesn't exist (test order), create first
    if response.status_code == 401:
        await client.post(
            f"{settings.API_V1_PREFIX}/auth/signup",
            json={
                "email": TEST_USER_EMAIL,
                "username": TEST_USER_USERNAME,
                "password": TEST_USER_PASSWORD,
                "full_name": "Test User"
            }
        )
        response = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    return data["access_token"]

@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    """Test get current user profile"""
    # Login to get token
    login_res = await client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        data={
            "username": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
    )
    
    # If login fails, create user then login
    if login_res.status_code != 200:
          await client.post(
            f"{settings.API_V1_PREFIX}/auth/signup",
            json={
                "email": TEST_USER_EMAIL,
                "username": TEST_USER_USERNAME,
                "password": TEST_USER_PASSWORD,
                "full_name": "Test User"
            }
        )
          login_res = await client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={
                "username": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
        )
    
    token = login_res.json()["access_token"]
    
    response = await client.get(
        f"{settings.API_V1_PREFIX}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == TEST_USER_EMAIL
    assert data["is_active"] is True

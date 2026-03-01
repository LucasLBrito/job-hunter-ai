import pytest
import pytest_asyncio

@pytest.mark.asyncio
async def test_signup_success(client):
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "newuser@test.com",
            "username": "newuser@test.com",
            "password": "Password123!",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_signup_duplicate_email(client):
    # Setup first user
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "dup@test.com", "username": "dup@test.com", "password": "Password123!", "full_name": "User 1"}
    )
    # Try again
    response = await client.post(
        "/api/v1/auth/signup",
        json={"email": "dup@test.com", "username": "dup@test.com", "password": "Password123!", "full_name": "User 2"}
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_login_success(client):
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "login@test.com", "username": "login@test.com", "password": "Password123!", "full_name": "Login User"}
    )
    
    # OAuth2 uses form-data
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "login@test.com", "password": "Password123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "wrong@test.com", "username": "wrong@test.com", "password": "Password123!", "full_name": "Wrong User"}
    )
    
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "wrong@test.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401

import httpx
import asyncio
import json

async def test_api():
    base_url = "http://localhost:8000/api/v1"
    
    async with httpx.AsyncClient() as client:
        # 1. Login to get token (assuming test user exists, creating if not is harder, let's just create one)
        print("Creating test user if not exists...")
        test_email = "test_search@example.com"
        test_pass = "Test12345!"
        
        # Signup
        signup_res = await client.post(f"{base_url}/auth/signup", json={
            "email": test_email,
            "username": "test_search",
            "password": test_pass,
            "full_name": "Test Search"
        })
        
        # 2. Login
        print("Logging in...")
        login_res = await client.post(f"{base_url}/auth/login", data={
            "username": test_email,
            "password": test_pass
        })
        
        if login_res.status_code != 200:
            print(f"Login failed: {login_res.status_code} - {login_res.text}")
            return
            
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Search
        print("Starting search via API...")
        try:
            search_res = await client.post(
                f"{base_url}/jobs/search?query=python&limit=2", 
                headers=headers,
                timeout=60.0 # generous timeout
            )
            print(f"Search status: {search_res.status_code}")
            if search_res.status_code == 200:
                print(f"Found {len(search_res.json())} jobs")
            else:
                print(f"Error payload: {search_res.text}")
        except Exception as e:
            print(f"Exception during request: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())

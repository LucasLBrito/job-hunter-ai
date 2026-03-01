import requests
import json

# Create test user with correct schema
signup_url = "http://localhost:8000/api/v1/auth/signup"
signup_data = {
    "email": "lucas@test.com",
    "username": "lucas_test",
    "password": "senha123",
    "full_name": "Lucas Teste"
}

print("=== Creating test user ===")
try:
    signup_response = requests.post(signup_url, json=signup_data)
    print(f"Signup Status: {signup_response.status_code}")
    
    if signup_response.status_code in [200, 201]:
        print("✅ User created!")
        print(json.dumps(signup_response.json(), indent=2))
    elif signup_response.status_code == 400:
        print("⚠️  User already exists")
    else:
        print(f"❌ Signup failed: {signup_response.text}")
        
    # Login
    print("\n=== Logging in ===")
    login_url = "http://localhost:8000/api/v1/auth/login"
    login_data = {
        "username": "lucas@test.com",  # Can use email or username
        "password": "senha123"
    }
    
    login_response = requests.post(login_url, data=login_data)
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data.get('access_token')
        print(f"✅ Token obtained: {token[:40]}...")
        
        # Test recommended endpoint
        print("\n=== Testing /jobs/recommended ===")
        headers = {"Authorization": f"Bearer {token}"}
        rec_url = "http://localhost:8000/api/v1/jobs/recommended?limit=5"
        
        rec_response = requests.get(rec_url, headers=headers)
        print(f"Status Code: {rec_response.status_code}")
        print(f"Content-Type: {rec_response.headers.get('content-type')}")
        print(f"\nResponse Body:")
        
        try:
            response_json = rec_response.json()
            print(json.dumps(response_json, indent=2))
            
            if rec_response.status_code == 200:
                jobs = response_json if isinstance(response_json, list) else []
                print(f"\n✅ SUCCESS! Got {len(jobs)} recommended jobs")
                if len(jobs) > 0:
                    print(f"First job: {jobs[0].get('title')} at {jobs[0].get('company')}")
            else:
                print(f"\n❌ Error {rec_response.status_code}")
        except Exception as e:
            print(f"Response (text): {rec_response.text}")
            print(f"Parse error: {e}")
    else:
        print(f"❌ Login failed: {login_response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

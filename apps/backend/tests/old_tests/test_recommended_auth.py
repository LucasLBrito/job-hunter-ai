import requests
import json
import sys

# First, let's get a valid token by logging in
login_url = "http://localhost:8000/api/v1/auth/login"
login_data = {
    "username": "lucas@example.com",  # Adjust to your test user
    "password": "senha123"
}

print("Step 1: Logging in...")
try:
    # Login
    login_response = requests.post(login_url, data=login_data)
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data.get('access_token')
        print(f"Token obtained: {token[:20]}...")
        
        # Now test the recommended endpoint with the token
        print("\nStep 2: Testing /jobs/recommended with auth...")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        rec_url = "http://localhost:8000/api/v1/jobs/recommended?limit=5"
        rec_response = requests.get(rec_url, headers=headers)
        
        print(f"Recommended Status: {rec_response.status_code}")
        print(f"Response Headers: {dict(rec_response.headers)}")
        print(f"\nResponse Body:")
        
        try:
            response_json = rec_response.json()
            print(json.dumps(response_json, indent=2))
        except:
            print(rec_response.text)
            
    else:
        print(f"Login failed: {login_response.text}")
        print("\nTrying without auth to see error...")
        rec_url = "http://localhost:8000/api/v1/jobs/recommended?limit=5"
        rec_response = requests.get(rec_url)
        print(f"Status: {rec_response.status_code}")
        print(f"Response: {rec_response.text}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

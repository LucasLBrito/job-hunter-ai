import requests
import json

# Test recommended endpoint
url = "http://localhost:8000/api/v1/jobs/recommended?limit=5"

# Get token from localStorage or use test user
# For now, let's test without auth to see the exact error
headers = {}

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Response: {response.text}")
    
    if response.status_code != 200:
        try:
            error_detail = response.json()
            print(f"\nError Detail: {json.dumps(error_detail, indent=2)}")
        except:
            pass
except Exception as e:
    print(f"Error: {e}")

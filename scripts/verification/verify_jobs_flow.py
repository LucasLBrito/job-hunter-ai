import requests
import sys
import json

BASE_URL = "http://localhost:8000/api/v1"

def print_result(step, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {step}")
    if details:
        print(f"   Details: {details}")
    if not success:
        sys.exit(1)

def verify_jobs():
    print("🚀 Starting Job Search Verification...\n")
    
    # 1. Login to get token
    username = "skill_test_user"
    password = "password123"
    
    # We assume user exists from previous test. If not, this fails (which is valid test result).
    r = requests.post(f"{BASE_URL}/auth/login", data={"username": username, "password": password})
    
    if r.status_code != 200:
        # Try registering if login fails
        print("   User not found, registering...")
        requests.post(f"{BASE_URL}/auth/signup", json={
            "username": username, "email": "skill_test@example.com", 
            "password": password, "full_name": "Skill Test User"
        })
        r = requests.post(f"{BASE_URL}/auth/login", data={"username": username, "password": password})
        
    if r.status_code != 200:
        print_result("Login", False, f"Could not login: {r.text}")
        
    access_token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    print_result("Login", True, "Authenticated")

    # 2. Search Jobs
    query = "python"
    print(f"   Searching for '{query}' jobs (this triggers the scraper)...")
    
    # POST /jobs/search ?query=python
    # Note: jobs.py defines query as query param, not body? 
    # @router.post("/search") def search_jobs(*, query: str, ...)
    # So it expects ?query=... in URL
    
    r = requests.post(f"{BASE_URL}/jobs/search?query={query}&limit=5", headers=headers)
    
    if r.status_code == 200:
        jobs = r.json()
        print_result("Job Search", True, f"Found {len(jobs)} jobs")
        if len(jobs) > 0:
            print(f"   Example: {jobs[0].get('title')} at {jobs[0].get('company')}")
    else:
        print_result("Job Search", False, f"{r.status_code} - {r.text}")

if __name__ == "__main__":
    verify_jobs()

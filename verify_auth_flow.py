import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def print_result(step, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {step}")
    if details:
        print(f"   Details: {details}")
    if not success:
        sys.exit(1)

def verify_auth():
    print("🚀 Starting Authentication Flow Verification (Skill-Based Testing)...\n")
    
    # 1. Test Health
    try:
        r = requests.get(f"http://localhost:8000/health")
        print_result("Health Check", r.status_code == 200, r.json())
    except Exception as e:
        print_result("Health Check", False, f"Connection failed: {e}")

    # 2. Register User
    username = "skill_test_user"
    email = "skill_test@example.com"
    password = "password123"
    
    payload = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": "Skill Test User"
    }
    
    # Clean up potentially existing user (optional/hard to do without admin, so we just try register)
    # If exists, we proceed to login.
    
    print(f"   Attempting to register {username}...")
    r = requests.post(f"{BASE_URL}/auth/signup", json=payload)
    
    if r.status_code == 201:
        print_result("Registration", True, "User created successfully")
    elif r.status_code == 400 and "already registered" in r.text:
        print_result("Registration", True, "User already exists (proceeding)")
    else:
        print_result("Registration", False, f"{r.status_code} - {r.text}")

    # 3. Login (Get Token)
    login_data = {
        "username": username, # Backend auth checks email OR username logic? No, typically username field expects username or email depending on implementation.
        # CRUD.authenticate check both.
        "password": password
    }
    # OAuth2 form request usually key is 'username' for the identifier
    
    print(f"   Attempting to login...")
    r = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if r.status_code == 200:
        token_data = r.json()
        access_token = token_data.get("access_token")
        print_result("Login", True, f"Token received: {access_token[:10]}...")
    else:
        print_result("Login", False, f"{r.status_code} - {r.text}")

    # 4. Verify Route (Get Me)
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if r.status_code == 200:
        user_data = r.json()
        print_result("Verify Token (Get Me)", True, f"User: {user_data.get('username')}")
    else:
        print_result("Verify Token (Get Me)", False, f"{r.status_code} - {r.text}")

if __name__ == "__main__":
    verify_auth()

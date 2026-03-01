
import requests
import json
import random
import string

BASE_URL = "http://localhost:8000/api/v1/auth"

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def test_signup():
    print("="*60)
    print("🚦 TESTING SIGNUP ENDPOINT")
    print("="*60)

    # 1. Test Short Password (Expect 422)
    print("\n1️⃣ Testing Short Password (6 chars)...")
    username = f"user_{generate_random_string(5)}"
    email = f"{username}@test.com"
    payload_short = {
        "full_name": "Test User",
        "username": username,
        "email": email,
        "password": "short" # 5 chars
    }
    try:
        res = requests.post(f"{BASE_URL}/signup", json=payload_short)
        print(f"   Status Code: {res.status_code}")
        print(f"   Response: {res.text}")
        if res.status_code == 422:
            print("   ✅ Correctly rejected short password (422)")
        else:
            print(f"   ⚠️ Unexpected status code: {res.status_code}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

    # 2. Test Valid Password (Expect 201)
    print("\n2️⃣ Testing Valid Password (8+ chars)...")
    username_valid = f"user_{generate_random_string(5)}"
    email_valid = f"{username_valid}@test.com"
    payload_valid = {
        "full_name": "Test User",
        "username": username_valid,
        "email": email_valid,
        "password": "valid_password_123" # 18 chars
    }
    try:
        res = requests.post(f"{BASE_URL}/signup", json=payload_valid)
        print(f"   Status Code: {res.status_code}")
        print(f"   Response: {res.text}")
        if res.status_code == 201:
            print("   ✅ Signup Successful (201)")
        else:
            print(f"   ❌ Signup Failed: {res.status_code}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        
    # 3. Test Existing Email (Expect 400) - If 2 passed
    if res.status_code == 201:
        print("\n3️⃣ Testing Existing Email (Expect 400)...")
        try:
            res = requests.post(f"{BASE_URL}/signup", json=payload_valid)
            print(f"   Status Code: {res.status_code}")
            if res.status_code == 400:
                print("   ✅ Correctly rejected existing email (400)")
            else:
                print(f"   ⚠️ Unexpected status code: {res.status_code}")
        except Exception as e:
             print(f"   ❌ Request failed: {e}")

if __name__ == "__main__":
    test_signup()

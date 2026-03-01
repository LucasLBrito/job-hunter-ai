import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("="*60)
print("  TESTE DE AUTENTICAÇÃO - DEBUG")
print("="*60)

# Test 1: Health check
print("\n1. Health Check:")
try:
    r = requests.get("http://localhost:8000/health")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text}")
except Exception as e:
    print(f"   Erro: {e}")

# Test 2: Signup
print("\n2. Signup:")
signup_data = {
    "email": "debug@test.com",
    "username": "debuguser",
    "password": "senha12345",
    "full_name": "Debug User"
}

try:
    r = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text[:500]}")
    
    if r.status_code in [200, 201]:
        print("   ✅ Signup OK")
        
        # Test 3: Login
        print("\n3. Login:")
        login_data = {
            "username": signup_data["email"],
            "password": signup_data["password"]
        }
        
        r = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"   Status: {r.status_code}")
        
        if r.status_code == 200:
            token = r.json()['access_token']
            print(f"   ✅ Token: {token[:50]}...")
            
            # Test 4: /me
            print("\n4. /me endpoint:")
            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            print(f"   Status: {r.status_code}")
            print(f"   Response: {r.text[:300]}")
        else:
            print(f"   ❌ Login falhou: {r.text}")
    else:
        print(f"   ❌ Signup falhou")
        
except Exception as e:
    print(f"   Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)

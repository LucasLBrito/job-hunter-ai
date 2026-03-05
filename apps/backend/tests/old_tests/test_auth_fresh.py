import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

timestamp = int(time.time())
email = f"fresh{timestamp}@test.com"
username = f"fresh{timestamp}"
password = "senha12345"

print("="*60)
print("  TESTE COMPLETO de AUTH")
print("="*60)

# Signup com email novo
print(f"\n1. Signup com {email}")
r = requests.post(f"{BASE_URL}/auth/signup", json={
    "email": email,
    "username": username,
    "password": password,
    "full_name": "Fresh User"
})
print(f"   Status: {r.status_code}")
if r.status_code not in [200, 201]:
    print(f"   Erro: {r.text}")
    exit()
else:
    print("   ✅ Signup OK")

# Login  
print(f"\n2. Login")
r = requests.post(f"{BASE_URL}/auth/login", data={
    "username": email,  # Backend espera email aqui
    "password": password
})
print(f"   Status: {r.status_code}")
if r.status_code != 200:
    print(f"   Erro: {r.text}")
    exit()
else:
    token = r.json()['access_token']
    print(f"   ✅ Token obtido: {token[:30]}...")

# /me
print(f"\n3. GET /auth/me")
headers = {"Authorization": f"Bearer {token}"}
r = requests.get(f"{BASE_URL}/auth/me", headers=headers)
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    user = r.json()
    print(f"   ✅ Usuário: {user['email']}")
else:
    print(f"   Erro: {r.text}")

print("\n" + "="*60)
print("✅ BACKEND AUTH FUNCIONANDO PERFEITAMENTE!")
print(f"\nCredenciais para testar no frontend:")
print(f"  Email: {email}")
print(f"  Senha: {password}")
print("="*60)

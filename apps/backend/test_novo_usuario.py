"""
Teste com novo usuário (email diferente)
"""
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

timestamp = int(time.time())
email = f"usuario{timestamp}@test.com"
username = f"user{timestamp}"

print("="*70)
print("  🧪 TESTE COM NOVO USUÁRIO")
print("="*70)

print(f"\n📝 Criando usuário:")
print(f"   Email: {email}")
print(f"   Username: {username}")

r = requests.post(f"{BASE_URL}/auth/signup", json={
    "email": email,
    "username": username,
    "password": "senha12345",
    "full_name": "Usuário Teste"
})

print(f"\n   Status: {r.status_code}")
if r.status_code == 201:
    user = r.json()
    print(f"   ✅ SUCESSO! Usuário criado")
    print(f"   ID: {user['id']}")
    print(f"   Email: {user['email']}")
    
    # Login
    print(f"\n🔐 Fazendo login:")
    r = requests.post(f"{BASE_URL}/auth/login", data={
        "username": email,
        "password": "senha12345"
    })
    
    if r.status_code == 200:
        token = r.json()['access_token']
        print(f"   ✅ Login OK!")
        
        # /me
        r = requests.get(f"{BASE_URL}/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        if r.status_code == 200:
            print(f"   ✅ Autenticação completa!")
            
            print("\n" + "="*70)
            print("  ✅ SISTEMA FUNCIONANDO 100%!")
            print("="*70)
            print(f"\n📋 CREDENCIAIS PARA USO NO NAVEGADOR:")
            print(f"   Email: {email}")
            print(f"   Senha: senha12345")
            print("="*70)
            print(f"\n📂 Arquivo do banco:")
            print(f"   apps/backend/data/database.db")
            print("="*70)
else:
    print(f"   ❌ Erro: {r.text}")

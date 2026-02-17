"""
Teste com banco limpo - Criar primeiro usuário
"""
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

print("="*70)
print("  🧪 TESTE COM BANCO LIMPO")
print("="*70)

# Criar primeiro usuário
email = "primeiro@test.com"
username = "primeiro"
password = "senha12345"

print(f"\n1️⃣ Criando primeiro usuário no banco limpo:")
print(f"   Email: {email}")
print(f"   Username: {username}")

r = requests.post(f"{BASE_URL}/auth/signup", json={
    "email": email,
    "username": username,
    "password": password,
    "full_name": "Primeiro Usuário"
})

print(f"\n   Status: {r.status_code}")
if r.status_code == 201:
    print(f"   ✅ Usuário criado com sucesso!")
    user = r.json()
    print(f"   ID: {user['id']}")
    print(f"   Email: {user['email']}")
    
    # Fazer login
    print(f"\n2️⃣ Fazendo login:")
    r = requests.post(f"{BASE_URL}/auth/login", data={
        "username": email,
        "password": password
    })
    
    if r.status_code == 200:
        token = r.json()['access_token']
        print(f"   ✅ Login OK!")
        print(f"   Token: {token[:40]}...")
        
        # Test /me
        print(f"\n3️⃣ Testando /auth/me:")
        r = requests.get(f"{BASE_URL}/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        if r.status_code == 200:
            print(f"   ✅ Autenticação funcionando!")
            print(f"   Usuário: {r.json()['email']}")
            
            print("\n" + "="*70)
            print("  ✅ TUDO FUNCIONANDO COM BANCO LIMPO!")
            print("="*70)
            print(f"\n📋 CREDENCIAIS PARA TESTE NO NAVEGADOR:")
            print(f"   Email: {email}")
            print(f"   Senha: {password}")
            print("="*70)
        else:
            print(f"   ❌ Erro /me: {r.text}")
    else:
        print(f"   ❌ Erro login: {r.text}")
else:
    print(f"   ❌ Erro: {r.text}")

print("\n🔍 Verifique os logs do backend para ver o logging detalhado!")

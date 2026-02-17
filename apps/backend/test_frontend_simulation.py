"""
Monitor backend logs in real-time for authentication requests
"""
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

print("="*70)
print("  TESTE DE COMUNICAÇÃO FRONTEND → BACKEND")
print("="*70)

# Simulate what frontend does
print("\n📡 Simulando requisição do FRONTEND...")
print("\n1. Tentando LOGIN (como o frontend faz):")

# Exactly as frontend sends
form_data = {
    'username': 'fresh1771339140@test.com',  # Email que sabemos que funciona
    'password': 'senha12345'
}

print(f"   Dados enviados: {form_data}")
print(f"   Content-Type: application/x-www-form-urlencoded")
print(f"   URL: {BASE_URL}/auth/login")

try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=form_data,  # URLencoded form
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    print(f"\n   ✅ Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Token recebido: {data['access_token'][:40]}...")
        
        # Test /me with token
        print("\n2. Testando GET /auth/me:")
        token = data['access_token']
        me_response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={'Authorization': f'Bearer {token}'}
        )
        print(f"   Status: {me_response.status_code}")
        if me_response.status_code == 200:
            user = me_response.json()
            print(f"   ✅ Usuário: {user['email']}")
            print("\n" + "="*70)
            print("  ✅ BACKEND ESTÁ FUNCIONANDO PERFEITAMENTE!")
            print("="*70)
        else:
            print(f"   ❌ Erro /me: {me_response.text}")
    else:
        print(f"   ❌ Erro: {response.text}")
        print("\n💡 DIAGNÓSTICO:")
        print("   - Backend pode estar com cache")
        print("   - Ou há 2 backends rodando simultaneamente")
        print("   - Verificar logs do backend!")
        
except Exception as e:
    print(f"\n❌ Erro de conexão: {e}")
    print("\n💡 PROBLEMA:")
    print("   Backend pode não estar rodando na porta 8000")
    print("   Ou há conflito de portas")

print("\n" + "="*70)

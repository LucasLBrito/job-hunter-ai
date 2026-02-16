import asyncio
import httpx
import json

# Config
API_URL = "http://localhost:8001/api/v1"
TEST_USER = {
    "email": "preferences_tester@example.com",
    "username": "preferences_tester",
    "password": "password123",
    "full_name": "Preferences Tester"
}

PREFERENCES_PAYLOAD = {
    "technologies": ["Python", "React", "FastAPI", "Docker"],
    "job_titles": ["Backend Engineer", "Fullstack Developer", "Software Architect"],
    "work_models": ["Remote", "Hybrid"],
    "employment_types": ["Full-time", "Contract"],
    "company_styles": ["Startup", "Scale-up", "Tech Company"],
    "seniority_level": "Senior",
    "preferred_locations": ["São Paulo", "Remote", "Lisbon"],
    "salary_min": 15000,
    "salary_max": 25000,
    "benefits": ["Health Insurance", "Remote First", "GymPass", "VR"],
    "industries": ["Fintech", "AI", "Healthtech"],
    "current_status": "Employed",
    "reason_for_search": "Better opportunities and salary",
    "open_to_relocation": True,
    "availability": "1 month notice"
}

async def get_token(client):
    """Get auth token, creating user if needed"""
    try:
        # Try login
        res = await client.post(f"{API_URL}/auth/login", data={"username": TEST_USER["email"], "password": TEST_USER["password"]})
        if res.status_code == 200:
            return res.json()["access_token"]
        
        # Create user
        print(f"User not found, creating {TEST_USER['email']}...")
        await client.post(f"{API_URL}/auth/signup", json=TEST_USER)
        
        # Login again
        res = await client.post(f"{API_URL}/auth/login", data={"username": TEST_USER["email"], "password": TEST_USER["password"]})
        return res.json()["access_token"]
    except Exception as e:
        print(f"Error getting token: {e}")
        return None

async def main():
    print("🚀 Iniciando Seed de Preferências...")
    
    async with httpx.AsyncClient() as client:
        # 1. Auth
        token = await get_token(client)
        if not token:
            print("❌ Falha na autenticação. Verifique se o servidor está rodando.")
            return

        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Autenticado!")
        
        # 2. Update Preferences
        print("\n📝 Atualizando preferências...")
        res = await client.put(
            f"{API_URL}/users/me/preferences", 
            headers=headers, 
            json=PREFERENCES_PAYLOAD
        )
        
        if res.status_code == 200:
            user = res.json()
            print("✅ Preferências atualizadas com sucesso!")
            
            print("\n📋 Dados retornados:")
            print(f"  - Job Titles: {user.get('job_titles')}")
            print(f"  - Work Models: {user.get('work_models')}")
            print(f"  - Benefits: {user.get('benefits')}")
            print(f"  - Relocation: {user.get('open_to_relocation')}")
            print(f"  - Complete: {user.get('is_preferences_complete')}")
            
            # Additional verification logic could go here
        else:
            print(f"❌ Erro ao atualizar preferências: {res.status_code}")
            print(res.text)
        
    print("\n✨ Seed concluído!")

if __name__ == "__main__":
    asyncio.run(main())

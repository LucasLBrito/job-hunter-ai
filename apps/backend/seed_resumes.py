import asyncio
import httpx
import os
import shutil
from pathlib import Path

# Config
API_URL = "http://localhost:8001/api/v1"
TEST_USER = {
    "email": "resume_tester@example.com",
    "username": "resume_tester",
    "password": "password123",
    "full_name": "Resume Tester"
}

FAKE_RESUMES = [
    {
        "filename": "Curriculo_Backend_Python.txt",
        "description": "Foco em Python, Django e FastAPI",
        "content": "NOME: Joao Silva\nCARGO: Backend Developer\nSKILLS: Python, FastAPI, SQL, Docker\nEXPERIENCIA: 5 anos desenvolvendo APIs REST..."
    },
    {
        "filename": "Curriculo_Data_Engineer.txt",
        "description": "Experiencia em ETL e Big Data",
        "content": "NOME: Maria Souza\nCARGO: Data Engineer\nSKILLS: Python, Spark, Airflow, AWS\nEXPERIENCIA: Pipelines de dados para bancos financeiros..."
    },
    {
        "filename": "Curriculo_Fullstack.txt",
        "description": "React + Node.js e Python",
        "content": "NOME: Pedro Santos\nCARGO: Fullstack Dev\nSKILLS: React, TypeScript, Python, Postgres\nEXPERIENCIA: Dashboards administrativos..."
    }
]

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

async def create_fake_files():
    """Create local dummy files"""
    Path("temp_resumes").mkdir(exist_ok=True)
    files = []
    for r in FAKE_RESUMES:
        path = Path("temp_resumes") / r["filename"]
        with open(path, "w", encoding="utf-8") as f:
            f.write(r["content"])
        files.append((path, r["description"]))
    return files

async def main():
    print("🚀 Iniciando Seed de Currículos...")
    
    async with httpx.AsyncClient() as client:
        # 1. Auth
        token = await get_token(client)
        if not token:
            print("❌ Falha na autenticação. Verifique se o servidor está rodando.")
            return

        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Autenticado!")
        
        # 2. Create Files
        files = await create_fake_files()
        
        # 3. Upload List
        print(f"\n📤 Enviando {len(files)} currículos...")
        for file_path, desc in files:
            with open(file_path, "rb") as f:
                files_payload = {'file': (file_path.name, f, 'text/plain')}
                data_payload = {'description': desc}
                
                res = await client.post(
                    f"{API_URL}/resumes/", 
                    headers=headers, 
                    files=files_payload, 
                    data=data_payload
                )
                
                if res.status_code == 200:
                    data = res.json()
                    print(f"  ✅ Uploaded: {data['filename']} (ID: {data['id']})")
                else:
                    print(f"  ❌ Error uploading {file_path.name}: {res.text}")

        # 4. cleanup
        try:
            shutil.rmtree("temp_resumes")
            print("\n🧹 Arquivos temporários limpos.")
        except:
            pass

        # 5. List
        print("\n📋 Listando currículos no banco:")
        res_list = await client.get(f"{API_URL}/resumes/", headers=headers)
        if res_list.status_code == 200:
            items = res_list.json()
            for item in items:
                print(f"  - ID {item['id']}: {item['filename']} ({item['file_size']} bytes) - {item['file_path']}")
        
    print("\n✨ Seed concluído!")

if __name__ == "__main__":
    asyncio.run(main())

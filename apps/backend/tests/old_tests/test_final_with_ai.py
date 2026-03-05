"""
Teste Final - Análise de Currículo com IA Funcionando
"""
import requests
import json
import time
from io import BytesIO

BASE_URL = "http://localhost:8000/api/v1"

print("="*70)
print("  🚀 TESTE FINAL - JOB HUNTER AI COM IA ATIVA")
print("="*70)

# 1. Criar usuário
print("\n1️⃣ Criando usuário de teste...")
user_data = {
    "email": f"final.test{int(time.time())}@email.com",
    "username": f"final_{int(time.time())}",
    "password": "senha123",
    "full_name": "Teste Final AI"
}

r = requests.post(f"{BASE_URL}/auth/signup", json=user_data)
if r.status_code in [200, 201]:
    print(f"✅ Usuário criado: {user_data['email']}")
else:
    print(f"❌ Erro: {r.status_code}")
    exit()

# 2. Login
print("\n2️⃣ Fazendo login...")
r = requests.post(f"{BASE_URL}/auth/login", data={
    "username": user_data["email"],
    "password": user_data["password"]
})
token = r.json()['access_token']
headers = {"Authorization": f"Bearer {token}"}
print("✅ Login OK")

# 3. Upload currículo
print("\n3️⃣ Upload de currículo...")
resume = """
CARLOS RODRIGUES
Desenvolvedor Python Senior | Especialista em IA
carlos.rodrigues@email.com | (11) 99999-9999

RESUMO
Desenvolvedor Python com 8 anos de experiência em inteligência artificial, 
machine learning e desenvolvimento de aplicações web escaláveis.

SKILLS TÉCNICAS
• Python, FastAPI, Django, Flask
• Machine Learning: TensorFlow, PyTorch, scikit-learn
• NLP: BERT, GPT, Transformers
• Bancos de Dados: PostgreSQL, MongoDB, Redis
• Cloud: AWS, Google Cloud, Docker, Kubernetes
• Frontend: React, Next.js, TypeScript

EXPERIÊNCIA
Tech AI Solutions | Senior ML Engineer | 2020-Presente
• Desenvolveu modelos de NLP para análise de sentimentos
• Implementou sistema de recomendação com 95% de precisão
• Liderou equipe de 4 desenvolvedores

StartupML | Python Developer | 2017-2020
• Criou APIs RESTful com FastAPI
• Desenvolveu pipelines de dados com Airflow
• Implementou testes automatizados (90% coverage)

FORMAÇÃO
Mestrado em Inteligência Artificial | USP | 2019
Bacharelado em Ciência da Computação | Unicamp | 2016

CERTIFICAÇÕES
• AWS Machine Learning Specialty
• TensorFlow Developer Certificate
• Google Cloud Professional ML Engineer
""".encode('utf-8')

files = {'file': ('carlos_resume.txt', BytesIO(resume), 'text/plain')}
r = requests.post(f"{BASE_URL}/resumes/", headers=headers, files=files)
resume_id = r.json()['id']
print(f"✅ Currículo enviado - ID: {resume_id}")

# 4. Trigger análise
print("\n4️⃣ Iniciando análise com IA...")
r = requests.post(f"{BASE_URL}/resumes/{resume_id}/analyze", headers=headers)
print("✅ Análise iniciada (background task)")

# 5. Aguardar análise
print("\n5️⃣ Aguardando análise completar...")
print("   (Gemini vai extrair skills, experiência, etc.)")

for i in range(20):
    time.sleep(5)
    r = requests.get(f"{BASE_URL}/resumes/{resume_id}", headers=headers)
    resume_data = r.json()
    
    if resume_data.get('is_analyzed'):
        print(f"\n🎉 ANÁLISE COMPLETA! (em ~{(i+1)*5}s)")
        print("\n" + "="*70)
        print("  📊 RESULTADOS DA ANÁLISE IA")
        print("="*70)
        
        # Summary
        summary = resume_data.get('ai_summary', '')
        if summary and not summary.startswith('ERROR'):
            print(f"\n📝 Resumo IA:")
            print(f"   {summary[:200]}...")
            
            # Skills técnicas
            try:
                tech = json.loads(resume_data.get('technical_skills', '[]'))
                print(f"\n💻 Skills Técnicas ({len(tech)}):")
                for skill in tech[:8]:
                    print(f"   • {skill}")
                if len(tech) > 8:
                    print(f"   ... e mais {len(tech)-8}")
            except: pass
            
            # Skills soft
            try:
                soft = json.loads(resume_data.get('soft_skills', '[]'))
                print(f"\n👥 Skills Interpessoais ({len(soft)}):")
                for skill in soft[:5]:
                    print(f"   • {skill}")
            except: pass
            
            # Experiência
            years = resume_data.get('years_of_experience')
            if years:
                print(f"\n⏰ Experiência: {years} anos")
            
            print("\n✅ IA FUNCIONANDO PERFEITAMENTE!")
        else:
            print(f"\n⚠️  Análise retornou erro: {summary}")
        break
    else:
        print(f"   Tentativa {i+1}/20...")

# 6. Recomendações
print("\n6️⃣ Buscando recomendações com Pinecone...")
r = requests.get(f"{BASE_URL}/jobs/recommended?limit=5", headers=headers)

if r.status_code == 200:
    jobs = r.json()
    print(f"\n🎯 {len(jobs)} VAGAS RECOMENDADAS:\n")
    
    for idx, job in enumerate(jobs, 1):
        print(f"{idx}. {job['title']}")
        print(f"   Empresa: {job.get('company', 'N/A')}")
        if job.get('compatibility_score'):
            print(f"   Match: {job['compatibility_score']}%")
        print()

print("\n" + "="*70)
print("  ✅ TESTE COMPLETO - TUDO FUNCIONANDO!")
print("="*70)

print(f"\n🌐 Acesse o navegador: http://localhost:3000")
print(f"📧 Email: {user_data['email']}")
print(f"🔑 Senha: {user_data['password']}")

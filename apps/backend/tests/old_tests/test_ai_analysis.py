"""
Test Resume Analysis with OpenAI (if available) or Gemini
"""
import requests
import json
import time
from io import BytesIO

BASE_URL = "http://localhost:8000/api/v1"

def test_ai_analysis():
    print("="*70)
    print("  TESTE: Análise de Currículo com IA")
    print("="*70)
    
    # Step 1: Create user
    print("\n1. Criando usuário...")
    signup_data = {
        "email": f"ai.test{int(time.time())}@email.com",
        "username": f"ai_test_{int(time.time())}",
        "password": "senha123",
        "full_name": "AI Test User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    if response.status_code in [200, 201]:
        print(f"✅ Usuário criado: {signup_data['email']}")
    else:
        print(f"❌ Erro ao criar usuário: {response.status_code}")
        return
    
    # Step 2: Login
    print("\n2. Fazendo login...")
    login_data = {
        "username": signup_data["email"],
        "password": signup_data["password"]
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ Erro no login: {response.status_code}")
        return
    
    token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Login realizado")
    
    # Step 3: Upload resume
    print("\n3. Fazendo upload de currículo...")
    
    resume_content = """
MARIA SANTOS
Desenvolvedora Full Stack Senior
Email: maria.santos@email.com | Tel: (11) 99999-9999

RESUMO PROFISSIONAL
Desenvolvedora Full Stack com 7 anos de experiência em desenvolvimento de aplicações web
escaláveis. Especialista em Python, React e arquitetura de microsserviços. Experiência 
comprovada em liderar equipes e entregar projetos de alta complexidade.

HABILIDADES TÉCNICAS
• Linguagens: Python, JavaScript, TypeScript, Java, SQL
• Frontend: React.js, Next.js, Redux, Material-UI, Tailwind CSS
• Backend: FastAPI, Django, Flask, Spring Boot
• Bancos de Dados: PostgreSQL, MongoDB, Redis, MySQL
• Cloud & DevOps: AWS (EC2, S3, Lambda), Docker, Kubernetes, CI/CD
• Ferramentas: Git, GitHub Actions, Jenkins, Terraform
• IA & ML: TensorFlow, PyTorch, scikit-learn, OpenAI API

HABILIDADES INTERPESSOAIS
• Liderança de equipe
• Comunicação efetiva
• Resolução de problemas
• Trabalho em equipe
• Mentoria

EXPERIÊNCIA PROFISSIONAL

Tech Solutions Inc. | São Paulo, SP
Senior Full Stack Developer | Mar 2020 - Presente
• Liderou desenvolvimento de plataforma SaaS com 100k+ usuários ativos
• Implementou arquitetura de microsserviços reduzindo latência em 40%
• Mentorou equipe de 5 desenvolvedores júniors
• Tecnologias: Python, React, AWS, PostgreSQL, Docker

StartupXYZ | São Paulo, SP
Full Stack Developer | Jan 2018 - Fev 2020
• Desenvolveu APIs RESTful usando FastAPI e Django
• Criou interfaces responsivas com React e Redux
• Implementou testes automatizados aumentando cobertura para 85%
• Tecnologias: Python, JavaScript, MongoDB, Redis

WebDev Corp | São Paulo, SP  
Desenvolvedora Junior | Jun 2016 - Dez 2017
• Desenvolveu features para aplicação web de e-commerce
• Trabalhou com stack MERN (MongoDB, Express, React, Node.js)
• Participou de code reviews e pair programming

FORMAÇÃO ACADÊMICA
Bacharel em Ciência da Computação | Universidade de São Paulo (USP) | 2016
Pós-graduação em Inteligência Artificial | Unicamp | 2019

CERTIFICAÇÕES
• AWS Certified Solutions Architect - Associate
• Google Cloud Professional Developer
• Python Institute PCAP Certified

IDIOMAS
• Português (Nativo)
• Inglês (Fluente)
• Espanhol (Intermediário)

PROJETOS
• Sistema de recomendação usando IA (Python, TensorFlow)
• Plataforma de análise de dados em tempo real (React, FastAPI, WebSockets)
• API de integração com múltiplos serviços de pagamento
""".encode('utf-8')
    
    files = {
        'file': ('maria_santos_resume.txt', BytesIO(resume_content), 'text/plain')
    }
    
    response = requests.post(
        f"{BASE_URL}/resumes/",
        headers=headers,
        files=files
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ Erro no upload: {response.status_code}")
        print(response.text)
        return
    
    resume_data = response.json()
    resume_id = resume_data['id']
    print(f"✅ Currículo enviado - ID: {resume_id}")
    
    # Step 4: Trigger analysis
    print("\n4. Iniciando análise com IA...")
    response = requests.post(
        f"{BASE_URL}/resumes/{resume_id}/analyze",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ Análise iniciada (processamento em background)")
    else:
        print(f"⚠️  Status: {response.status_code}")
    
    # Step 5: Wait for analysis
    print("\n5. Aguardando análise completar...")
    print("   (Isso vai levar uns 30-60 segundos se a API Key estiver configurada)")
    
    for attempt in range(20):  # 100 seconds max
        time.sleep(5)
        
        response = requests.get(
            f"{BASE_URL}/resumes/{resume_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            resume = response.json()
            
            if resume.get('is_analyzed'):
                print(f"\n✅ ANÁLISE COMPLETA! (levou ~{(attempt + 1) * 5} segundos)")
                print("\n" + "="*70)
                print("  RESULTADOS DA ANÁLISE")
                print("="*70)
                
                # Show summary
                summary = resume.get('ai_summary', '')
                if summary and not summary.startswith('ERROR:'):
                    print(f"\n📝 Resumo:")
                    print(f"   {summary[:300]}...")
                    
                    # Show skills
                    try:
                        tech_skills = json.loads(resume.get('technical_skills', '[]'))
                        print(f"\n💻 Habilidades Técnicas ({len(tech_skills)}):")
                        for skill in tech_skills[:10]:
                            print(f"   • {skill}")
                        if len(tech_skills) > 10:
                            print(f"   ... e mais {len(tech_skills) - 10} habilidades")
                    except:
                        pass
                    
                    try:
                        soft_skills = json.loads(resume.get('soft_skills', '[]'))
                        print(f"\n👥 Habilidades Interpessoais ({len(soft_skills)}):")
                        for skill in soft_skills[:5]:
                            print(f"   • {skill}")
                    except:
                        pass
                    
                    # Show experience
                    years = resume.get('years_of_experience')
                    if years:
                        print(f"\n⏰ Anos de Experiência: {years}")
                    
                    print(f"\n✅ TESTE PASSOU! A IA está funcionando corretamente!")
                    
                else:
                    print(f"\n❌ Análise falhou: {summary}")
                    print("\n⚠️  POSSÍVEIS CAUSAS:")
                    print("   1. GEMINI_API_KEY não configurada no .env")
                    print("   2. Chave API inválida ou com quota excedida")
                    print("   3. Problema de conexão com Google AI")
                    print("\n💡 DICA: Você forneceu uma chave OPENAI, mas o sistema usa GEMINI")
                    print("   Para obter uma chave Gemini:")
                    print("   1. Acesse: https://makersuite.google.com/app/apikey")
                    print("   2. Crie uma chave API gratuita")
                    print("   3. Adicione ao .env: GEMINI_API_KEY=sua_chave_aqui")
                
                return
                
            elif resume.get('ai_summary', '').startswith('ERROR:'):
                print(f"\n❌ Análise falhou: {resume.get('ai_summary')}")
                print("\nResumo do currículo ainda disponível para teste:")
                print(f"   Arquivo: {resume.get('filename')}")
                print(f"   Tamanho: {resume.get('file_size')} bytes")
                return
            else:
                print(f"   Tentativa {attempt + 1}/20: Ainda analisando...")
        else:
            print(f"   Erro ao verificar status: {response.status_code}")
    
    print("\n⏱️  Timeout: A análise está levando mais tempo que o esperado")
    print("   O processo pode estar rodando. Verifique no dashboard web!")

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     TESTE DE ANÁLISE DE CURRÍCULO COM IA                     ║
║                                                              ║
║  Sistema: Gemini AI (Google)                                 ║
║  Nota: Você forneceu chave OpenAI, mas usamos Gemini        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    test_ai_analysis()

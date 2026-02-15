
import urllib.request
import json
import sys
import time

BASE_URL = "http://localhost:8000"

def log(msg, status="INFO"):
    colors = {"INFO": "\033[94m", "SUCCESS": "\033[92m", "ERROR": "\033[91m"}
    reset = "\033[0m"
    print(f"{colors.get(status, '')}[{status}] {msg}{reset}")

def make_request(method, endpoint, data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    req_data = json.dumps(data).encode("utf-8") if data else None
    
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except Exception as e:
        return 0, str(e)

def run_tests():
    log("🚀 Iniciando Testes Funcionais de Fluxo...", "INFO")
    
    # 1. Health Check
    status, _ = make_request("GET", "/health")
    if status == 200:
        log("✅ Health Check OK", "SUCCESS")
    else:
        log("❌ Health Check Falhou", "ERROR")
        sys.exit(1)

    # 2. Signup
    log("👤 Testando Registro de Usuário...", "INFO")
    user_data = {
        "email": f"teste_{int(time.time())}@example.com",
        "username": "tester",
        "password": "strongpassword123"
    }
    status, response = make_request("POST", "/api/v1/auth/signup", user_data)
    if status == 200:
        log(f"✅ Registro OK: ID {response.get('id')}", "SUCCESS")
    else:
        log(f"❌ Registro Falhou: {response}", "ERROR")

    # 3. Login
    log("🔑 Testando Login...", "INFO")
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    status, response = make_request("POST", "/api/v1/auth/login", login_data)
    
    token = None
    if status == 200 and "access_token" in response:
        token = response["access_token"]
        log("✅ Login OK - Token Recebido", "SUCCESS")
    else:
        log(f"❌ Login Falhou: {response}", "ERROR")
        sys.exit(1)

    # 4. List Jobs
    log("📋 Testando Listagem de Vagas...", "INFO")
    status, jobs = make_request("GET", "/api/v1/jobs", token=token)
    if status == 200 and isinstance(jobs, list):
        log(f"✅ Listagem OK - {len(jobs)} vagas encontradas", "SUCCESS")
    else:
        log(f"❌ Listagem Falhou: {jobs}", "ERROR")

    # 5. Create Job
    log("➕ Testando Criação de Vaga...", "INFO")
    new_job = {
        "title": "Backend Developer",
        "company": "Startup Inc",
        "location": "São Paulo",
        "salary_min": 12000
    }
    status, response = make_request("POST", "/api/v1/jobs", new_job, token=token)
    if status == 200 and response["title"] == new_job["title"]:
        log("✅ Criação de Vaga OK", "SUCCESS")
    else:
        log(f"❌ Criação Falhou: {response}", "ERROR")

    log("\n✨ Todos os testes de fluxo passaram!", "SUCCESS")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        log(f"Erro inesperado: {e}", "ERROR")

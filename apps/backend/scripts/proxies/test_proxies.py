import asyncio
import httpx
import time
from typing import List

# Arquivo contendo um proxy por linha: ip:porta ou http://ip:porta
PROXY_FILE = "proxies.txt"

# Plataformas onde testaremos se o Proxy funciona sem tomar block 403 / timeout
TEST_URLS = {
    "Catho": "https://www.catho.com.br/",
    "Gupy": "https://portal.api.gupy.io/api/v1/jobs?limit=1",
    "Adzuna": "https://www.adzuna.com.br/"
}

async def check_proxy(proxy_url: str, timeout: int = 10) -> dict:
    """Testa um único proxy contra várias plataformas"""
    
    proxy_str = proxy_url.strip()
    if not proxy_str.startswith("http"):
        proxy_str = f"http://{proxy_str}"
        
    print(f"\n🔄 Testando: {proxy_str}")
    
    results = {"proxy": proxy_str, "status": "✅ Ativo", "details": {}}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/json"
    }

    async with httpx.AsyncClient(proxies=proxy_str, timeout=timeout, verify=False) as client:
        for name, url in TEST_URLS.items():
            start_time = time.time()
            try:
                # Usa HEAD ou GET dependendo da plataforma
                resp = await client.get(url, headers=headers)
                elapsed = time.time() - start_time
                
                if resp.status_code in [200, 201, 202, 301, 302, 404]:
                    print(f"  [OK] {name} ({resp.status_code}) - {elapsed:.2f}s")
                    results["details"][name] = f"OK ({elapsed:.2f}s)"
                else:
                    print(f"  [BLOCKED] {name} ({resp.status_code}) - {elapsed:.2f}s")
                    results["details"][name] = f"Blocked ({resp.status_code})"
                    results["status"] = "⚠️ Parcial"
            except Exception as e:
                elapsed = time.time() - start_time
                error_msg = str(e)[:40] or type(e).__name__
                print(f"  [ERROR] {name} - {error_msg} ({elapsed:.2f}s)")
                results["details"][name] = f"Error ({error_msg})"
                results["status"] = "❌ Falhou"

    # Se falhou em tudo, marcamos logo como off
    if all(v.startswith("Error") for v in results["details"].values()):
        results["status"] = "❌ Morto"
        
    return results


async def main():
    print("=" * 50)
    print("🚀 JOB HUNTER AI - PROXY TESTER")
    print("=" * 50)
    
    try:
        with open(PROXY_FILE, "r") as f:
            proxies = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        print(f"❌ Arquivo '{PROXY_FILE}' não encontrado!")
        print(f"Exemplo de formato esperado no '{PROXY_FILE}':\n185.199.229.156:7492\nhttp://user:pass@12.34.56.78:8080")
        
        # Cria arquivo de exemplo vazio para que o usuário saiba preencher
        with open(PROXY_FILE, "w") as f:
            f.write("# Cole seus proxies aqui (um por linha)\n")
            f.write("# Format:\n# 12.34.56.78:8080\n")
        return

    if not proxies:
        print(f"⚠️ O arquivo '{PROXY_FILE}' está vazio. Adicione os proxies lá!")
        return

    print(f"📋 Encontrados {len(proxies)} proxies para testar.")
    
    # Executa de forma paralela mas controlada (batch de 5)
    batch_size = 5
    successful_proxies = []
    
    for i in range(0, len(proxies), batch_size):
        batch = proxies[i:i+batch_size]
        tasks = [check_proxy(p) for p in batch]
        
        # Espera todos do lote completarem
        batch_results = await asyncio.gather(*tasks)
        
        for r in batch_results:
            if "Ativo" in r["status"] or "Parcial" in r["status"]:
                successful_proxies.append(r["proxy"])
                
    print("\n" + "=" * 50)
    print(f"🎯 RESUMO: {len(successful_proxies)}/{len(proxies)} vivos.")
    print("=" * 50)
    
    if successful_proxies:
        print("💡 Proxies funcionando (Salve-os no seu .env.vps / .env.local):")
        for p in successful_proxies:
            print(p)
            
if __name__ == "__main__":
    asyncio.run(main())

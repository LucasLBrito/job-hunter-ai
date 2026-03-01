import sys
import os
import asyncio
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.scrapers.gupy_scraper import GupyScraper
from app.services.scrapers.remote_scrapers import RemotarScraper
from app.services.job_ai_analyzer import JobAIAnalyzer

async def main():
    print("=== INICIANDO TESTE DOS SCRAPERS ===")
    
    termo = "Python"
    print(f"Buscando vagas para: '{termo}'\\n")
    
    # Testar Gupy
    print("-> Testando GupyScraper...")
    gupy = GupyScraper()
    vagas_gupy = await gupy.search_jobs(termo, limit=3)
    print(f"Gupy retornou {len(vagas_gupy)} vagas")
    for v in vagas_gupy:
        print(f"  - {v.title} @ {v.company} ({v.location})")
        
    print("\\n-> Testando RemotarScraper...")
    remotar = RemotarScraper()
    vagas_remotar = await remotar.search_jobs(termo, limit=3)
    print(f"Remotar retornou {len(vagas_remotar)} vagas")
    for v in vagas_remotar:
        print(f"  - {v.title} @ {v.company} ({v.location})")
        
    todas_vagas = vagas_gupy + vagas_remotar
    
    if not todas_vagas:
        print("Nenhuma vaga encontrada para testar a IA.")
        return

    print("\\n=== INICIANDO TESTE DA IA ===")
    
    perfil_teste = {
        "cargo_desejado": "Desenvolvedor Python",
        "nivel": "Pleno",
        "modalidade": "Remoto",
        "salario_minimo": 5000,
        "skills_principais": ["Python", "FastAPI", "SQL"],
        "skills_bonus": ["AWS", "Docker"],
        "nao_quero": ["PHP", "Ruby"],
        "localizacao_preferida": "Brasil",
    }
    
    analyzer = JobAIAnalyzer(perfil=perfil_teste)
    print("Client OpenAI configurado:", "SIM" if analyzer.client else "NÃO (sem API Key)")
    
    if analyzer.client:
        print("\\nEnviando vagas para análise (GPT-4o-mini)...")
        vagas_dicts = [
            {
                "title": v.title,
                "company": v.company,
                "location": v.location,
                "is_remote": v.is_remote,
                "description": v.description or "",
                "source_platform": v.source_platform,
                "url": v.url
            }
            for v in todas_vagas[:3] # Analisar apenas as 3 primeiras para ir rápido
        ]
        
        resultados = await analyzer.analisar_lote(vagas_dicts, max_vagas=3)
        print(f"\\nAnalisadas {len(resultados)} vagas:")
        for res in resultados:
            a = res.get("analise_ia", {})
            print(f"\\nVaga: {res['title']} @ {res['company']}")
            print(f"Recomendação: {a.get('recomendacao')} (Pontuação: {a.get('pontuacao')})")
            print(f"Motivo: {a.get('motivo')}")
    else:
        print("\\nPulando análise via IA porque OPENAI_API_KEY não foi detectada no ambiente.")

if __name__ == "__main__":
    asyncio.run(main())

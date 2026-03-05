import asyncio
import logging
from app.services.scrapers.adzuna_scraper import AdzunaScraper
from app.services.scrapers.catho_scraper import CathoScraper
from app.services.scrapers.gupy_scraper import GupyScraper
from app.services.scrapers.jobspy_scraper import JobSpyScraper
from app.services.scrapers.remoteok import RemoteOKScraper
from app.services.scrapers.ti_brasil_scrapers import (
    ProgramaThorScraper, GeekHunterScraper, CoodeshScraper, APInfoScraper
)
from app.services.scrapers.remote_scrapers import RemotarScraper, WeWorkRemotelyScraper
from app.services.scrapers.freelance_scrapers import WorkanaScraper, FreelaScraper

logging.basicConfig(level=logging.ERROR, format='%(name)s - %(levelname)s - %(message)s')

async def main():
    scrapers = [
        JobSpyScraper(),
        RemoteOKScraper(),
        AdzunaScraper(),
        CathoScraper(),
        GupyScraper(),
        ProgramaThorScraper(),
        GeekHunterScraper(),
        CoodeshScraper(),
        APInfoScraper(),
        RemotarScraper(),
        WeWorkRemotelyScraper(),
        WorkanaScraper(),
        FreelaScraper()
    ]
    
    query = "Desenvolvedor"
    limit = 5
    
    with open("resultados_scrapers.txt", "w", encoding="utf-8") as f:
        f.write("====================================\n")
        f.write("TESTANDO SCRAPERS INDIVIDUALMENTE\n")
        f.write("====================================\n\n")
        
        for scraper in scrapers:
            name = type(scraper).__name__
            f.write(f"[{name}] Buscando...\n")
            try:
                results = await scraper.search_jobs(query=query, limit=limit)
                f.write(f"[{name}] Encontrou {len(results)} vagas.\n")
                for i, r in enumerate(results[:2]):
                    f.write(f"    - {r.title} | {r.company} | {r.url}\n")
            except Exception as e:
                f.write(f"[{name}] ERRO: {e}\n")
            f.write("------------------------------------\n\n")

if __name__ == "__main__":
    asyncio.run(main())

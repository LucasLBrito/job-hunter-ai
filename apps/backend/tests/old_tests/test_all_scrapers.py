import asyncio
import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.scrapers.adzuna_scraper import AdzunaScraper
from app.services.scrapers.catho_scraper import CathoScraper
from app.services.scrapers.freelance_scrapers import WorkanaScraper, FreelaScraper
from app.services.scrapers.gupy_scraper import GupyScraper
from app.services.scrapers.jobspy_scraper import JobSpyScraper
from app.services.scrapers.remote_scrapers import RemotarScraper, WeWorkRemotelyScraper
from app.services.scrapers.remoteok import RemoteOKScraper
from app.services.scrapers.ti_brasil_scrapers import ProgramaThorScraper, GeekHunterScraper, CoodeshScraper, APInfoScraper
from app.services.scrapers.vagas_scraper import VagasScraper

scrapers = [
    AdzunaScraper(),
    CathoScraper(),
    WorkanaScraper(),
    FreelaScraper(),
    GupyScraper(),
    JobSpyScraper(),
    RemotarScraper(),
    WeWorkRemotelyScraper(),
    RemoteOKScraper(),
    ProgramaThorScraper(),
    GeekHunterScraper(),
    CoodeshScraper(),
    APInfoScraper(),
    VagasScraper()
]

query = "Python"

async def test_scrapers():
    print(f"=========================================")
    print(f"Testing Scrapers with query: '{query}'")
    print(f"=========================================\n")
    
    results_summary = []
    
    for scraper in scrapers:
        name = type(scraper).__name__
        print(f"Testing {name}...")
        try:
            # We timeout at 15s so the test doesn't hang forever on broken scrapers
            result = await asyncio.wait_for(scraper.search_jobs(query, limit=2), timeout=15)
            print(f"  [OK] Found {len(result)} jobs.")
            results_summary.append((name, "OK", len(result)))
            if result:
                print(f"  Sample: {result[0].title} at {result[0].company}")
        except asyncio.TimeoutError:
            print(f"  [TIMEOUT] Scraper timed out.")
            results_summary.append((name, "TIMEOUT", 0))
        except Exception as e:
            print(f"  [ERROR] {type(e).__name__}: {str(e)[:100]}")
            results_summary.append((name, "ERROR", 0))
        print()
        
    print(f"=========================================")
    print(f"SUMMARY")
    print(f"=========================================")
    for name, status, count in results_summary:
        icon = "✅" if status == "OK" and count > 0 else ("⚠️ " if status == "OK" and count == 0 else "❌")
        print(f"{icon} {name.ljust(25)} {status.ljust(8)} {count} jobs")

if __name__ == "__main__":
    asyncio.run(test_scrapers())

import asyncio
import logging
import sys

# Add app to path if needed or just run from backend root
from app.services.scrapers.remoteok import RemoteOKScraper
from app.services.scrapers.jobspy_scraper import JobSpyScraper
from app.services.scrapers.adzuna_scraper import AdzunaScraper
from app.services.scrapers.vagas_scraper import VagasScraper

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def test_scrapers():
    query = "python"
    limit = 2
    
    scrapers = [
        ("RemoteOK", RemoteOKScraper()),
        ("Adzuna", AdzunaScraper()),
        ("Vagas", VagasScraper()),
        ("JobSpy", JobSpyScraper())
    ]
    
    for name, scraper in scrapers:
        print(f"\n--- Testing {name} ---")
        try:
            results = await scraper.search_jobs(query, limit=limit)
            print(f"SUCCESS: {name} returned {len(results)} results")
            for r in results:
                print(f"  - {r.title} at {r.company}")
        except Exception as e:
            print(f"FAILED: {name} failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_scrapers())

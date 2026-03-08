import asyncio
import logging
from app.services.jobsearch.cathoscraper import CathoScraper
from app.services.jobsearch.vagas import VagasScraper
from app.services.jobsearch.remoteok import RemoteOKScraper
from app.services.jobsearch.remotar import RemotarScraper
from app.services.jobsearch.geekhunter import GeekHunterScraper
from app.services.jobsearch.coodesh import CoodeshScraper
from app.services.jobsearch.freela import FreelaScraper
from app.services.jobsearch.workana import WorkanaScraper
from app.services.jobsearch.apinfo import APInfoScraper
from app.services.jobsearch.programathor import ProgramaThorScraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

async def main():
    scrapers = [
        CathoScraper(),
        VagasScraper(),
        RemoteOKScraper(),
        RemotarScraper(),
        GeekHunterScraper(),
        CoodeshScraper(),
        FreelaScraper(),
        WorkanaScraper(),
        APInfoScraper(),
        ProgramaThorScraper()
    ]
    query = "python"
    for s in scrapers:
        try:
            print(f"--- Testing {s.PLATFORM_NAME} ---")
            jobs = await s.search_jobs(query, limit=5)
            print(f"Found {len(jobs)} jobs")
            for j in jobs[:2]:
                print(f"  - {j.title[:50]} at {j.company[:30]} ({j.url})")
        except Exception as e:
            print(f"Error in {s.PLATFORM_NAME}: {e}")
        print("\n")

if __name__ == "__main__":
    asyncio.run(main())

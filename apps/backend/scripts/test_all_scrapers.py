"""Test all configured scrapers to verify they respond."""
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import all scrapers from the new jobsearch module
from app.services.jobsearch.remoteok import RemoteOKScraper
from app.services.jobsearch.adzuna import AdzunaScraper
from app.services.jobsearch.vagas import VagasScraper
from app.services.jobsearch.gupy import GupyScraper
from app.services.jobsearch.programathor import ProgramaThorScraper
from app.services.jobsearch.geekhunter import GeekHunterScraper
from app.services.jobsearch.coodesh import CoodeshScraper
from app.services.jobsearch.apinfo import APInfoScraper
from app.services.jobsearch.remotar import RemotarScraper
from app.services.jobsearch.weworkremotely import WeWorkRemotelyScraper
from app.services.jobsearch.workana import WorkanaScraper
from app.services.jobsearch.freela import FreelaScraper
from app.services.jobsearch.cathoscraper import CathoScraper
from app.services.jobsearch.jobspy_scraper import JobSpyScraper

async def test_scrapers():
    query = "Backend"
    limit = 2

    scrapers = [
        RemoteOKScraper(), AdzunaScraper(), VagasScraper(), GupyScraper(),
        ProgramaThorScraper(), GeekHunterScraper(), CoodeshScraper(), APInfoScraper(),
        RemotarScraper(), WeWorkRemotelyScraper(), WorkanaScraper(), FreelaScraper(),
        CathoScraper(), JobSpyScraper(),
    ]

    print("\n" + "="*50)
    print("BATCH TESTING ALL CONFIGURED SCRAPERS (JOBSEARCH)")
    print("="*50 + "\n")
    print(f"Total scrapers: {len(scrapers)}\n")

    for scraper in scrapers:
        name = type(scraper).__name__
        print(f"Testing: {name} ... ", end="", flush=True)

        try:
            results = await scraper.search_jobs(query, limit)
            if results and len(results) > 0:
                print(f"OK! Found {len(results)} jobs.")
            else:
                print(f"Empty response.")
        except Exception as e:
            error_msg = str(e)[:60]
            print(f"ERROR: {error_msg}")

    print("\n" + "="*50)
    print("TESTS FINISHED")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(test_scrapers())

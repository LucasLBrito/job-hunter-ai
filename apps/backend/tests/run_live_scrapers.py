import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from app.services.jobsearch import apinfo, remotar, weworkremotely, jobspy_scraper, cathoscraper, vagas, gupy

async def test_scraper(scraper_class, query="python", limit=2):
    print(f"\\n--- Testing {scraper_class.__name__} ---")
    try:
        scraper = scraper_class()
        jobs = await scraper.search_jobs(query, limit)
        print(f"✅ Success: {len(jobs)} jobs found.")
        if jobs:
            print(f"Sample: {jobs[0].title} at {jobs[0].company}")
    except Exception as e:
        print(f"❌ Failed: {e}")

async def main():
    print("Starting tests for all active scrapers...")
    scrapers = [
        apinfo.APInfoScraper,
        remotar.RemotarScraper,
        weworkremotely.WeWorkRemotelyScraper,
        jobspy_scraper.JobSpyScraper,
        vagas.VagasScraper,
        cathoscraper.CathoScraper,
        gupy.GupyScraper,
    ]
    
    for scraper_class in scrapers:
        await test_scraper(scraper_class)

if __name__ == "__main__":
    asyncio.run(main())

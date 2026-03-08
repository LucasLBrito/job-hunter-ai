import asyncio
import os
import sys
import logging
from pprint import pprint

# Ensure the app module is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Load environmental variables from .env
from dotenv import load_dotenv
load_dotenv()

from app.services.jobsearch.tavily_scraper import TavilyScraper
from app.services.jobsearch.firecrawl_job_scraper import FirecrawlJobScraper
from app.services.jobsearch.exa_scraper import ExaScraper

logging.basicConfig(level=logging.INFO)

async def test_scraper(scraper_class, query="python developer"):
    print(f"\n--- Testing {scraper_class.__name__} ---")
    scraper = scraper_class()
    if not scraper.api_key:
        print(f"WARNING: Missing API Key for {scraper_class.__name__}. Skipping.")
        return
        
    try:
        jobs = await scraper.search_jobs(query, limit=2)
        print(f"SUCCESS: Found {len(jobs)} jobs")
        for j in jobs:
            print(f"  - {j.title} at {j.company} ({j.source_platform})")
            print(f"    URL: {j.url}")
            print(f"    Desc preview: {j.description[:50]}...")
    except Exception as e:
        print(f"ERROR: testing {scraper_class.__name__}: {e}")

async def main():
    print("Checking for required API Keys in .env...")
    print(f"TAVILY_API_KEY: {'[SET]' if os.getenv('TAVILY_API_KEY') else '[MISSING]'}")
    print(f"FIRECRAWL_API_KEY: {'[SET]' if os.getenv('FIRECRAWL_API_KEY') else '[MISSING]'}")
    print(f"EXA_API_KEY: {'[SET]' if os.getenv('EXA_API_KEY') else '[MISSING]'}")
    
    await test_scraper(TavilyScraper, "python developer")
    await test_scraper(FirecrawlJobScraper, "python developer")
    await test_scraper(ExaScraper, "python developer")

if __name__ == "__main__":
    asyncio.run(main())

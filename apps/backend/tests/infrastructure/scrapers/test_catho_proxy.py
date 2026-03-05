import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.services.scrapers.catho_scraper import CathoScraper
from app.infrastructure.proxies.manager import proxy_manager

async def main():
    print("Testing Catho Scraper with ProxyManager injected...")
    scraper = CathoScraper()
    
    # Pre-fetch proxies to test
    await proxy_manager.fetch_proxies()
    
    jobs = await scraper.search_jobs("Python", limit=5)
    
    if jobs:
        print(f"✅ Success! Found {len(jobs)} jobs on Catho.")
        for j in jobs:
            print(f"- {j.title} | {j.company} | {j.url}")
    else:
        print("❌ Failed: Catho returned 0 jobs. Either no working proxy was found, or the proxy itself was blocked by Catho.")

if __name__ == "__main__":
    asyncio.run(main())

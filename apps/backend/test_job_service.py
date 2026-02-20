import asyncio
import sys
import logging

# Ensure app is importable
sys.path.append(".")

from app.database import AsyncSessionLocal
from app.services.job_service import JobService

logging.basicConfig(level=logging.INFO)

async def main():
    try:
        async with AsyncSessionLocal() as db:
            js = JobService(db)
            print("JobService initialized with scrapers:", js.scrapers)
            
            # Run the search
            print("Running search...")
            jobs = await js.search_and_save_jobs("o", limit=10)
            print(f"Success! Found {len(jobs)} jobs.")
    except Exception as e:
        print("ERROR:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import logging
import sys

from app.database import AsyncSessionLocal
from app.services.job_service import JobService

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def test_job_service():
    query = "python"
    limit = 5
    
    print(f"\n--- Testing JobService.search_and_save_jobs with query '{query}' ---")
    async with AsyncSessionLocal() as db:
        service = JobService(db)
        
        try:
            new_jobs = await service.search_and_save_jobs(query=query, limit=limit)
            print(f"✅ Success! Saved {len(new_jobs)} new jobs to the database.")
            for job in new_jobs:
                print(f"  - [{job.source_platform}] {job.title} at {job.company} (ID: {job.id})")
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_job_service())

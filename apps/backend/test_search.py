import asyncio
import logging
from app.database import AsyncSessionLocal
from app.services.job_service import JobService
from app.core.config import settings

logging.basicConfig(level=logging.INFO)

async def test_search():
    print("Testing JobService.search_and_save_jobs")
    async with AsyncSessionLocal() as db:
        try:
            job_service = JobService(db)
            jobs = await job_service.search_and_save_jobs(query="python", limit=2)
            print(f"Success! Found {len(jobs)} jobs.")
        except Exception as e:
            print(f"FAILED WITH EXCEPTION: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_search())

import asyncio
from app.database import AsyncSessionLocal
from app.services.job_service import JobService

async def test_search():
    async with AsyncSessionLocal() as db:
        service = JobService(db)
        print("Starting search...")
        results = await service.search_and_save_jobs("python", limit=2)
        print(f"Found {len(results)} jobs")
        for j in results:
            print(f"- {j.title} at {j.company}")

if __name__ == "__main__":
    asyncio.run(test_search())

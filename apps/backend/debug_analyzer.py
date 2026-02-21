import asyncio
import logging
from app.database import AsyncSessionLocal
from app.services.analyzer import ResumeAnalyzer

logging.basicConfig(level=logging.INFO)

async def test():
    async with AsyncSessionLocal() as session:
        analyzer = ResumeAnalyzer()
        await analyzer._do_analysis(2, session)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(test())

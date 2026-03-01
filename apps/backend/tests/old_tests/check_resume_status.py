import asyncio
import sys
import os

sys.path.append(os.getcwd())

from app.database import AsyncSessionLocal
from app import crud

async def check(resume_id):
    async with AsyncSessionLocal() as db:
        resume = await crud.resume.get(db, resume_id)
        if resume:
            print(f"Resume {resume.id}:")
            print(f"  Analyzed: {resume.is_analyzed}")
            print(f"  Summary: {resume.ai_summary[:100]}..." if resume.ai_summary else "  Summary: None")
            print(f"  Skills: {resume.technical_skills[:100]}..." if resume.technical_skills else "  Skills: None")
        else:
            print(f"Resume {resume_id} not found")

if __name__ == "__main__":
    asyncio.run(check(9))

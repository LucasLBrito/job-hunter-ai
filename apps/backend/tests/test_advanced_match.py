import asyncio
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.job import Job
from app.api.v1.jobs.recommendations import get_recommended_jobs

async def setup_mock_data(db):
    # Create Mock User
    import uuid
    uid = str(uuid.uuid4())[:8]
    mock_user = User(
        email=f"advanced_test_{uid}@example.com",
        username=f"advanced_tester_{uid}",
        hashed_password="test",
        job_titles=json.dumps(["Python Developer", "Django"]),
        technologies=json.dumps(["Python", "SQL", "Docker"])
    )
    db.add(mock_user)
    
    # Create Mock Jobs
    jobs_data = [
        {"title": "Python Developer Pleno", "company": "Tech ABC", "description": "Vaga para desenvolvedor python com experiência em Docker e SQL."},
        {"title": "Frontend React", "company": "Tech XYZ", "description": "Vaga Frontend com Javascript e React."},
        {"title": "DevOps Engineer", "company": "Cloud Inc", "description": "Focado em AWS, kubernetes e Terraform."},
        {"title": "Django Backend Dev", "company": "Software Co", "description": "Procuramos alguem com forte conhecimento em Python e Django."},
    ]
    
    for i, jd in enumerate(jobs_data):
        j = Job(
            external_id=f"test_advanced_{uid}_{i}",
            title=jd['title'],
            company=jd['company'],
            description=jd['description'],
            source_platform="test",
            source_url="http://test.com"
        )
        db.add(j)
        
    await db.commit()
    await db.refresh(mock_user)
    return mock_user, uid

async def cleanup_mock_data(db, user_id, uid):
    from sqlalchemy import delete
    await db.execute(delete(User).where(User.id == user_id))
    # Note: job instances won't be easily deletable by query without raw delete, doing simple cleanup
    await db.execute(delete(Job).where(Job.external_id.like(f"test_advanced_{uid}_%")))
    await db.commit()

async def main():
    async with AsyncSessionLocal() as db:
        print("Setting up mock data...")
        user, uid = await setup_mock_data(db)
        
        try:
            print("\n--- Running Advanced Match Algorithm ---")
            print(f"User Prefs: Titles: {user.job_titles} | Techs: {user.technologies}\n")
            
            results = await get_recommended_jobs(db=db, limit=10, current_user=user)
            
            print(f"Found {len(results)} recommended jobs. Ranked by score:\n")
            for r in results:
                print(f"[{r.compatibility_score:.2f}] {r.title} at {r.company}")
                
        finally:
            print("\nCleaning up mock data...")
            await cleanup_mock_data(db, user.id, uid)

if __name__ == "__main__":
    asyncio.run(main())

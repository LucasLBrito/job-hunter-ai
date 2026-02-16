from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any

from app.api import deps
from app.models.user import User
from app.models.job import Job
from app.models.resume import Resume
from app.models.application import Application

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def get_stats(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Get usage statistics for the dashboard.
    """
    # 1. Total Jobs Scraped (Global)
    result_jobs = await db.execute(select(func.count(Job.id)))
    total_jobs = result_jobs.scalar() or 0
    
    # 2. Resumes Analyzed (Global/User?) - Let's do User's resumes
    result_resumes = await db.execute(
        select(func.count(Resume.id)).where(
            Resume.user_id == current_user.id,
            Resume.is_analyzed == True
        )
    )
    resumes_analyzed = result_resumes.scalar() or 0
    
    # 3. Applications (User)
    result_apps = await db.execute(
        select(func.count(Application.id)).where(Application.user_id == current_user.id)
    )
    total_applications = result_apps.scalar() or 0
    
    # 4. Jobs marked as favorite (User)
    # Assuming Job model tracks favorites via relation or simple logic?
    # Job model has is_favorite but it's per job.
    # If jobs are shared, is_favorite usage might be tricky (should be a UserJob association).
    # Checking Job model... 
    # In Phase 2, Job had `is_favorite` boolean. But if multiple users use the same DB...
    # For MVP single-user focus, this is fine.
    # Future: UserJob table.
    
    # Let's count current_user's applications as "Applied"
    
    return {
        "total_jobs_available": total_jobs,
        "my_resumes_analyzed": resumes_analyzed,
        "my_applications": total_applications
    }

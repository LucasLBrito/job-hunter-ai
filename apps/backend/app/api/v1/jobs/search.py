from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.api import deps

router = APIRouter()

@router.post("/search", response_model=List[schemas.JobResponse])
async def search_jobs(
    *,
    db: AsyncSession = Depends(deps.get_db),
    query: str = "",
    limit: int = 100,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search jobs directly from the PostgreSQL database (Serving Layer).
    No background scraping is triggered here anymore.
    """
    from sqlalchemy import select
    from app.models.job import Job as JobModel
    
    stmt = select(JobModel)
    
    if query and query.strip():
        search_term = f"%{query.strip()}%"
        stmt = stmt.where(
            (JobModel.title.ilike(search_term)) | 
            (JobModel.description.ilike(search_term)) |
            (JobModel.company.ilike(search_term))
        )
        
    # Order by newest first
    stmt = stmt.order_by(JobModel.id.desc()).limit(limit)
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    
    return jobs

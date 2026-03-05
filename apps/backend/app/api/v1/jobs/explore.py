"""
Jobs Explore Endpoint - Browse all raw jobs in the database.
Provides full-text search, platform filtering, remote filtering, and pagination.
No authentication required for the explore view (public job board).
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_, case, Integer, cast

from app import schemas
from app.api import deps
from app.models.job import Job as JobModel

router = APIRouter()


@router.get("/explore")
async def explore_jobs(
    db: AsyncSession = Depends(deps.get_db),
    q: Optional[str] = Query(None, description="Search text (title, company, description)"),
    platform: Optional[str] = Query(None, description="Filter by source platform"),
    remote_only: bool = Query(False, description="Only show remote jobs"),
    limit: int = Query(30, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> Any:
    """
    Explore all raw jobs in the database with search and filters.
    Returns jobs sorted by relevance (if search query) or newest first.
    Also returns aggregated stats (total count, platform breakdown).
    """
    # Base query
    base_q = select(JobModel).where(JobModel.is_active == True)

    # Platform filter
    if platform and platform.strip():
        base_q = base_q.where(JobModel.source_platform == platform.strip())

    # Remote filter
    if remote_only:
        base_q = base_q.where(JobModel.is_remote == True)

    # Text search with relevance scoring
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        base_q = base_q.where(
            or_(
                JobModel.title.ilike(search_term),
                JobModel.company.ilike(search_term),
                JobModel.description.ilike(search_term),
                JobModel.location.ilike(search_term),
            )
        )
        # Order by title match first (more relevant), then by id desc
        relevance = case(
            (JobModel.title.ilike(search_term), 3),
            (JobModel.company.ilike(search_term), 2),
            else_=1
        ).label("relevance")
        # Add relevance column to query for ordering
        jobs_q = base_q.add_columns(relevance).order_by(desc(relevance), JobModel.id.desc())
    else:
        jobs_q = base_q.order_by(JobModel.id.desc())

    # Get total count (before pagination)
    count_q = select(func.count()).select_from(base_q.subquery())
    total_result = await db.execute(count_q)
    total_count = total_result.scalar() or 0

    # Apply pagination
    jobs_q = jobs_q.offset(offset).limit(limit)
    result = await db.execute(jobs_q)

    # Extract Job objects (handling both plain scalars and tuples from add_columns)
    if q and q.strip():
        jobs = [row[0] for row in result]
    else:
        jobs = result.scalars().all()

    # Get platform breakdown (for filter badges)
    platform_q = (
        select(
            JobModel.source_platform,
            func.count(JobModel.id).label("count")
        )
        .where(JobModel.is_active == True)
        .group_by(JobModel.source_platform)
        .order_by(desc("count"))
    )
    platform_result = await db.execute(platform_q)
    platforms = [{"name": row[0], "count": row[1]} for row in platform_result]

    # Get remote count
    remote_q = select(func.count(JobModel.id)).where(
        JobModel.is_active == True, JobModel.is_remote == True
    )
    remote_result = await db.execute(remote_q)
    remote_count = remote_result.scalar() or 0

    # Serialize jobs using the schema
    serialized_jobs = []
    for job in jobs:
        try:
            job_data = schemas.JobResponse.model_validate(job)
            serialized_jobs.append(job_data.model_dump(mode="json"))
        except Exception:
            # Fallback: manual serialization
            serialized_jobs.append({
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "description": (job.description or "")[:300],
                "location": job.location,
                "is_remote": job.is_remote,
                "source_url": job.source_url,
                "source_platform": job.source_platform,
                "external_id": job.external_id,
                "is_active": job.is_active,
                "is_favorite": job.is_favorite or False,
                "is_hidden": job.is_hidden or False,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "salary_currency": job.salary_currency,
                "compatibility_score": job.compatibility_score,
                "posted_date": str(job.posted_date) if job.posted_date else None,
                "created_at": str(job.created_at) if job.created_at else None,
            })

    return {
        "jobs": serialized_jobs,
        "total": total_count,
        "offset": offset,
        "limit": limit,
        "has_more": offset + limit < total_count,
        "platforms": platforms,
        "remote_count": remote_count,
    }

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.JobResponse])
async def read_jobs(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve jobs.
    """
    jobs = await crud.job.get_multi(db, skip=skip, limit=limit)
    return jobs

@router.post("/", response_model=schemas.JobResponse)
async def create_job(
    *,
    db: AsyncSession = Depends(deps.get_db),
    job_in: schemas.JobCreate,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new job.
    """
    job = await crud.job.create(db=db, obj_in=job_in)
    return job

@router.get("/{job_id}", response_model=schemas.JobResponse)
async def read_job(
    *,
    db: AsyncSession = Depends(deps.get_db),
    job_id: int,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get job by ID.
    """
    job = await crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/{job_id}", response_model=schemas.JobResponse)
async def update_job(
    *,
    db: AsyncSession = Depends(deps.get_db),
    job_id: int,
    job_in: schemas.JobUpdate,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a job.
    """
    job = await crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job = await crud.job.update(db=db, db_obj=job, obj_in=job_in)
    return job

@router.delete("/{job_id}", response_model=schemas.JobResponse)
async def delete_job(
    *,
    db: AsyncSession = Depends(deps.get_db),
    job_id: int,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a job.
    """
    job = await crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job = await crud.job.remove(db=db, id=job_id)
    return job

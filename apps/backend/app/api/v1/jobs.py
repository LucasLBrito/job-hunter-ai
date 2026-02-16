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

@router.post("/search", response_model=List[schemas.JobResponse])
async def search_jobs(
    *,
    db: AsyncSession = Depends(deps.get_db),
    query: str,
    limit: int = 20,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search for jobs using active scrapers.
    """
    from app.services.job_service import JobService
    job_service = JobService(db)
    new_jobs = await job_service.search_and_save_jobs(query=query, limit=limit)
    return new_jobs

@router.post("/{job_id}/analyze", response_model=schemas.JobResponse)
async def analyze_job_fit(
    *,
    db: AsyncSession = Depends(deps.get_db),
    job_id: int,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Analyze job fit against user's default resume.
    """
    # 1. Get Job
    job = await crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # 2. Get User's Resume (Default match)
    # Assuming user has a resume. For now, fetch the most recent one.
    resumes = await crud.resume.get_multi_by_owner(db, owner_id=current_user.id, limit=1)
    if not resumes:
        raise HTTPException(status_code=400, detail="No resume found for analysis.")
    resume = resumes[0]
    
    # Extract text from resume if not already (assuming content is text or has been extracted)
    # resume.content is the raw file, resume.extracted_data might be JSON.
    # We need raw text. If Phase 3 extraction saved text, good.
    # Let's assume user.user_preferences or we just pass the JSON summary for now which is text-ish.
    # Ideally we'd store raw_text. Checking User/Resume model...
    # Resume model has 'content' (binary). 'extracted_data' (JSON).
    # Let's stringify extracted_data for the prompt.
    
    import json
    resume_text = json.dumps(resume.extracted_data, indent=2)
    
    # 3. Call Matcher Service
    from app.services.analysis.matcher import MatcherService
    # Use user's key if available, else system key (or error)
    api_key = current_user.gemini_api_key  # Or settings.GEMINI_API_KEY
    if not api_key:
         # Fallback to system key
         from app.core.config import settings
         api_key = settings.GEMINI_API_KEY
    
    if not api_key:
        raise HTTPException(status_code=400, detail="Gemini API Key not found.")

    matcher = MatcherService(api_key=api_key)
    analysis = await matcher.analyze_fit(resume_text, job.description or job.title)
    
    # 4. Update Job
    # Check Schema for JobUpdate. We need to allow arbitrary dict or add fields to JobUpdate.
    # Models have pros/cons as Text (JSON).
    
    # Update DB fields directly or via CRUD if supported.
    # CRUD update usually takes schema. Let's update via object dictionary pattern.
    
    job.compatibility_score = analysis.get("match_score")
    job.pros = json.dumps(analysis.get("pros", []))
    job.cons = json.dumps(analysis.get("cons", []))
    job.analyzed_date = func.now()
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Parse back JSON for response (Pydantic expects list, DB has string)
    # SQLAlchemy model field is Text, but Pydantic is List.
    # We need to manually ensure conversion or rely on Pydantic's from_attributes parsing if configured.
    # But 'job.pros' is a string now. JobResponse expects List.
    # We might need to override the response object or fix Model to be JSON type (SQLite supports JSON but stored as Text often).
    # Let's ensure response is correct.
    
    # Temporary fix: Manually assign parsed lists to the job object instance before returning (it won't save to DB, just for response).
    job.pros = analysis.get("pros", [])
    job.cons = analysis.get("cons", [])
    
    return job

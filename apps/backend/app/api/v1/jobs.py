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

# IMPORTANT: Static routes must come BEFORE dynamic path parameter routes
@router.get("/recommended", response_model=List[schemas.JobResponse])
async def get_recommended_jobs(
    db: AsyncSession = Depends(deps.get_db),
    limit: int = 10,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get AI-recommended jobs based on user's analyzed resume AND preferences.
    Returns jobs sorted by composite compatibility score.
    """
    from sqlalchemy import select, desc
    from app.models.resume import Resume
    import json
    
    # Get user's most recent analyzed resume
    stmt = select(Resume).where(
        Resume.user_id == current_user.id,
        Resume.is_analyzed == True
    ).order_by(desc(Resume.updated_at)).limit(1)
    
    result = await db.execute(stmt)
    resume = result.scalars().first()
    
    # Get all active jobs
    all_jobs = await crud.job.get_multi(db, skip=0, limit=200)
    
    if not all_jobs:
        return []
    
    # Extract resume skills
    resume_skills = []
    if resume:
        try:
            resume_skills = json.loads(resume.technical_skills) if resume.technical_skills else []
        except:
            resume_skills = []
    
    # Extract user preferences
    user_techs = []
    user_work_models = []
    user_job_titles = []
    user_locations = []
    user_industries = []
    user_salary_min = None
    user_salary_max = None
    user_seniority = None
    
    try:
        user_techs = json.loads(current_user.technologies) if current_user.technologies else []
    except:
        pass
    try:
        user_work_models = json.loads(current_user.work_models) if current_user.work_models else []
    except:
        pass
    try:
        user_job_titles = json.loads(current_user.job_titles) if current_user.job_titles else []
    except:
        pass
    try:
        user_locations = json.loads(current_user.preferred_locations) if current_user.preferred_locations else []
    except:
        pass
    try:
        user_industries = json.loads(current_user.industries) if current_user.industries else []
    except:
        pass
    
    user_salary_min = current_user.salary_min
    user_salary_max = current_user.salary_max
    user_seniority = current_user.seniority_level
    
    # Combine resume skills + user-selected technologies (unique)
    all_skills = list(set([s.lower() for s in resume_skills] + [s.lower() for s in user_techs]))
    
    # Score each job
    scored_jobs = []
    for job in all_jobs:
        score = 0.0
        max_score = 0.0
        
        job_text = f"{job.title} {job.description or ''} {job.requirements or ''}".lower()
        job_title_lower = job.title.lower() if job.title else ""
        
        # 1. Technology/Skill Match (weight: 35)
        max_score += 35
        if all_skills:
            match_count = sum(1 for skill in all_skills if skill in job_text)
            score += (match_count / max(len(all_skills), 1)) * 35
        
        # 2. Job Title Match (weight: 25)
        max_score += 25
        if user_job_titles:
            title_match = any(t.lower() in job_title_lower for t in user_job_titles)
            if title_match:
                score += 25
            else:
                # Partial match
                partial = sum(1 for t in user_job_titles if any(word in job_title_lower for word in t.lower().split()))
                score += (partial / len(user_job_titles)) * 15
        
        # 3. Work Model Match (weight: 15)
        max_score += 15
        if user_work_models:
            user_wants_remote = any(m.lower() in ["remote", "remoto"] for m in user_work_models)
            user_wants_hybrid = any(m.lower() in ["hybrid", "híbrido", "hibrido"] for m in user_work_models)
            
            if user_wants_remote and job.is_remote:
                score += 15
            elif user_wants_hybrid and ("hybrid" in job_text or "híbrido" in job_text):
                score += 15
            elif not user_wants_remote and not job.is_remote:
                score += 10  # User prefers in-person and job is in-person
        
        # 4. Salary Match (weight: 10)
        max_score += 10
        if user_salary_min and job.salary_max:
            if job.salary_max >= user_salary_min:
                score += 10
            elif job.salary_max >= user_salary_min * 0.8:
                score += 5  # Within 80% of desired minimum
        elif not user_salary_min:
            score += 5  # No preference, partial score
        
        # 5. Location Match (weight: 10)
        max_score += 10
        if user_locations and job.location:
            loc_match = any(loc.lower() in job.location.lower() for loc in user_locations)
            if loc_match:
                score += 10
        elif not user_locations:
            score += 5  # No preference
        
        # 6. Seniority Match (weight: 5)
        max_score += 5
        if user_seniority:
            seniority_lower = user_seniority.lower()
            if seniority_lower in job_title_lower or seniority_lower in job_text:
                score += 5
        
        # Calculate percentage
        final_score = min(int((score / max_score) * 100), 95) if max_score > 0 else 0
        job.compatibility_score = final_score
        scored_jobs.append(job)
    
    # Sort by score descending
    scored_jobs.sort(key=lambda x: x.compatibility_score or 0, reverse=True)
    
    return scored_jobs[:limit]


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
    import json
    from sqlalchemy.sql import func
    
    job = await crud.job.get(db=db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    resumes = await crud.resume.get_multi_by_owner(db, user_id=current_user.id, limit=1)
    if not resumes:
        raise HTTPException(status_code=400, detail="No resume found for analysis.")
    resume = resumes[0]
    
    resume_text = json.dumps(resume.structured_data, indent=2) if resume.structured_data else resume.raw_text or ""
    
    from app.services.analysis.matcher import MatcherService
    api_key = current_user.gemini_api_key
    if not api_key:
         from app.core.config import settings
         api_key = settings.GEMINI_API_KEY
    
    if not api_key:
        raise HTTPException(status_code=400, detail="Gemini API Key not found.")

    matcher = MatcherService(api_key=api_key)
    analysis = await matcher.analyze_fit(resume_text, job.description or job.title)
    
    job.compatibility_score = analysis.get("match_score")
    job.pros = json.dumps(analysis.get("pros", []))
    job.cons = json.dumps(analysis.get("cons", []))
    job.analyzed_date = func.now()
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    job.pros = analysis.get("pros", [])
    job.cons = analysis.get("cons", [])
    
    return job

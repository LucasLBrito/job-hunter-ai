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
    Get AI-recommended jobs based on user's analyzed resume.
    Returns jobs sorted by compatibility score.
    """
    from sqlalchemy import select, desc
    from app.models.resume import Resume
    
    # Get user's most recent analyzed resume
    stmt = select(Resume).where(
        Resume.user_id == current_user.id,
        Resume.is_analyzed == True
    ).order_by(desc(Resume.updated_at)).limit(1)
    
    result = await db.execute(stmt)
    resume = result.scalars().first()
    
    if not resume:
        # No analyzed resume - return top jobs
        jobs = await crud.job.get_multi(db, skip=0, limit=limit)
        return jobs
    
    # Try Pinecone Semantic Search first
    try:
        from app.services.pinecone_service import PineconeService
        from app.services.embedding_service import EmbeddingService
        import json
        
        pinecone_service = PineconeService()
        if pinecone_service.index:
            # 1. Try to get existing vector
            vector = pinecone_service.get_resume_vector(resume.id)
            
            # 2. If not found, generate it (on the fly recovery)
            if not vector:
                # Parse JSON fields from Resume model
                # Resume stores: ai_summary (text), technical_skills (JSON string), soft_skills (JSON string)
                try:
                    tech_skills = json.loads(resume.technical_skills) if resume.technical_skills else []
                    soft_skills = json.loads(resume.soft_skills) if resume.soft_skills else []
                    summary = resume.ai_summary or ""
                    
                    embed_text = f"{summary} {' '.join(tech_skills)} {' '.join(soft_skills)}"
                    
                    if embed_text.strip():
                        embedding_service = EmbeddingService()
                        if embedding_service.api_key:
                            vector = await embedding_service.get_embedding(embed_text)
                except Exception as parse_err:
                    print(f"Error parsing resume data: {parse_err}")
            
            # 3. Search
            if vector:
                search_results = pinecone_service.search_jobs(query_embedding=vector, top_k=limit)
                
                if search_results:
                    # Get jobs from DB preserving order
                    job_ids = [res['id'] for res in search_results]
                    
                    # Fetch jobs (this might not preserve order depending on DB impl, so we re-sort)
                    # For simplicity, let's fetch matching jobs and manual sort
                    # Or use a WHERE IN clause.
                    from app.models.job import Job
                    stmt = select(Job).where(Job.id.in_(job_ids))
                    db_res = await db.execute(stmt)
                    jobs_map = {job.id: job for job in db_res.scalars().all()}
                    
                    ordered_jobs = []
                    for res in search_results:
                        job = jobs_map.get(res['id'])
                        if job:
                            job.compatibility_score = int(res['score'] * 100) # Pinecone score is 0-1 (cosine)
                            ordered_jobs.append(job)
                            
                    return ordered_jobs
    except Exception as e:
        # Log error and fall back to keyword matching
        import traceback
        print(f"Pinecone search failed: {e}")
        print(traceback.format_exc())
        pass

    # Fallback: Keyword Matching (Old Logic)
    all_jobs = await crud.job.get_multi(db, skip=0, limit=100)
    
    if not all_jobs:
        return []
    
    # Extract skills from resume for matching
    try:
        import json
        resume_skills = json.loads(resume.technical_skills) if resume.technical_skills else []
        if not resume_skills:
            resume_skills = json.loads(resume.soft_skills) if resume.soft_skills else []
    except:
        resume_skills = []
         
    # Score each job
    scored_jobs = []
    for job in all_jobs:
        job_text = f"{job.title} {job.description or ''}".lower()
        
        # Calculate keyword match score
        match_count = sum(1 for skill in resume_skills if str(skill).lower() in job_text)
        score = (match_count / max(len(resume_skills), 1)) * 100 if resume_skills else 0
        
        # Set compatibility score
        job.compatibility_score = min(int(score), 95)
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


@router.get("/recommended", response_model=List[schemas.JobResponse])
async def get_recommended_jobs(
    db: AsyncSession = Depends(deps.get_db),
    limit: int = 10,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get AI-recommended jobs based on user's analyzed resume.
    Returns jobs sorted by compatibility score.
    """
    from sqlalchemy import select, desc
    from app.models.resume import Resume
    
    # Get user's most recent analyzed resume
    stmt = select(Resume).where(
        Resume.user_id == current_user.id,
        Resume.is_analyzed == True
    ).order_by(desc(Resume.updated_at)).limit(1)
    
    result = await db.execute(stmt)
    resume = result.scalars().first()
    
    if not resume:
        # No analyzed resume - return top jobs
        jobs = await crud.job.get_multi(db, skip=0, limit=limit)
        return jobs
    
    # Try Pinecone Semantic Search first
    try:
        from app.services.pinecone_service import PineconeService
        from app.services.embedding_service import EmbeddingService
        import json
        
        pinecone_service = PineconeService()
        if pinecone_service.index:
            # 1. Try to get existing vector
            vector = pinecone_service.get_resume_vector(resume.id)
            
            # 2. If not found, generate it (on the fly recovery)
            if not vector:
                # Parse JSON fields from Resume model
                # Resume stores: ai_summary (text), technical_skills (JSON string), soft_skills (JSON string)
                try:
                    tech_skills = json.loads(resume.technical_skills) if resume.technical_skills else []
                    soft_skills = json.loads(resume.soft_skills) if resume.soft_skills else []
                    summary = resume.ai_summary or ""
                    
                    embed_text = f"{summary} {' '.join(tech_skills)} {' '.join(soft_skills)}"
                    
                    if embed_text.strip():
                        embedding_service = EmbeddingService()
                        if embedding_service.api_key:
                            vector = await embedding_service.get_embedding(embed_text)
                except Exception as parse_err:
                    print(f"Error parsing resume data: {parse_err}")
            
            # 3. Search
            if vector:
                search_results = pinecone_service.search_jobs(query_embedding=vector, top_k=limit)
                
                if search_results:
                    # Get jobs from DB preserving order
                    job_ids = [res['id'] for res in search_results]
                    
                    # Fetch jobs (this might not preserve order depending on DB impl, so we re-sort)
                    # For simplicity, let's fetch matching jobs and manual sort
                    # Or use a WHERE IN clause.
                    from app.models.job import Job
                    stmt = select(Job).where(Job.id.in_(job_ids))
                    db_res = await db.execute(stmt)
                    jobs_map = {job.id: job for job in db_res.scalars().all()}
                    
                    ordered_jobs = []
                    for res in search_results:
                        job = jobs_map.get(res['id'])
                        if job:
                            job.compatibility_score = int(res['score'] * 100) # Pinecone score is 0-1 (cosine)
                            ordered_jobs.append(job)
                            
                    return ordered_jobs
    except Exception as e:
        # Log error and fall back to keyword matching
        import traceback
        print(f"Pinecone search failed: {e}")
        print(traceback.format_exc())
        pass

    # Fallback: Keyword Matching (Old Logic)
    all_jobs = await crud.job.get_multi(db, skip=0, limit=100)
    
    if not all_jobs:
        return []
    
    # Extract skills from resume for matching
    try:
        import json
        resume_skills = json.loads(resume.technical_skills) if resume.technical_skills else []
        if not resume_skills:
            resume_skills = json.loads(resume.soft_skills) if resume.soft_skills else []
    except:
        resume_skills = []
         
    # Score each job
    scored_jobs = []
    for job in all_jobs:
        job_text = f"{job.title} {job.description or ''}".lower()
        
        # Calculate keyword match score
        match_count = sum(1 for skill in resume_skills if str(skill).lower() in job_text)
        score = (match_count / max(len(resume_skills), 1)) * 100 if resume_skills else 0
        
        # Set compatibility score
        job.compatibility_score = min(int(score), 95)
        scored_jobs.append(job)
    
    # Sort by score descending
    scored_jobs.sort(key=lambda x: x.compatibility_score or 0, reverse=True)
    
    return scored_jobs[:limit]

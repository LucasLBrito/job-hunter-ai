from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
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
    query: str = None,
    limit: int = 10,
    offset: int = 0,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get top recommended jobs for the current user.
    Queries the user_jobs table for pre-computed per-user scores.
    Falls back to in-memory scoring if no scored entries exist yet.
    """
    from sqlalchemy import select, desc
    from app.models.user_job import UserJob
    from app.models.job import Job as JobModel

    print(f"DEBUG: get_recommended_jobs for user {current_user.id}")

    # --- Primary path: read from user_jobs table ---
    # We join with UserJob so we can order by the custom compatibility score
    query_builder = select(JobModel).join(UserJob, UserJob.job_id == JobModel.id).where(UserJob.user_id == current_user.id)
    
    if query and query.strip():
        search_term = f"%{query.strip()}%"
        # We use ilike to make it case-insensitive
        query_builder = query_builder.where(
            (JobModel.title.ilike(search_term)) | 
            (JobModel.description.ilike(search_term)) |
            (JobModel.company.ilike(search_term))
        )
        
    stmt = (
        query_builder
        .order_by(UserJob.compatibility_score.desc().nullslast(), JobModel.id.desc())
        .offset(offset)
        # Fetch a bit more than limit in case we need to dedup same title/company combos downstream
        .limit(limit * 3)
    )
    result = await db.execute(stmt)
    db_scored_jobs = result.scalars().all()

    if db_scored_jobs:
        # Attach the per-user score to the job object for the response
        score_map_stmt = select(UserJob).where(UserJob.user_id == current_user.id)
        score_map_result = await db.execute(score_map_stmt)
        score_map = {uj.job_id: uj.compatibility_score for uj in score_map_result.scalars().all()}

        for j in db_scored_jobs:
            j.compatibility_score = score_map.get(j.id)

        # Dedup by title+company
        unique_jobs = []
        seen = set()
        for j in db_scored_jobs:
            key = f"{str(j.title or '').lower()}|{str(j.company or '').lower()}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(j)

        return unique_jobs[:limit]

    # --- Fallback: in-memory scoring (no persisted scores yet) ---
    from app.models.resume import Resume
    from app.crud import job as crud_job
    from app.services.scoring_service import ScoringService

    stmt_resume = select(Resume).where(
        Resume.user_id == current_user.id,
        Resume.is_analyzed == True
    ).order_by(desc(Resume.analyzed_at)).limit(1)
    resume_result = await db.execute(stmt_resume)
    resume = resume_result.scalars().first()
    
    # Fetch chunk from jobs table directly
    fallback_query = select(JobModel)
    if query and query.strip():
        search_term = f"%{query.strip()}%"
        fallback_query = fallback_query.where(
            (JobModel.title.ilike(search_term)) | 
            (JobModel.description.ilike(search_term)) |
            (JobModel.company.ilike(search_term))
        )
    # Fetch a massive chunk from jobs table directly to have a good pool for scoring
    fallback_query = fallback_query.order_by(JobModel.id.desc()).offset(offset).limit(limit * 50)
    fallback_result = await db.execute(fallback_query)
    all_jobs = fallback_result.scalars().all()
    
    if not all_jobs:
        return []

    preferences = ScoringService.extract_skills_and_preferences(current_user, resume)
    for job in all_jobs:
        job.compatibility_score = ScoringService.calculate_score(job, preferences)

    # Sort descending by score
    all_jobs.sort(key=lambda x: (x.compatibility_score or 0, float(x.id)), reverse=True)

    unique_jobs = []
    seen = set()
    for j in all_jobs:
        key = f"{str(j.title or '').lower()}|{str(j.company or '').lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(j)
            
            if len(unique_jobs) >= limit:
                break

    return unique_jobs


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


@router.post("/analyze-batch")
async def analyze_jobs_batch(
    *,
    db: AsyncSession = Depends(deps.get_db),
    query: str,
    max_vagas: int = 20,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Fluxo completo: busca vagas em TODOS os scrapers configurados E analisa com IA
    (GPT-4o-mini) em uma única chamada.
    
    Retorna lista de vagas enriquecidas com campo `analise_ia` contendo:
    - `pontuacao`: 0-100
    - `recomendacao`: APLICAR | CONSIDERAR | IGNORAR
    - `motivo`: explicação em 1-2 frases
    - `pontos_positivos`: lista de pontos fortes
    - `pontos_negativos`: lista de pontos fracos
    - `salario_estimado`: valor estimado ou 'Não informado'
    
    O perfil de análise é construído automaticamente a partir das preferências do usuário.
    """
    import json

    from app.services.job_service import JobService
    from app.services.job_ai_analyzer import JobAIAnalyzer

    # 1. Buscar vagas com os scrapers
    job_service = JobService(db)
    saved_jobs = await job_service.search_and_save_jobs(query=query, limit=max_vagas * 2)

    if not saved_jobs:
        return {"total": 0, "analyzed": 0, "vagas": []}

    # 2. Converter Job models para dicts compatíveis com o analisador
    vagas_dicts = [
        {
            "title": j.title,
            "company": j.company,
            "location": j.location,
            "is_remote": j.is_remote,
            "description": j.description or "",
            "source_platform": j.source_platform,
            "source_url": j.source_url,
            "salary_min": j.salary_min,
            "salary_max": j.salary_max,
            "_job_id": j.id,
        }
        for j in saved_jobs
    ]

    # 3. Criar analisador com perfil do usuário
    analyzer = JobAIAnalyzer.from_user(current_user)
    vagas_analisadas = await analyzer.analisar_lote(vagas_dicts, max_vagas=max_vagas)

    # 4. Atualizar compatibility_score no banco para vagas analisadas com sucesso
    for vaga in vagas_analisadas:
        analise = vaga.get("analise_ia", {})
        job_id = vaga.get("_job_id")
        if job_id and analise.get("recomendacao") not in ("ERRO", None):
            job = await crud.job.get(db=db, id=job_id)
            if job:
                job.compatibility_score = analise.get("pontuacao", 0)
                db.add(job)
    await db.commit()

    return {
        "total_coletadas": len(saved_jobs),
        "total_analisadas": len(vagas_analisadas),
        "perfil_usado": analyzer.perfil,
        "vagas": vagas_analisadas,
    }


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

    # Extract structured user preferences to pass to the AI
    user_prefs = {
        "job_titles": current_user.job_titles,
        "seniority_level": current_user.seniority_level,
        "work_models": current_user.work_models,
        "employment_types": current_user.employment_types,
        "technologies": current_user.technologies,
        "preferred_locations": current_user.preferred_locations,
        "salary_min": current_user.salary_min,
        "salary_max": current_user.salary_max,
        "industries": current_user.industries,
        "benefits": current_user.benefits,
        "company_styles": current_user.company_styles,
    }
    
    # Clean up empty preferences to not distract the AI
    cleaned_prefs = {k: v for k, v in user_prefs.items() if v}

    matcher = MatcherService(api_key=api_key)
    analysis = await matcher.analyze_fit(
        resume_text=resume_text, 
        job_description=job.description or job.title,
        user_preferences=cleaned_prefs
    )
    
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

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps

router = APIRouter()

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

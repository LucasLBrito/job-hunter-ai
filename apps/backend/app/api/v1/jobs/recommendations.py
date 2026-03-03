from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.api import deps

router = APIRouter()

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

    # --- Fallback: Advanced SQL Match ---
    # We will build a dynamic scoring query based on user preferences.
    from sqlalchemy import case, cast, Integer
    import json
    
    # 1. Obter perfil do usuário
    titles = []
    techs = []
    if current_user.job_titles:
        try:
            titles = json.loads(current_user.job_titles)
        except:
            titles = [current_user.job_titles]
            
    if current_user.technologies:
        try:
            techs = json.loads(current_user.technologies)
        except:
            techs = [current_user.technologies]
            
    # Garantir que temos algo para buscar
    if not titles and not techs:
        titles = ["desenvolvedor", "developer", "engenheiro", "engineer"]
        
    search_terms = [t.lower() for t in titles + techs if t and t.strip()]
    
    dialect = db.bind.dialect.name if db.bind else "postgresql"
    
    if dialect == "postgresql" and search_terms:
        # PostgreSQL Advanced tsvector Match
        from sqlalchemy import func, text
        
        # Monta a tsquery: 'python | react | node'
        query_string = " | ".join([t.replace(" ", " & ") for t in search_terms])
        
        # tsvector column or cast
        ts_vector = func.to_tsvector('portuguese', func.coalesce(JobModel.title, '') + ' ' + func.coalesce(JobModel.description, ''))
        ts_query = func.to_tsquery('portuguese', query_string)
        
        rank = func.ts_rank(ts_vector, ts_query).label('match_score')
        
        fallback_query = select(JobModel, rank).where(
            ts_vector.op('@@')(ts_query)
        ).order_by(desc('match_score')).limit(limit)
        
    else:
        # SQLite / Generic Fallback: Match heuristic using multiple ilike score cases
        score_cases = []
        for term in search_terms:
            like_term = f"%{term}%"
            # 3 points for title match, 1 point for description match
            score_cases.append(
                case((JobModel.title.ilike(like_term), 3), else_=0) +
                case((JobModel.description.ilike(like_term), 1), else_=0)
            )
            
        if score_cases:
            combined_score = sum(score_cases).label('match_score')
            fallback_query = select(JobModel, combined_score).where(
                combined_score > 0
            ).order_by(desc('match_score')).limit(limit)
        else:
            fallback_query = select(JobModel, cast(0, Integer).label('match_score')).order_by(JobModel.id.desc()).limit(limit)

    result = await db.execute(fallback_query)
    
    unique_jobs = []
    seen = set()
    for row in result:
        # Result may contain (Job, match_score) tuple from our custom selects
        try:
            # SQLAlchemy Rows are tuple-like. We selected (JobModel, score)
            j = row[0]
            score = row[1] if len(row) > 1 else 0.0
            j.compatibility_score = float(score) if score else 0.0
        except Exception:
            # Fallback if somehow it's just the scalar or single object
            j = row
            j.compatibility_score = getattr(j, 'match_score', 0.0)

        key = f"{str(j.title or '').lower()}|{str(j.company or '').lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(j)
            
    return unique_jobs

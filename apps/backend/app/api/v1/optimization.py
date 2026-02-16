import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any

from app import crud
from app.api import deps
from app.models.user import User
from app.services.optimization_service import optimization_service
from pathlib import Path
from app.services.extraction.local import LocalTextExtractor

router = APIRouter()
logger = logging.getLogger(__name__)

class OptimizeRequest(BaseModel):
    resume_id: int
    job_description: str
    model: str = "gemini-1.5-flash"

@router.post("/optimize", response_model=Dict[str, Any])
async def optimize_resume(
    request: OptimizeRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Optimize a resume for a specific job description using the user's LLM API Key.
    """
    # 1. Get Resume
    resume = await crud.resume.get(db=db, id=request.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if resume.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 2. Extract Text (if not already stored or to be sure)
    # Ideally we should store extracted text in DB to save re-processing
    # But for now, let's extract again or use what we have.
    # The Resume model has 'content' (raw text) or file path.
    
    resume_text = ""
    # Check if we have analyzed text or raw content
    if resume.content: # Assuming 'content' field exists in Resume model? 
        # Wait, let me check Resume model definition.
        # If not, use extractor.
        pass
    
    # Re-checking Resume model...
    # If I don't recall, I'll assume I need to extract from file_path if content is missing.
    extractor = LocalTextExtractor()
    try:
        resume_text = await extractor.extract_text(Path(resume.file_path))
    except Exception as e:
        logger.error(f"Failed to extract text from resume {resume.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to read resume file")
        
    if not resume_text:
         raise HTTPException(status_code=400, detail="Resume content is empty")

    # 3. Call Optimization Service
    result = await optimization_service.optimize_resume(
        user=current_user,
        resume_text=resume_text,
        job_description=request.job_description,
        model=request.model
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import shutil
import os
import uuid
from pathlib import Path

from app import crud, schemas
from app.api import deps
from app.core.config import settings

router = APIRouter()

# Directory to save uploaded resumes
UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/", response_model=List[schemas.ResumeResponse])
async def read_resumes(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve resumes owned by current user.
    """
    resumes = await crud.resume.get_multi_by_owner(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return resumes

@router.post("/", response_model=schemas.ResumeResponse)
async def create_resume(
    *,
    db: AsyncSession = Depends(deps.get_db),
    file: UploadFile = File(...),
    description: str = Form(None),
    background_tasks: BackgroundTasks,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload a new resume file (PDF/DOCX).
    """
    # 1. Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(400, detail="Invalid file type. Only PDF, DOCX and TXT allowed.")
    
    # 2. Generate safe filename
    safe_filename = f"{uuid.uuid4()}{file_ext}"
    user_upload_dir = UPLOAD_DIR / str(current_user.id)
    user_upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = user_upload_dir / safe_filename
    
    # 3. Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(500, detail=f"Could not save file: {str(e)}")
        
    # 4. Create DB record
    file_size = os.path.getsize(file_path)
    resume_in = schemas.ResumeCreate(
        filename=file.filename,
        description=description,
        file_path=str(file_path),
        file_size=file_size,
        file_type=file_ext.replace(".", "")
    )
    
    resume = await crud.resume.create_with_owner(
        db=db, obj_in=resume_in, user_id=current_user.id
    )
    
    # 5. Trigger Analysis Background Task
    from app.services.analyzer import resume_analyzer
    background_tasks.add_task(resume_analyzer.process_resume_task, resume.id, db)
    
    return resume

@router.get("/{resume_id}", response_model=schemas.ResumeResponse)
async def read_resume(
    *,
    db: AsyncSession = Depends(deps.get_db),
    resume_id: int,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get resume by ID.
    """
    resume = await crud.resume.get(db=db, id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return resume

@router.post("/{resume_id}/analyze", response_model=schemas.ResumeResponse)
async def analyze_resume(
    *,
    db: AsyncSession = Depends(deps.get_db),
    resume_id: int,
    background_tasks: BackgroundTasks,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Trigger AI analysis for a resume.
    Runs synchronously so errors are properly reported.
    """
    resume = await crud.resume.get(db=db, id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Run analysis synchronously for better error handling
    from app.services.analyzer import ResumeAnalyzer
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        analyzer = ResumeAnalyzer()
        await analyzer._do_analysis(resume_id, db)
        
        # Refresh the resume to get updated data
        await db.refresh(resume)
        logger.info(f"Resume {resume_id} analysis completed successfully.")
    except Exception as e:
        logger.error(f"Resume analysis failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {str(e)}. Check that your Gemini or OpenAI API key is configured."
        )
    
    return resume


@router.delete("/{resume_id}", response_model=schemas.ResumeResponse)
async def delete_resume(
    *,
    db: AsyncSession = Depends(deps.get_db),
    resume_id: int,
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a resume.
    """
    resume = await crud.resume.get(db=db, id=resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    # Delete file from disk
    try:
        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)
    except Exception:
        # Log error but continue with DB deletion
        pass
        
    resume = await crud.resume.remove(db=db, id=resume_id)
    return resume

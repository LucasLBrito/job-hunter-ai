from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ResumeBase(BaseModel):
    """Base schema for Resume"""
    filename: Optional[str] = None
    description: Optional[str] = None

class ResumeCreate(ResumeBase):
    """Schema for creating a resume (metadata only, file handled separately)"""
    filename: str
    file_path: str
    file_size: int
    file_type: str

class ResumeUpdate(BaseModel):
    """Schema for updating resume analysis data"""
    # AI Analysis fields can be updated by the worker
    raw_text: Optional[str] = None
    structured_data: Optional[str] = None
    technical_skills: Optional[str] = None
    soft_skills: Optional[str] = None
    certifications: Optional[str] = None
    education: Optional[str] = None
    work_experience: Optional[str] = None
    ai_summary: Optional[str] = None
    years_of_experience: Optional[int] = None
    
    is_analyzed: Optional[bool] = None

class ResumeResponse(ResumeBase):
    """Schema for resume response"""
    id: int
    user_id: int
    filename: str
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    
    # Analysis Status
    is_active: bool
    is_analyzed: bool
    
    # Analysis Data (Optional, populated if analyzed)
    ai_summary: Optional[str] = None
    years_of_experience: Optional[int] = None
    technical_skills: Optional[str] = None
    
    uploaded_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

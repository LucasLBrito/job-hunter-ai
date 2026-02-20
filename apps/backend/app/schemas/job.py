from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum


class JobSource(str, Enum):
    """Job source platforms"""
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    REMOTEOK = "remoteok"
    GITHUB = "github"
    GLASSDOOR = "glassdoor"
    GOOGLE = "google"
    ZIPRECRUITER = "zip_recruiter"
    ADZUNA = "adzuna"
    MANUAL = "manual"


class JobBase(BaseModel):
    """Base job schema"""
    title: str = Field(..., max_length=255)
    company: str = Field(..., max_length=255)
    description: Optional[str] = None
    requirements: Optional[str] = None
    location: Optional[str] = None
    is_remote: bool = False
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "BRL"
    source_url: str


class JobCreate(JobBase):
    """Schema for creating a job"""
    external_id: str
    source_platform: JobSource


class JobUpdate(BaseModel):
    """Schema for updating a job"""
    title: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    requirements: Optional[str] = None
    location: Optional[str] = None
    is_remote: Optional[bool] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    
    is_favorite: Optional[bool] = None
    is_hidden: Optional[bool] = None


class JobAnalysis(BaseModel):
    """AI analysis of a job"""
    compatibility_score: Optional[float] = Field(None, ge=0, le=100)
    ai_summary: Optional[str] = None
    extracted_technologies: Optional[List[str]] = None
    culture_fit_score: Optional[float] = Field(None, ge=0, le=100)
    company_research: Optional[dict] = None
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None


class JobResponse(JobBase):
    """Schema for job response"""
    id: int
    external_id: str
    source_platform: str
    is_active: bool
    is_favorite: bool
    is_hidden: bool
    
    # AI Analysis
    compatibility_score: Optional[float] = None
    extracted_technologies: Optional[List[str]] = None
    culture_fit_score: Optional[float] = None
    
    # Smart Analysis
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    
    # Timestamps
    posted_date: Optional[datetime] = None
    found_date: datetime
    analyzed_date: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class JobFilters(BaseModel):
    """Filters for job search"""
    search: Optional[str] = None
    source_platform: Optional[JobSource] = None
    is_remote: Optional[bool] = None
    is_favorite: Optional[bool] = None
    is_hidden: Optional[bool] = None
    min_compatibility_score: Optional[float] = Field(None, ge=0, le=100)
    technologies: Optional[List[str]] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)

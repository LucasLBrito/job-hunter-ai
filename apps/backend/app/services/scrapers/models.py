from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

class ScrapedJob(BaseModel):
    """
    Standardized job data structure returned by all scrapers.
    """
    title: str
    company: str
    location: str
    is_remote: bool
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "BRL"
    description: str
    url: str
    external_id: str
    source_platform: str  # e.g., "remoteok", "linkedin"
    posted_at: Optional[datetime] = None
    
    # Optional metadata
    company_url: Optional[str] = None
    logo_url: Optional[str] = None
    technologies: List[str] = []

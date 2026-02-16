from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime


# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    whatsapp_number: Optional[str] = None


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user job preferences"""
    technologies: Optional[List[str]] = None
    job_titles: Optional[List[str]] = None
    work_models: Optional[List[str]] = None
    employment_types: Optional[List[str]] = None
    company_styles: Optional[List[str]] = None
    seniority_level: Optional[str] = None
    preferred_locations: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    benefits: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    
    current_status: Optional[str] = None
    reason_for_search: Optional[str] = None
    open_to_relocation: Optional[bool] = None
    availability: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response (without password)"""
    id: int
    phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    is_active: bool
    is_superuser: bool
    email_verified: bool
    created_at: datetime
    
    # Preferences
    technologies: Optional[List[str]] = None
    job_titles: Optional[List[str]] = None
    work_models: Optional[List[str]] = None
    employment_types: Optional[List[str]] = None
    company_styles: Optional[List[str]] = None
    seniority_level: Optional[str] = None
    preferred_locations: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    benefits: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    
    current_status: Optional[str] = None
    reason_for_search: Optional[str] = None
    open_to_relocation: Optional[bool] = None
    availability: Optional[str] = None
    is_preferences_complete: bool = False
    
    @field_validator(
        "technologies", "job_titles", "work_models", "employment_types", 
        "company_styles", "preferred_locations", "benefits", "industries",
        mode="before"
    )
    @classmethod
    def parse_json_list(cls, v):
        if isinstance(v, str):
            try:
                import json
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v
    
    class Config:
        from_attributes = True  # Pydantic v2


class UserInDB(UserBase):
    """Schema for user in database (with hashed password)"""
    id: int
    hashed_password: str
    is_active: bool
    is_superuser: bool
    
    class Config:
        from_attributes = True

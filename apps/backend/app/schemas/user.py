from pydantic import BaseModel, EmailStr, Field
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


class UserPreferences(BaseModel):
    """Schema for user job preferences"""
    technologies: List[str] = []
    seniority_level: Optional[str] = None
    preferred_locations: List[str] = []
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None


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
    seniority_level: Optional[str] = None
    preferred_locations: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    
    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class UserInDB(UserBase):
    """Schema for user in database (with hashed password)"""
    id: int
    hashed_password: str
    is_active: bool
    is_superuser: bool
    
    class Config:
        from_attributes = True

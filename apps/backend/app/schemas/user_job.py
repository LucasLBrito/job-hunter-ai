from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserJobBase(BaseModel):
    user_id: int
    job_id: int
    compatibility_score: Optional[float] = Field(None, ge=0, le=100)
    status: str = "new"


class UserJobCreate(UserJobBase):
    """Schema for creating a UserJob record"""
    pass


class UserJobUpdate(BaseModel):
    """Schema for updating a UserJob record"""
    compatibility_score: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[str] = None


class UserJobResponse(UserJobBase):
    """Schema for returning a UserJob record"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

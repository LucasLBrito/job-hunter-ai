"""Schemas package"""

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserPreferencesUpdate,
    UserInDB
)

from app.schemas.auth import (
    Token,
    TokenData,
    LoginRequest,
    SignupRequest,
    PasswordChange,
    PasswordReset
)

from app.schemas.job import (
    JobSource,
    JobBase,
    JobCreate,
    JobUpdate,
    JobAnalysis,
    JobResponse,
    JobFilters
)

from app.schemas.resume import (
    ResumeBase,
    ResumeCreate,
    ResumeUpdate,
    ResumeResponse
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserPreferences",
    "UserInDB",
    # Auth
    "Token",
    "TokenData",
    "LoginRequest",
    "SignupRequest",
    "PasswordChange",
    "PasswordReset",
    # Job
    "JobSource",
    "JobBase",
    "JobCreate",
    "JobUpdate",
    "JobAnalysis",
    "JobResponse",
    "JobFilters",
    # Resume
    "ResumeBase",
    "ResumeCreate", 
    "ResumeUpdate",
    "ResumeResponse",
]

"""Schemas package"""

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserPreferences,
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
]

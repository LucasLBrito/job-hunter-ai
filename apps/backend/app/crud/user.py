from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from typing import Optional
import json


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create new user"""
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        is_superuser=False,
        email_verified=False
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(db: AsyncSession, user_id: int, user_in: UserUpdate) -> Optional[User]:
    """Update user profile"""
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_preferences(
    db: AsyncSession,
    user_id: int,
    technologies: Optional[list] = None,
    seniority_level: Optional[str] = None,
    preferred_locations: Optional[list] = None,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None
) -> Optional[User]:
    """Update user job preferences"""
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    
    if technologies is not None:
        user.technologies = json.dumps(technologies)
    if seniority_level is not None:
        user.seniority_level = seniority_level
    if preferred_locations is not None:
        user.preferred_locations = json.dumps(preferred_locations)
    if salary_min is not None:
        user.salary_min = salary_min
    if salary_max is not None:
        user.salary_max = salary_max
    
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    from app.core.security import verify_password
    
    user = await get_user_by_email(db, email)
    if not user:
        # Try with username
        user = await get_user_by_username(db, email)
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from typing import Optional
import json


class CRUDUser:
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get(self, db: AsyncSession, id: int) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, user_in: UserCreate) -> User:
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

    async def update(self, db: AsyncSession, *, db_obj: User, obj_in) -> User:
        """Update user profile. obj_in can be a Pydantic model or a dict."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_preferences(
        self,
        db: AsyncSession,
        user: User,
        technologies: Optional[list] = None,
        seniority_level: Optional[str] = None,
        preferred_locations: Optional[list] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None
    ) -> User:
        """Update user job preferences"""
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
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def authenticate(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.get_by_email(db, email)
        if not user:
            # Try with username
            user = await self.get_by_username(db, email)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user

user = CRUDUser()

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user_job import UserJob
from app.schemas.user_job import UserJobCreate, UserJobUpdate


class CRUDUserJob:
    async def get(self, db: AsyncSession, id: int) -> Optional[UserJob]:
        result = await db.execute(select(UserJob).where(UserJob.id == id))
        return result.scalars().first()

    async def get_by_user_and_job(self, db: AsyncSession, user_id: int, job_id: int) -> Optional[UserJob]:
        result = await db.execute(
            select(UserJob).where(UserJob.user_id == user_id, UserJob.job_id == job_id)
        )
        return result.scalars().first()

    async def get_top_by_user(self, db: AsyncSession, user_id: int, limit: int = 20) -> List[UserJob]:
        """Get the top scored jobs for a given user, ordered by compatibility_score desc."""
        result = await db.execute(
            select(UserJob)
            .where(UserJob.user_id == user_id)
            .order_by(UserJob.compatibility_score.desc().nullslast())
            .limit(limit)
        )
        return result.scalars().all()

    async def create_or_update(self, db: AsyncSession, *, user_id: int, job_id: int, score: float) -> UserJob:
        """
        Create a new UserJob record, or update the score if one already exists
        (upsert pattern for the unique constraint on user_id + job_id).
        """
        existing = await self.get_by_user_and_job(db, user_id=user_id, job_id=job_id)
        if existing:
            existing.compatibility_score = score
            db.add(existing)
            await db.commit()
            await db.refresh(existing)
            return existing

        new_record = UserJob(user_id=user_id, job_id=job_id, compatibility_score=score)
        db.add(new_record)
        await db.commit()
        await db.refresh(new_record)
        return new_record

    async def update_status(self, db: AsyncSession, *, user_id: int, job_id: int, status: str) -> Optional[UserJob]:
        """Update the status field (e.g., 'applied', 'rejected', 'saved') of a UserJob entry."""
        record = await self.get_by_user_and_job(db, user_id=user_id, job_id=job_id)
        if not record:
            return None
        record.status = status
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record


user_job = CRUDUserJob()

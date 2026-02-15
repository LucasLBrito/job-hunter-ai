from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.resume import Resume
from app.schemas.resume import ResumeCreate, ResumeUpdate

class CRUDResume:
    async def get(self, db: AsyncSession, id: int) -> Optional[Resume]:
        result = await db.execute(select(Resume).filter(Resume.id == id))
        return result.scalars().first()

    async def get_multi_by_owner(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Resume]:
        result = await db.execute(
            select(Resume)
            .filter(Resume.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: ResumeCreate, user_id: int
    ) -> Resume:
        db_obj = Resume(
            user_id=user_id,
            filename=obj_in.filename,
            file_path=obj_in.file_path,
            file_size=obj_in.file_size,
            file_type=obj_in.file_type,
            description=obj_in.description,
            is_active=True,
            is_analyzed=False
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: Resume, obj_in: ResumeUpdate
    ) -> Resume:
        update_data = obj_in.model_dump(exclude_unset=True)
        if not update_data:
            return db_obj
            
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[Resume]:
        result = await db.execute(select(Resume).filter(Resume.id == id))
        obj = result.scalars().first()
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

resume = CRUDResume()

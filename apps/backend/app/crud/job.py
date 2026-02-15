from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate

class CRUDJob:
    async def get(self, db: AsyncSession, id: int) -> Optional[Job]:
        result = await db.execute(select(Job).filter(Job.id == id))
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Job]:
        result = await db.execute(select(Job).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: JobCreate) -> Job:
        db_obj = Job(
            title=obj_in.title,
            company=obj_in.company,
            source_url=obj_in.source_url,
            external_id=obj_in.external_id,
            source_platform=obj_in.source_platform.value,
            location=obj_in.location,
            description=obj_in.description,
            salary_min=obj_in.salary_min,
            salary_max=obj_in.salary_max,
            is_active=True
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: Job, obj_in: JobUpdate
    ) -> Job:
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Se não houver campos para atualizar, retorna o objeto original
        if not update_data:
            return db_obj
            
        # Atualiza os atributos do objeto
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[Job]:
        result = await db.execute(select(Job).filter(Job.id == id))
        obj = result.scalars().first()
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

job = CRUDJob()

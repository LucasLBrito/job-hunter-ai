import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime

from app.services.scrapers.base import BaseScraper
from app.services.scrapers.remoteok import RemoteOKScraper
from app.services.scrapers.models import ScrapedJob
from app.models.job import Job
from app.crud import job as crud_job
from app.schemas.job import JobCreate

logger = logging.getLogger(__name__)

class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db
        # Registry of available scrapers
        self.scrapers: List[BaseScraper] = [
            RemoteOKScraper()
        ]

    async def search_and_save_jobs(self, query: str, limit: int = 50) -> List[Job]:
        """
        Search for jobs across all configured scrapers and save new ones to DB.
        """
        all_new_jobs = []
        
        for scraper in self.scrapers:
            try:
                scraped_results = await scraper.search_jobs(query, limit=limit)
                
                for scraped_job in scraped_results:
                    # Deduplication check
                    existing_job = await crud_job.get_by_external_id(self.db, external_id=scraped_job.external_id)
                    if existing_job:
                        logger.info(f"Job already exists: {scraped_job.title} ({scraped_job.external_id})")
                        continue
                        
                    # Save new job
                    # Map ScrapedJob to JobCreate/SQLAlchemy Model
                    # Note: JobCreate schema might need updates for new fields if strictly validated
                    # For now using direct model mapping or ensuring Schema compatibility
                    
                    job_in = JobCreate(
                        title=scraped_job.title,
                        company=scraped_job.company,
                        location=scraped_job.location,
                        is_remote=scraped_job.is_remote,
                        salary_min=scraped_job.salary_min,
                        salary_max=scraped_job.salary_max,
                        salary_currency=scraped_job.salary_currency,
                        description=scraped_job.description,
                        requirements=None, # Scraper might not separate requirements
                        source_platform=scraped_job.source_platform,
                        source_url=scraped_job.url,
                        external_id=scraped_job.external_id
                    )
                    
                    new_job = await crud_job.create(self.db, obj_in=job_in)
                    
                    # Generate & Store Embedding (Pinecone)
                    try:
                        from app.services.embedding_service import EmbeddingService
                        from app.services.pinecone_service import PineconeService
                        
                        embed_text = f"{new_job.title} {new_job.company} {new_job.description or ''}"
                        
                        embedding_service = EmbeddingService()
                        if embedding_service.api_key:
                            vector = await embedding_service.get_embedding(embed_text)
                            
                            pinecone_service = PineconeService()
                            pinecone_service.upsert_job(
                                job_id=new_job.id,
                                embedding=vector,
                                metadata={
                                    "title": new_job.title,
                                    "company": new_job.company,
                                    "location": new_job.location,
                                    "is_remote": new_job.is_remote
                                }
                            )
                    except Exception as e:
                         logger.error(f"Embedding/Pinecone failed for job {new_job.id}: {e}")
                    

                    
                    all_new_jobs.append(new_job)
                    
            except Exception as e:
                logger.error(f"Error executing scraper {type(scraper).__name__}: {e}")
                
        logger.info(f"Saved {len(all_new_jobs)} new jobs for query '{query}'")
        return all_new_jobs

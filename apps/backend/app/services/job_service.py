import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime

from app.services.scrapers.base import BaseScraper
from app.services.scrapers.remoteok import RemoteOKScraper
from app.services.scrapers.jobspy_scraper import JobSpyScraper
from app.services.scrapers.adzuna_scraper import AdzunaScraper
from app.services.scrapers.catho_scraper import CathoScraper
from app.services.scrapers.models import ScrapedJob
from app.models.job import Job
from app.crud import job as crud_job
from app.schemas.job import JobCreate

logger = logging.getLogger(__name__)

class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db
        # Registry of all available scrapers
        self.scrapers: List[BaseScraper] = []
        
        from app.core.config import settings
        if settings.ENABLE_JOBSPY:
            self.scrapers.append(JobSpyScraper())
            
        self.scrapers.append(RemoteOKScraper())
        self.scrapers.append(AdzunaScraper())
        self.scrapers.append(CathoScraper())

    async def search_and_save_jobs(self, query: str, limit: int = 50) -> List[Job]:
        """
        Search for jobs across ALL configured scrapers and save new ones to DB.
        Runs scrapers in parallel for speed.
        """
        all_new_jobs = []
        
        # Run all scrapers in parallel
        scraper_tasks = []
        for scraper in self.scrapers:
            scraper_tasks.append(
                self._run_scraper_safe(scraper, query, limit)
            )
        
        results = await asyncio.gather(*scraper_tasks)
        
        # Flatten results from all scrapers
        all_scraped = []
        for scraper_results in results:
            all_scraped.extend(scraper_results)
        
        logger.info(f"Total scraped jobs across all platforms: {len(all_scraped)}")
        
        # Save to database with deduplication
        for scraped_job in all_scraped:
            try:
                # Deduplication check by external_id
                existing_job = await crud_job.get_by_external_id(
                    self.db, external_id=scraped_job.external_id
                )
                if existing_job:
                    continue
                
                # Extra deduplication by Title + Company to avoid overlapping sources
                from sqlalchemy import select
                existing_by_name = await self.db.execute(
                    select(Job).where(
                        Job.title == scraped_job.title, 
                        Job.company == scraped_job.company
                    )
                )
                if existing_by_name.scalars().first():
                    continue
                    
                # Save new job
                job_in = JobCreate(
                    title=scraped_job.title,
                    company=scraped_job.company,
                    location=scraped_job.location,
                    is_remote=scraped_job.is_remote,
                    salary_min=scraped_job.salary_min,
                    salary_max=scraped_job.salary_max,
                    salary_currency=scraped_job.salary_currency,
                    description=scraped_job.description,
                    requirements=None,
                    source_platform=scraped_job.source_platform,
                    source_url=scraped_job.url,
                    external_id=scraped_job.external_id
                )
                
                new_job = await crud_job.create(self.db, obj_in=job_in)
                
                # Generate & Store Embedding (Pinecone) — optional
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
                    logger.warning(f"Embedding/Pinecone skipped for job {new_job.id}: {e}")
                
                all_new_jobs.append(new_job)
                    
            except Exception as e:
                logger.error(f"Error saving job '{scraped_job.title}': {e}")
                
        logger.info(f"Saved {len(all_new_jobs)} new jobs for query '{query}'")
        return all_new_jobs

    async def _run_scraper_safe(self, scraper: BaseScraper, query: str, limit: int) -> List[ScrapedJob]:
        """Run a scraper with error handling — never crash the whole search."""
        scraper_name = type(scraper).__name__
        try:
            # 25 seconds timeout to prevent hanging the entire process
            results = await asyncio.wait_for(
                scraper.search_jobs(query, limit=limit),
                timeout=25.0
            )
            logger.info(f"{scraper_name}: returned {len(results)} results")
            return results
        except asyncio.TimeoutError:
            logger.error(f"{scraper_name} timed out after 25 seconds.")
            return []
        except Exception as e:
            logger.error(f"{scraper_name} failed: {e}")
            return []

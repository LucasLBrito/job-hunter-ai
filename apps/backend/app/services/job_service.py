import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime

from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.remoteok import RemoteOKScraper
from app.services.jobsearch.jobspy_scraper import JobSpyScraper
from app.services.jobsearch.adzuna import AdzunaScraper
from app.services.jobsearch.vagas import VagasScraper
from app.services.jobsearch.gupy import GupyScraper
from app.services.jobsearch.programathor import ProgramaThorScraper
from app.services.jobsearch.geekhunter import GeekHunterScraper
from app.services.jobsearch.coodesh import CoodeshScraper
from app.services.jobsearch.apinfo import APInfoScraper
from app.services.jobsearch.remotar import RemotarScraper
from app.services.jobsearch.weworkremotely import WeWorkRemotelyScraper
from app.services.jobsearch.workana import WorkanaScraper
from app.services.jobsearch.freela import FreelaScraper
from app.services.jobsearch.cathoscraper import CathoScraper
from app.services.jobsearch.models import ScrapedJob
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
        self.scrapers.append(VagasScraper())
        self.scrapers.append(GupyScraper())
        self.scrapers.append(ProgramaThorScraper())
        self.scrapers.append(GeekHunterScraper())
        self.scrapers.append(CoodeshScraper())
        self.scrapers.append(APInfoScraper())
        self.scrapers.append(RemotarScraper())
        self.scrapers.append(WeWorkRemotelyScraper())
        self.scrapers.append(WorkanaScraper())
        self.scrapers.append(FreelaScraper())
        self.scrapers.append(CathoScraper())

    async def search_and_save_jobs(self, query: str, limit: int = 200, user_for_scoring = None, max_saved_jobs: int = 100) -> List[Job]:
        """
        Search for jobs across ALL configured scrapers and save new ones to DB.
        Runs scrapers concurrently (3 at a time via semaphore) for high throughput.
        If user_for_scoring is provided, it will score the jobs in memory and only save the top `max_saved_jobs`.
        """
        all_scraped = []
        
        # Higher limit per scraper for volume
        jobs_per_scraper = max(30, limit // max(1, len(self.scrapers)))
        
        # Semaphore to limit concurrent scrapers (avoid overwhelming network/IP)
        sem = asyncio.Semaphore(3)
        
        async def run_with_semaphore(scraper):
            async with sem:
                name = type(scraper).__name__
                try:
                    logger.info(f"Fetching {jobs_per_scraper} jobs from {name} for '{query}'...")
                    results = await self._run_scraper_safe(scraper, query, jobs_per_scraper)
                    # Small delay after each scraper to avoid IP blocks
                    await asyncio.sleep(2)
                    return results
                except Exception as e:
                    logger.error(f"Error orchestrating {name}: {e}")
                    return []
        
        # Run all scrapers concurrently (semaphore limits to 3 at a time)
        tasks = [run_with_semaphore(s) for s in self.scrapers]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results_list:
            if isinstance(result, list):
                all_scraped.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Scraper task failed: {result}")
        
        logger.info(f"Total scraped jobs across all platforms: {len(all_scraped)}")
        
        if not all_scraped:
            logger.info("No jobs found from scrapers. Adding seed jobs for testing.")
            all_scraped = self._get_seed_jobs(query)
            
        # Score jobs in memory to save only the most relevant ones
        if user_for_scoring:
            from app.services.scoring_service import ScoringService
            from sqlalchemy import select, desc
            from app.models.resume import Resume
            
            # Get user's most recent analyzed resume completely independently
            try:
                stmt = select(Resume).where(
                    Resume.user_id == user_for_scoring.id,
                    Resume.is_analyzed == True
                ).order_by(desc(Resume.analyzed_at)).limit(1)
                result = await self.db.execute(stmt)
                resume = result.scalars().first()
            except Exception as e:
                logger.warning(f"Could not load resume for scoring: {e}")
                resume = None
                
            preferences = ScoringService.extract_skills_and_preferences(user_for_scoring, resume)
            
            # Score each scraped job
            for job in all_scraped:
                job.compatibility_score = ScoringService.calculate_score(job, preferences)
                
            # Sort descending by score
            all_scraped.sort(key=lambda x: x.compatibility_score or 0, reverse=True)
            
            # Keep only the top `max_saved_jobs` to prevent DB bloat
            all_scraped = all_scraped[:max_saved_jobs]
            logger.info(f"Trimmed to top {len(all_scraped)} jobs based on user profile scoring.")
            
        # Save to database with deduplication
        for scraped_job in all_scraped:
            try:
                # Deduplication check by external_id
                existing_job = await crud_job.get_by_external_id(
                    self.db, external_id=scraped_job.external_id
                )
                if existing_job:
                    if user_for_scoring:
                        try:
                            from app.crud.user_job import user_job as crud_user_job
                            score = getattr(scraped_job, "compatibility_score", None) or 0
                            await crud_user_job.create_or_update(
                                self.db,
                                user_id=user_for_scoring.id,
                                job_id=existing_job.id,
                                score=score
                            )
                        except Exception as e:
                            logger.warning(f"Could not update UserJob score for existing job {existing_job.id}: {e}")
                    # Add to return list even if it already exists, so the frontend gets all results
                    all_new_jobs.append(existing_job)
                    continue
                
                # Extra deduplication by Title + Company to avoid overlapping sources
                from sqlalchemy import select
                existing_by_name = await self.db.execute(
                    select(Job).where(
                        Job.title == scraped_job.title, 
                        Job.company == scraped_job.company
                    )
                )
                existing_job_by_name = existing_by_name.scalars().first()
                if existing_job_by_name:
                    if user_for_scoring:
                        try:
                            from app.crud.user_job import user_job as crud_user_job
                            score = getattr(scraped_job, "compatibility_score", None) or 0
                            await crud_user_job.create_or_update(
                                self.db,
                                user_id=user_for_scoring.id,
                                job_id=existing_job_by_name.id,
                                score=score
                            )
                        except Exception as e:
                            logger.warning(f"Could not update UserJob score for existing job {existing_job_by_name.id}: {e}")
                    all_new_jobs.append(existing_job_by_name)
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
                    external_id=scraped_job.external_id,
                    compatibility_score=getattr(scraped_job, "compatibility_score", None)
                )
                
                new_job = await crud_job.create(self.db, obj_in=job_in)

                # Save user-specific score in the UserJob table
                if user_for_scoring:
                    try:
                        from app.crud.user_job import user_job as crud_user_job
                        score = getattr(scraped_job, "compatibility_score", None) or 0
                        await crud_user_job.create_or_update(
                            self.db,
                            user_id=user_for_scoring.id,
                            job_id=new_job.id,
                            score=score
                        )
                    except Exception as e:
                        logger.warning(f"Could not save UserJob score for job {new_job.id}: {e}")

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
                
        logger.info(f"Returning {len(all_new_jobs)} jobs for query '{query}'")
        return all_new_jobs

    def _get_seed_jobs(self, query: str) -> List[ScrapedJob]:
        """Return some sample jobs if nothing was found, so the user can test the UI."""
        return [
            ScrapedJob(
                title=f"Desenvolvedor {query.capitalize() or 'Senior'}",
                company="Tech Solutions Brazil",
                location="São Paulo, SP",
                is_remote=True,
                description=f"Oportunidade para atuar com {query or 'tecnologia'} em um ambiente dinâmico.",
                url="https://example.com/job1",
                external_id=f"seed_1_{query}",
                source_platform="system_seed",
                posted_at=datetime.utcnow()
            ),
            ScrapedJob(
                title=f"Engenheiro de Software ({query or 'Backend'})",
                company="Global Innovations",
                location="Remoto",
                is_remote=True,
                description=f"Buscamos especialistas em {query or 'desenvolvimento'} para nosso time global.",
                url="https://example.com/job2",
                external_id=f"seed_2_{query}",
                source_platform="system_seed",
                posted_at=datetime.utcnow()
            )
        ]

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

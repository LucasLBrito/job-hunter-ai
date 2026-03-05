"""Gupy Scraper - Uses Gupy's public API."""
import logging
from typing import List
from datetime import datetime
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class GupyScraper(BaseScraper):
    PLATFORM_NAME = "gupy"
    BASE_URL = "https://portal.api.gupy.io/api/v1/jobs"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        params = {"jobName": query, "limit": min(limit, 40), "offset": 0}
        jobs = []
        try:
            resp = await self.fetch(self.BASE_URL, params=params, headers={"Accept": "application/json"})
            data = resp.json()
            for item in data.get("data", [])[:limit]:
                try:
                    job_id = str(item.get("id", ""))
                    title = item.get("name") or item.get("jobName") or "N/A"
                    company = item.get("careerPageName") or item.get("company", {}).get("name", "Confidencial")
                    location = item.get("city") or item.get("state") or "Brasil"
                    is_remote = str(item.get("workplaceType", "")).lower() in ("remote", "remoto", "home_office")
                    job_url = item.get("jobUrl") or f"https://gupy.io/vagas/{job_id}"
                    jobs.append(ScrapedJob(
                        title=title, company=company, location=location, is_remote=is_remote,
                        description=item.get("description") or "", url=job_url,
                        external_id=f"gupy_{job_id}", source_platform=self.PLATFORM_NAME,
                        posted_at=datetime.utcnow(), employment_type=item.get("type"), technologies=[],
                    ))
                except Exception as e:
                    logger.warning(f"GupyScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"GupyScraper: failed: {e}")
        logger.info(f"GupyScraper: found {len(jobs)} results for '{query}'")
        return jobs

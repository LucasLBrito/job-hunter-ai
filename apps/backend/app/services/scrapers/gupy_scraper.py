"""
Gupy Scraper — Busca vagas via API pública da Gupy (sem autenticação necessária).
Documentação: https://portal.api.gupy.io/docs
"""
import logging
import httpx
from typing import List, Optional
from datetime import datetime

from app.services.scrapers.base import BaseScraper
from app.services.scrapers.models import ScrapedJob

logger = logging.getLogger(__name__)


class GupyScraper(BaseScraper):
    PLATFORM_NAME = "gupy"
    BASE_URL = "https://portal.api.gupy.io/api/v1/jobs"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        params = {
            "jobName": query,
            "limit": min(limit, 40),
            "offset": 0,
        }
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; JobHunterAI/1.0)",
        }

        jobs: List[ScrapedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(self.BASE_URL, params=params, headers=headers)
                if resp.status_code != 200:
                    logger.warning(f"GupyScraper: HTTP {resp.status_code}")
                    return []

                data = resp.json()
                items = data.get("data", [])

                for item in items[:limit]:
                    try:
                        job_id = str(item.get("id", ""))
                        title = item.get("name") or item.get("jobName") or "N/A"
                        company = item.get("careerPageName") or item.get("company", {}).get("name", "Confidencial")
                        location = item.get("city") or item.get("state") or "Brasil"
                        is_remote = str(item.get("workplaceType", "")).lower() in ("remote", "remoto", "home_office")
                        job_url = item.get("jobUrl") or f"https://gupy.io/vagas/{job_id}"

                        jobs.append(ScrapedJob(
                            title=title,
                            company=company,
                            location=location,
                            is_remote=is_remote,
                            description=item.get("description") or "",
                            url=job_url,
                            external_id=f"gupy_{job_id}",
                            source_platform=self.PLATFORM_NAME,
                            posted_at=datetime.utcnow(),
                            employment_type=item.get("type"),
                            technologies=[],
                        ))
                    except Exception as e:
                        logger.warning(f"GupyScraper: parse error for item: {e}")

        except Exception as e:
            logger.error(f"GupyScraper: request failed: {e}")

        logger.info(f"GupyScraper: found {len(jobs)} results for '{query}'")
        return jobs

    async def get_job_details(self, job_url: str) -> Optional[ScrapedJob]:
        return None

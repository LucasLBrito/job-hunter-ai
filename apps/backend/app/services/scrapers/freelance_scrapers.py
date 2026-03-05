"""
Freelance Scrapers — Workana e 99Freelas
Plataformas de trabalho freelance no Brasil, seguindo BaseScraper async.
"""
import logging
import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime

from app.services.scrapers.base import BaseScraper
from app.services.scrapers.models import ScrapedJob

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


class WorkanaScraper(BaseScraper):
    """Workana — maior plataforma de freelance da América Latina."""
    PLATFORM_NAME = "workana"
    BASE_URL = "https://www.workana.com/jobs"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        params = {"search_query": query, "language": "pt"}
        jobs: List[ScrapedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(self.BASE_URL, params=params, headers=HEADERS)
                if resp.status_code != 200:
                    logger.warning(f"WorkanaScraper: HTTP {resp.status_code}")
                    return []
                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("div.project-item, article.project-item, div[class*='project']")
                for card in cards[:limit]:
                    try:
                        title_el = card.select_one("h2, h3, [class*='title']")
                        title = title_el.get_text(strip=True) if title_el else "N/A"
                        link_el = card.select_one("a[href*='/job/']") or card.select_one("a")
                        href = link_el["href"] if link_el and link_el.get("href") else ""
                        job_url = f"https://www.workana.com{href}" if href.startswith("/") else (href or self.BASE_URL)
                        budget_el = card.select_one("[class*='budget'], [class*='price']")
                        budget = budget_el.get_text(strip=True) if budget_el else ""
                        desc_el = card.select_one("p, [class*='description']")
                        desc = desc_el.get_text(strip=True) if desc_el else ""
                        external_id = f"workana_{hash(job_url)}"
                        jobs.append(ScrapedJob(
                            title=title, company="Cliente Workana",
                            location="Remoto (Freelance)", is_remote=True,
                            description=f"{desc} {budget}".strip(),
                            url=job_url, external_id=external_id,
                            source_platform=self.PLATFORM_NAME,
                            posted_at=datetime.utcnow(), employment_type="Freelance",
                            technologies=[],
                        ))
                    except Exception as e:
                        logger.warning(f"WorkanaScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"WorkanaScraper: request failed: {e}")
        logger.info(f"WorkanaScraper: found {len(jobs)} results for '{query}'")
        return jobs

    async def get_job_details(self, job_url: str) -> Optional[ScrapedJob]:
        return None


class FreelaScraper(BaseScraper):
    """99Freelas — plataforma de freelances brasileira."""
    PLATFORM_NAME = "99freelas"
    BASE_URL = "https://www.99freelas.com.br/projects"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        params = {"q": query}
        jobs: List[ScrapedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(self.BASE_URL, params=params, headers=HEADERS)
                if resp.status_code != 200:
                    logger.warning(f"FreelaScraper: HTTP {resp.status_code}")
                    return []
                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("div.result-list-item, li.result-item, article")
                for card in cards[:limit]:
                    try:
                        title_el = card.select_one("h2, h3, [class*='title']")
                        title = title_el.get_text(strip=True) if title_el else "N/A"
                        link_el = card.select_one("a")
                        href = link_el["href"] if link_el and link_el.get("href") else ""
                        job_url = f"https://www.99freelas.com.br{href}" if href.startswith("/") else (href or self.BASE_URL)
                        budget_el = card.select_one("[class*='budget'], [class*='valor']")
                        budget = budget_el.get_text(strip=True) if budget_el else ""
                        desc_el = card.select_one("p, [class*='description']")
                        desc = desc_el.get_text(strip=True) if desc_el else ""
                        external_id = f"99freelas_{hash(job_url)}"
                        jobs.append(ScrapedJob(
                            title=title, company="Cliente 99Freelas",
                            location="Remoto (Freelance)", is_remote=True,
                            description=f"{desc} {budget}".strip(),
                            url=job_url, external_id=external_id,
                            source_platform=self.PLATFORM_NAME,
                            posted_at=datetime.utcnow(), employment_type="Freelance",
                            technologies=[],
                        ))
                    except Exception as e:
                        logger.warning(f"FreelaScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"FreelaScraper: request failed: {e}")
        logger.info(f"FreelaScraper: found {len(jobs)} results for '{query}'")
        return jobs

    async def get_job_details(self, job_url: str) -> Optional[ScrapedJob]:
        return None

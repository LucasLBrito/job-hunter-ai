"""
Remote Scrapers — Remotar e We Work Remotely
Vagas 100% remotas, seguindo o padrão BaseScraper async.
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


class RemotarScraper(BaseScraper):
    """Remotar — plataforma brasileira 100% home office."""
    PLATFORM_NAME = "remotar"
    BASE_URL = "https://remotar.com.br/jobs"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        url = f"{self.BASE_URL}?search={query.replace(' ', '+')}"
        jobs: List[ScrapedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=HEADERS)
                if resp.status_code != 200:
                    logger.warning(f"RemotarScraper: HTTP {resp.status_code}")
                    return []
                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("article, div[class*='job'], li[class*='job']")
                for card in cards[:limit]:
                    try:
                        title_el = card.select_one("h2, h3, [class*='title']")
                        title = title_el.get_text(strip=True) if title_el else "N/A"
                        company_el = card.select_one("[class*='company'], [class*='employer']")
                        company = company_el.get_text(strip=True) if company_el else "Confidencial"
                        link_el = card.select_one("a")
                        href = link_el["href"] if link_el and link_el.get("href") else ""
                        job_url = f"https://remotar.com.br{href}" if href.startswith("/") else (href or url)
                        desc_el = card.select_one("p, [class*='desc']")
                        desc = desc_el.get_text(strip=True) if desc_el else ""
                        external_id = f"remotar_{hash(job_url)}"
                        jobs.append(ScrapedJob(
                            title=title, company=company, location="Remoto (Brasil)",
                            is_remote=True, description=desc, url=job_url,
                            external_id=external_id, source_platform=self.PLATFORM_NAME,
                            posted_at=datetime.utcnow(), employment_type=None, technologies=[],
                        ))
                    except Exception as e:
                        logger.warning(f"RemotarScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"RemotarScraper: request failed: {e}")
        logger.info(f"RemotarScraper: found {len(jobs)} results for '{query}'")
        return jobs

    async def get_job_details(self, job_url: str) -> Optional[ScrapedJob]:
        return None


class WeWorkRemotelyScraper(BaseScraper):
    """We Work Remotely — maior plataforma de vagas remotas globais."""
    PLATFORM_NAME = "weworkremotely"
    BASE_URL = "https://weworkremotely.com/remote-jobs/search"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        url = f"{self.BASE_URL}?term={query.replace(' ', '+')}"
        jobs: List[ScrapedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=HEADERS)
                if resp.status_code != 200:
                    logger.warning(f"WeWorkRemotelyScraper: HTTP {resp.status_code}")
                    return []
                soup = BeautifulSoup(resp.text, "html.parser")
                # WWR usa <li> dentro de <section class="jobs">
                items = soup.select("section.jobs li:not(.view-all)")
                for item in items[:limit]:
                    try:
                        title_el = item.select_one("span.title")
                        title = title_el.get_text(strip=True) if title_el else "N/A"
                        company_el = item.select_one("span.company")
                        company = company_el.get_text(strip=True) if company_el else "Confidencial"
                        region_el = item.select_one("span.region")
                        region = region_el.get_text(strip=True) if region_el else "Worldwide"
                        link_el = item.select_one("a")
                        href = link_el["href"] if link_el and link_el.get("href") else ""
                        job_url = f"https://weworkremotely.com{href}" if href.startswith("/") else href
                        external_id = f"weworkremotely_{hash(job_url)}"
                        jobs.append(ScrapedJob(
                            title=title, company=company, location=region,
                            is_remote=True, description="",
                            url=job_url, external_id=external_id,
                            source_platform=self.PLATFORM_NAME,
                            posted_at=datetime.utcnow(), employment_type=None, technologies=[],
                        ))
                    except Exception as e:
                        logger.warning(f"WeWorkRemotelyScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"WeWorkRemotelyScraper: request failed: {e}")
        logger.info(f"WeWorkRemotelyScraper: found {len(jobs)} results for '{query}'")
        return jobs

    async def get_job_details(self, job_url: str) -> Optional[ScrapedJob]:
        return None

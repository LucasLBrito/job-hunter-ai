"""APInfo Scraper - HTML scraping from apinfo.com."""
import logging
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class APInfoScraper(BaseScraper):
    PLATFORM_NAME = "apinfo"
    BASE_URL = "https://www.apinfo.com/apinfo/asp/formvagas.cfm"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        params = {"texto": query, "acao": "listar"}
        jobs = []
        try:
            resp = await self.fetch(self.BASE_URL, params=params, referer="https://www.apinfo.com/")
            soup = BeautifulSoup(resp.text, "html.parser")
            rows = soup.select("table tr")
            for row in rows[:limit]:
                try:
                    cells = row.select("td")
                    if len(cells) < 2:
                        continue
                    title = cells[0].get_text(strip=True)
                    if not title or title.lower() in ("cargo", "funcao"):
                        continue
                    company = cells[1].get_text(strip=True) if len(cells) > 1 else "Confidencial"
                    link_el = cells[0].select_one("a") or row.select_one("a")
                    href = link_el["href"] if link_el and link_el.get("href") else ""
                    job_url = f"https://www.apinfo.com{href}" if href.startswith("/") else (href or self.BASE_URL)
                    location = cells[2].get_text(strip=True) if len(cells) > 2 else "Brasil"
                    is_remote = "remoto" in location.lower()
                    external_id = f"apinfo_{hash(job_url)}"
                    jobs.append(ScrapedJob(
                        title=title, company=company, location=location, is_remote=is_remote,
                        description="", url=job_url, external_id=external_id,
                        source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(), technologies=[],
                    ))
                except Exception as e:
                    logger.warning(f"APInfoScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"APInfoScraper: failed: {e}")
        logger.info(f"APInfoScraper: found {len(jobs)} results for '{query}'")
        return jobs

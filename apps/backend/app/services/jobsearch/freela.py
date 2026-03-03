"""99Freelas Scraper - HTML scraping from 99freelas.com.br."""
import logging
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class FreelaScraper(BaseScraper):
    PLATFORM_NAME = "99freelas"
    BASE_URL = "https://www.99freelas.com.br/projects"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        params = {"q": query}
        jobs = []
        try:
            resp = await self.fetch(self.BASE_URL, params=params, referer="https://www.99freelas.com.br/")
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
                        posted_at=datetime.utcnow(), employment_type="Freelance", technologies=[],
                    ))
                except Exception as e:
                    logger.warning(f"FreelaScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"FreelaScraper: failed: {e}")
        logger.info(f"FreelaScraper: found {len(jobs)} results for '{query}'")
        return jobs

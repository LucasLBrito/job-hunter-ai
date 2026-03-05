"""Workana Scraper - HTML scraping from workana.com with improved selectors."""
import logging
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class WorkanaScraper(BaseScraper):
    PLATFORM_NAME = "workana"
    BASE_URL = "https://www.workana.com/jobs"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        params = {"query": query, "language": "pt"}
        logger.info(f"WorkanaScraper: Searching for '{query}'")
        jobs = []
        try:
            resp = await self.fetch(self.BASE_URL, params=params, referer="https://www.workana.com/")
            soup = BeautifulSoup(resp.text, "html.parser")

            # Workana uses project-item cards
            cards = (
                soup.select("div.project-item") or
                soup.select("article.project-item") or
                soup.select("div[class*='project']") or
                soup.select("a[href*='/job/']")
            )
            for card in cards[:limit]:
                try:
                    title_el = card.select_one("h2, h3, [class*='title'], span.project-title")
                    title = title_el.get_text(strip=True) if title_el else card.get_text(strip=True)[:80]
                    if not title or len(title) < 3:
                        continue
                    link_el = card if card.name == "a" else (card.select_one("a[href*='/job/']") or card.select_one("a"))
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
                        posted_at=datetime.utcnow(), employment_type="Freelance", technologies=[],
                    ))
                except Exception as e:
                    logger.warning(f"WorkanaScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"WorkanaScraper: failed: {e}")
        logger.info(f"WorkanaScraper: found {len(jobs)} results for '{query}'")
        return jobs

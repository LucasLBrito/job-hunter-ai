"""Workana Scraper - HTML scraping from workana.com."""
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

            # Workana uses multiple possible structures
            cards = (
                soup.select("div.project-item") or
                soup.select("article.project-item") or
                soup.select("a[href*='/job/']") or
                soup.select("div[class*='project']") or
                soup.select("h2 a, h3 a")  # Broad fallback
            )
            seen = set()
            for card in cards[:limit * 2]:
                try:
                    if card.name == "a":
                        title = card.get_text(strip=True)[:100]
                        href = card.get("href", "")
                        parent = card.find_parent("div") or card.find_parent("article")
                    else:
                        title_el = card.select_one("h2 a, h3 a, h2, h3, [class*='title'], span.project-title, a[href*='/job/']")
                        if not title_el:
                            continue
                        title = title_el.get_text(strip=True)
                        link_el = title_el if title_el.name == "a" else card.select_one("a[href*='/job/']") or card.select_one("a")
                        href = link_el["href"] if link_el and link_el.get("href") else ""
                        parent = card

                    if not title or len(title) < 5 or title in seen:
                        continue
                    # Skip non-job links (navigation, etc)
                    if href and "/job/" not in href and "/jobs/" not in href and "/project/" not in href:
                        continue
                    seen.add(title)
                    job_url = f"https://www.workana.com{href}" if href.startswith("/") else (href or self.BASE_URL)
                    budget = ""
                    desc = ""
                    if parent:
                        budget_el = parent.select_one("[class*='budget'], [class*='price'], [class*='valor']")
                        budget = budget_el.get_text(strip=True) if budget_el else ""
                        desc_el = parent.select_one("p, [class*='description']")
                        desc = desc_el.get_text(strip=True) if desc_el else ""
                    external_id = f"workana_{hash(job_url)}"
                    jobs.append(ScrapedJob(
                        title=title, company="Cliente Workana",
                        location="Remoto (Freelance)", is_remote=True,
                        description=f"{desc} {budget}".strip()[:3000],
                        url=job_url, external_id=external_id,
                        source_platform=self.PLATFORM_NAME,
                        posted_at=datetime.utcnow(), employment_type="Freelance", technologies=[],
                    ))
                    if len(jobs) >= limit:
                        break
                except Exception as e:
                    logger.warning(f"WorkanaScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"WorkanaScraper: failed: {e}")
        logger.info(f"WorkanaScraper: found {len(jobs)} results for '{query}'")
        return jobs

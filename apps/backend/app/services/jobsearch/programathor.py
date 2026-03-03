"""ProgramaThor Scraper - HTML scraping from programathor.com.br."""
import logging
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class ProgramaThorScraper(BaseScraper):
    PLATFORM_NAME = "programathor"
    BASE_URL = "https://programathor.com.br/jobs"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        # ProgramaThor uses the first word as main filter
        search_term = query.split()[0] if query else "developer"
        url = f"{self.BASE_URL}?search={search_term}"
        logger.info(f"ProgramaThorScraper: Searching at {url}")
        jobs = []
        try:
            resp = await self.fetch(url, referer="https://programathor.com.br/")
            soup = BeautifulSoup(resp.text, "html.parser")
            # Try multiple selector strategies
            cards = soup.select("div.cell-list") or soup.select("div[class*='cell']") or soup.select("article")
            if not cards:
                # Try finding any link to /jobs/ pages
                cards = soup.select("a[href*='/jobs/']")
            for card in cards[:limit]:
                try:
                    title_el = card.select_one("h3") or card.select_one("h2") or card.select_one("[class*='title']")
                    title = title_el.get_text(strip=True) if title_el else card.get_text(strip=True)[:80]
                    if not title or len(title) < 3:
                        continue
                    company_el = card.select_one("h4") or card.select_one(".company") or card.select_one("[class*='company']")
                    company = company_el.get_text(strip=True) if company_el else "Confidencial"
                    link_el = card if card.name == "a" else card.select_one("a")
                    href = link_el["href"] if link_el and link_el.get("href") else ""
                    job_url = f"https://programathor.com.br{href}" if href.startswith("/") else href
                    if not job_url:
                        continue
                    location_el = card.select_one(".location") or card.select_one(".city") or card.select_one("[class*='location']")
                    location = location_el.get_text(strip=True) if location_el else "Brasil"
                    is_remote = "remoto" in location.lower() or "home office" in location.lower() or "remote" in location.lower()
                    desc_el = card.select_one(".description") or card.select_one("p")
                    desc = desc_el.get_text(strip=True) if desc_el else ""
                    external_id = f"programathor_{hash(job_url)}"
                    jobs.append(ScrapedJob(
                        title=title, company=company, location=location, is_remote=is_remote,
                        description=desc, url=job_url, external_id=external_id,
                        source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(), technologies=[],
                    ))
                except Exception as e:
                    logger.warning(f"ProgramaThorScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"ProgramaThorScraper: failed: {e}")
        logger.info(f"ProgramaThorScraper: found {len(jobs)} results for '{query}'")
        return jobs

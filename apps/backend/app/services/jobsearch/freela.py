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

            # Try multiple selector strategies
            cards = (
                soup.select("div.result-list-item") or
                soup.select("li.result-item") or
                soup.select("article") or
                soup.select("div[class*='project']") or
                soup.select("a[href*='/projects/']")
            )
            seen = set()
            for card in cards[:limit * 2]:
                try:
                    if card.name == "a":
                        title = card.get_text(strip=True)[:100]
                        href = card.get("href", "")
                        parent = card.find_parent("div") or card.find_parent("li")
                    else:
                        title_el = card.select_one("h1, h2, h3, a[class*='title'], [class*='title']")
                        if not title_el:
                            title_el = card.select_one("a")
                        title = title_el.get_text(strip=True) if title_el else ""
                        link_el = card.select_one("a[href*='/projects/']") or card.select_one("a")
                        href = link_el["href"] if link_el and link_el.get("href") else ""
                        parent = card

                    if not title or len(title) < 5 or title in seen:
                        continue
                    seen.add(title)
                    job_url = f"https://www.99freelas.com.br{href}" if href.startswith("/") else (href or self.BASE_URL)
                    budget = ""
                    if parent:
                        budget_el = parent.select_one("[class*='budget'], [class*='valor'], [class*='price']")
                        if budget_el:
                            budget = budget_el.get_text(strip=True)
                    desc = ""
                    if parent:
                        desc_el = parent.select_one("p, [class*='description'], [class*='descricao']")
                        if desc_el:
                            desc = desc_el.get_text(strip=True)
                    external_id = f"99freelas_{hash(job_url)}"
                    jobs.append(ScrapedJob(
                        title=title, company="Cliente 99Freelas",
                        location="Remoto (Freelance)", is_remote=True,
                        description=f"{desc} {budget}".strip()[:3000],
                        url=job_url, external_id=external_id,
                        source_platform=self.PLATFORM_NAME,
                        posted_at=datetime.utcnow(), employment_type="Freelance", technologies=[],
                    ))
                    if len(jobs) >= limit:
                        break
                except Exception as e:
                    logger.warning(f"FreelaScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"FreelaScraper: failed: {e}")
        logger.info(f"FreelaScraper: found {len(jobs)} results for '{query}'")
        return jobs

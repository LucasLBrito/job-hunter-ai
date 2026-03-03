"""Coodesh Scraper - Uses Coodesh's internal JSON API."""
import logging
from typing import List
from datetime import datetime
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class CoodeshScraper(BaseScraper):
    PLATFORM_NAME = "coodesh"
    # Coodesh SPA exposes a public GraphQL/REST API
    API_URL = "https://coodesh.com/api/public/vacancies"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        logger.info(f"CoodeshScraper: Searching for '{query}'")
        jobs = []
        try:
            params = {"search": query, "limit": min(limit, 50), "page": 1}
            headers = {"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"}
            resp = await self.fetch(
                self.API_URL, params=params, headers=headers,
                referer="https://coodesh.com/vagas"
            )
            data = resp.json()
            items = data if isinstance(data, list) else data.get("data", data.get("vacancies", data.get("results", [])))
            if isinstance(items, dict):
                items = items.get("data", [])

            for item in (items or [])[:limit]:
                try:
                    title = item.get("title") or item.get("name") or "N/A"
                    company = item.get("company_name") or item.get("company", {}).get("name", "Coodesh") if isinstance(item.get("company"), dict) else str(item.get("company", "Coodesh"))
                    location = item.get("location") or item.get("city") or "Remoto"
                    is_remote = item.get("remote", False) or "remoto" in str(location).lower()
                    slug = item.get("slug") or item.get("id") or ""
                    job_url = item.get("url") or f"https://coodesh.com/vagas/{slug}"
                    desc = item.get("description") or item.get("summary") or ""
                    external_id = f"coodesh_{item.get('id', hash(job_url))}"
                    jobs.append(ScrapedJob(
                        title=title, company=company, location=location, is_remote=is_remote,
                        description=str(desc)[:3000], url=job_url, external_id=external_id,
                        source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(), technologies=[],
                    ))
                except Exception as e:
                    logger.warning(f"CoodeshScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"CoodeshScraper: failed: {e}")
            return await self._fallback_html(query, limit)
        logger.info(f"CoodeshScraper: found {len(jobs)} results for '{query}'")
        return jobs

    async def _fallback_html(self, query: str, limit: int) -> List[ScrapedJob]:
        from bs4 import BeautifulSoup
        jobs = []
        try:
            url = f"https://coodesh.com/vagas?search={query.replace(' ', '+')}"
            resp = await self.fetch(url, referer="https://coodesh.com/")
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select("a[href*='/vagas/'], div[class*='card']")
            for card in cards[:limit]:
                try:
                    title_el = card.select_one("h2, h3, [class*='title']")
                    title = title_el.get_text(strip=True) if title_el else card.get_text(strip=True)[:80]
                    if not title or len(title) < 3:
                        continue
                    href = card.get("href") or ""
                    if not href:
                        link = card.select_one("a")
                        href = link["href"] if link and link.get("href") else ""
                    job_url = f"https://coodesh.com{href}" if href.startswith("/") else href
                    jobs.append(ScrapedJob(
                        title=title, company="Coodesh", location="Remoto", is_remote=True,
                        description="", url=job_url, external_id=f"coodesh_{hash(job_url)}",
                        source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(), technologies=[],
                    ))
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"CoodeshScraper fallback failed: {e}")
        return jobs

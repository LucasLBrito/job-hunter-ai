"""GeekHunter Scraper - Uses GeekHunter's internal JSON API."""
import logging
from typing import List
from datetime import datetime
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class GeekHunterScraper(BaseScraper):
    PLATFORM_NAME = "geekhunter"
    # GeekHunter exposes a JSON API used internally by their SPA frontend
    API_URL = "https://www.geekhunter.com.br/api/positions"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        logger.info(f"GeekHunterScraper: Searching for '{query}'")
        jobs = []
        try:
            params = {"query": query, "page": 1, "per_page": min(limit, 50)}
            headers = {
                "Accept": "application/json",
                "X-Requested-With": "XMLHttpRequest",
            }
            resp = await self.fetch(
                self.API_URL, params=params, headers=headers,
                referer="https://www.geekhunter.com.br/vagas"
            )
            data = resp.json()
            items = data if isinstance(data, list) else data.get("data", data.get("positions", data.get("results", [])))
            if isinstance(items, dict):
                items = items.get("data", [])
            
            for item in (items or [])[:limit]:
                try:
                    title = item.get("title") or item.get("name") or "N/A"
                    company = item.get("company_name") or item.get("company", {}).get("name", "Confidencial") if isinstance(item.get("company"), dict) else str(item.get("company", "Confidencial"))
                    location = item.get("city") or item.get("location") or "Brasil"
                    is_remote = item.get("remote", False) or "remoto" in str(location).lower()
                    slug = item.get("slug") or item.get("id") or ""
                    job_url = item.get("url") or f"https://www.geekhunter.com.br/vagas/{slug}"
                    desc = item.get("description") or item.get("summary") or ""
                    external_id = f"geekhunter_{item.get('id', hash(job_url))}"
                    jobs.append(ScrapedJob(
                        title=title, company=company, location=location, is_remote=is_remote,
                        description=str(desc)[:3000], url=job_url, external_id=external_id,
                        source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(), technologies=[],
                    ))
                except Exception as e:
                    logger.warning(f"GeekHunterScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"GeekHunterScraper: failed: {e}")
            # Fallback to HTML scraping
            return await self._fallback_html(query, limit)
        logger.info(f"GeekHunterScraper: found {len(jobs)} results for '{query}'")
        return jobs

    async def _fallback_html(self, query: str, limit: int) -> List[ScrapedJob]:
        """Fallback to HTML scraping if JSON API fails."""
        from bs4 import BeautifulSoup
        jobs = []
        try:
            url = f"https://www.geekhunter.com.br/vagas?q={query.replace(' ', '+')}"
            resp = await self.fetch(url, referer="https://www.geekhunter.com.br/")
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select("div[class*='job'], article, a[href*='/vagas/']")
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
                    job_url = f"https://www.geekhunter.com.br{href}" if href.startswith("/") else href
                    jobs.append(ScrapedJob(
                        title=title, company="GeekHunter", location="Brasil", is_remote=False,
                        description="", url=job_url, external_id=f"geekhunter_{hash(job_url)}",
                        source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(), technologies=[],
                    ))
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"GeekHunterScraper fallback failed: {e}")
        return jobs

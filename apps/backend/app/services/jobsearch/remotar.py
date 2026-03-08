"""Remotar Scraper - Uses Remotar's Next.js data or HTML."""
import logging
import json
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class RemotarScraper(BaseScraper):
    PLATFORM_NAME = "remotar"
    BASE_URL = "https://remotar.com.br"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        logger.info(f"RemotarScraper: Searching for '{query}'")
        jobs = []
        try:
            # Try the main jobs page first (more likely to have data)
            for url in [f"{self.BASE_URL}/vagas", f"{self.BASE_URL}/search?query={query.replace(' ', '+')}", self.BASE_URL]:
                try:
                    resp = await self.fetch(url, referer=self.BASE_URL)
                    text = resp.text
                    parsed = self._parse_page(text, query, limit)
                    if parsed:
                        jobs.extend(parsed)
                        break
                except Exception as e:
                    logger.warning(f"RemotarScraper: URL {url} failed: {e}")
                    continue

        except Exception as e:
            logger.error(f"RemotarScraper: failed: {e}")
        logger.info(f"RemotarScraper: found {len(jobs)} results for '{query}'")
        return jobs[:limit]

    def _parse_page(self, text: str, query: str, limit: int) -> List[ScrapedJob]:
        jobs = []
        # Strategy 1: __NEXT_DATA__
        if '__NEXT_DATA__' in text:
            try:
                start = text.find('__NEXT_DATA__')
                script_start = text.find('>', start) + 1
                script_end = text.find('</script>', script_start)
                if script_start > 0 and script_end > script_start:
                    next_data = json.loads(text[script_start:script_end])
                    # Walk through all pageProps looking for job arrays
                    page_props = next_data.get("props", {}).get("pageProps", {})
                    for key, value in page_props.items():
                        if isinstance(value, list) and value and isinstance(value[0], dict):
                            first = value[0]
                            if any(k in first for k in ["title", "name", "cargo", "vaga", "position"]):
                                for item in value[:limit]:
                                    job = self._parse_item(item)
                                    if job:
                                        jobs.append(job)
                                break
            except Exception as e:
                logger.warning(f"RemotarScraper: __NEXT_DATA__ parse error: {e}")

        # Strategy 2: HTML parsing
        if not jobs:
            soup = BeautifulSoup(text, "html.parser")
            # Try various selectors
            cards = (
                soup.select("a[href*='/vaga']") or
                soup.select("a[href*='/job']") or
                soup.select("div[class*='job'], div[class*='vaga'], article")
            )
            seen = set()
            search_lower = query.lower()
            for card in cards[:limit * 3]:
                try:
                    if card.name == "a":
                        href = card.get("href", "")
                        title = card.get_text(strip=True)[:100]
                    else:
                        title_el = card.select_one("h2, h3, h4, [class*='title']")
                        title = title_el.get_text(strip=True) if title_el else ""
                        link = card.select_one("a[href]")
                        href = link["href"] if link else ""

                    if not title or len(title) < 5 or title in seen:
                        continue
                    seen.add(title)
                    job_url = f"{self.BASE_URL}{href}" if href.startswith("/") else (href or self.BASE_URL)
                    external_id = f"remotar_{hash(job_url)}"
                    company_el = card.select_one("[class*='company'], [class*='empresa']")
                    company = company_el.get_text(strip=True) if company_el else "Confidencial"
                    jobs.append(ScrapedJob(
                        title=title, company=company, location="Remoto (Brasil)",
                        is_remote=True, description="", url=job_url,
                        external_id=external_id, source_platform=self.PLATFORM_NAME,
                        posted_at=datetime.utcnow(), technologies=[],
                    ))
                    if len(jobs) >= limit:
                        break
                except Exception:
                    pass
        return jobs

    def _parse_item(self, item: dict):
        try:
            title = item.get("title") or item.get("name") or item.get("cargo") or ""
            if not title:
                return None
            company = item.get("company_name") or item.get("company") or "Confidencial"
            if isinstance(company, dict):
                company = company.get("name", "Confidencial")
            slug = item.get("slug") or item.get("id") or ""
            job_url = item.get("url") or f"{self.BASE_URL}/vaga/{slug}"
            desc = item.get("description") or ""
            external_id = f"remotar_{item.get('id', hash(job_url))}"
            return ScrapedJob(
                title=title, company=str(company), location="Remoto (Brasil)",
                is_remote=True, description=str(desc)[:3000], url=job_url,
                external_id=external_id, source_platform=self.PLATFORM_NAME,
                posted_at=datetime.utcnow(), technologies=[],
            )
        except Exception:
            return None

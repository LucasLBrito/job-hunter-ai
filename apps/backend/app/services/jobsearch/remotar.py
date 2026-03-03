"""Remotar Scraper - Uses Remotar's internal API if available, else HTML."""
import logging
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class RemotarScraper(BaseScraper):
    PLATFORM_NAME = "remotar"
    # Remotar.com.br uses Next.js, we can try their __NEXT_DATA__ or direct page
    BASE_URL = "https://remotar.com.br"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        logger.info(f"RemotarScraper: Searching for '{query}'")
        jobs = []
        try:
            # Try the search page and extract Next.js data
            url = f"{self.BASE_URL}/search?query={query.replace(' ', '+')}"
            resp = await self.fetch(url, referer=self.BASE_URL)
            text = resp.text

            # Try extracting __NEXT_DATA__ JSON embedded in the page
            import json
            if '__NEXT_DATA__' in text:
                start = text.find('__NEXT_DATA__')
                script_start = text.find('>', start) + 1
                script_end = text.find('</script>', script_start)
                if script_start > 0 and script_end > script_start:
                    next_data = json.loads(text[script_start:script_end])
                    page_props = next_data.get("props", {}).get("pageProps", {})
                    items = page_props.get("jobs", page_props.get("vacancies", page_props.get("results", [])))
                    for item in (items or [])[:limit]:
                        try:
                            title = item.get("title") or item.get("name") or "N/A"
                            company = item.get("company_name") or item.get("company", "Confidencial")
                            slug = item.get("slug") or item.get("id") or ""
                            job_url = item.get("url") or f"{self.BASE_URL}/vaga/{slug}"
                            desc = item.get("description") or ""
                            external_id = f"remotar_{item.get('id', hash(job_url))}"
                            jobs.append(ScrapedJob(
                                title=title, company=str(company), location="Remoto (Brasil)",
                                is_remote=True, description=str(desc)[:3000], url=job_url,
                                external_id=external_id, source_platform=self.PLATFORM_NAME,
                                posted_at=datetime.utcnow(), technologies=[],
                            ))
                        except Exception as e:
                            logger.warning(f"RemotarScraper: parse error: {e}")

            # If no __NEXT_DATA__ results, fallback to HTML parsing
            if not jobs:
                soup = BeautifulSoup(text, "html.parser")
                cards = soup.select("a[href*='/vaga/'], a[href*='/job/'], article, div[class*='job']")
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
                        job_url = f"{self.BASE_URL}{href}" if href.startswith("/") else (href or url)
                        company_el = card.select_one("[class*='company']")
                        company = company_el.get_text(strip=True) if company_el else "Confidencial"
                        external_id = f"remotar_{hash(job_url)}"
                        jobs.append(ScrapedJob(
                            title=title, company=company, location="Remoto (Brasil)",
                            is_remote=True, description="", url=job_url,
                            external_id=external_id, source_platform=self.PLATFORM_NAME,
                            posted_at=datetime.utcnow(), technologies=[],
                        ))
                    except Exception:
                        pass

        except Exception as e:
            logger.error(f"RemotarScraper: failed: {e}")
        logger.info(f"RemotarScraper: found {len(jobs)} results for '{query}'")
        return jobs

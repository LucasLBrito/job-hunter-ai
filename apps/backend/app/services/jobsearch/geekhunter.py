"""GeekHunter Scraper - Uses GeekHunter's pages and API."""
import logging
import json
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class GeekHunterScraper(BaseScraper):
    PLATFORM_NAME = "geekhunter"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        logger.info(f"GeekHunterScraper: Searching for '{query}'")
        jobs = []
        try:
            # Try the vagas page with search
            url = f"https://www.geekhunter.com.br/vagas?q={query.replace(' ', '+')}"
            resp = await self.fetch(url, referer="https://www.geekhunter.com.br/")
            text = resp.text

            # Strategy 1: __NEXT_DATA__
            if '__NEXT_DATA__' in text:
                try:
                    soup_temp = BeautifulSoup(text, "html.parser")
                    script = soup_temp.find("script", id="__NEXT_DATA__")
                    if script:
                        next_data = json.loads(script.string)
                        page_props = next_data.get("props", {}).get("pageProps", {})
                        for key, value in page_props.items():
                            if isinstance(value, list) and value and isinstance(value[0], dict):
                                first = value[0]
                                if any(k in first for k in ["title", "name", "position"]):
                                    for item in value[:limit]:
                                        title = item.get("title") or item.get("name") or ""
                                        if not title:
                                            continue
                                        company = item.get("company_name") or item.get("company", "Confidencial")
                                        if isinstance(company, dict):
                                            company = company.get("name", "Confidencial")
                                        slug = item.get("slug") or item.get("id") or ""
                                        job_url = item.get("url") or f"https://www.geekhunter.com.br/vagas/{slug}"
                                        jobs.append(ScrapedJob(
                                            title=title, company=str(company),
                                            location=item.get("city", "Brasil"),
                                            is_remote=item.get("remote", False),
                                            description=str(item.get("description", ""))[:3000],
                                            url=job_url,
                                            external_id=f"geekhunter_{item.get('id', hash(job_url))}",
                                            source_platform=self.PLATFORM_NAME,
                                            posted_at=datetime.utcnow(), technologies=[],
                                        ))
                                    break
                except Exception as e:
                    logger.warning(f"GeekHunterScraper: __NEXT_DATA__ error: {e}")

            # Strategy 2: HTML parsing
            if not jobs:
                soup = BeautifulSoup(text, "html.parser")
                cards = (
                    soup.select("a[href*='/vagas/']") or
                    soup.select("div[class*='job'], article, div[class*='position']")
                )
                seen = set()
                for card in cards[:limit * 2]:
                    try:
                        if card.name == "a":
                            title = card.get_text(strip=True)[:100]
                            href = card.get("href", "")
                        else:
                            title_el = card.select_one("h2, h3, a")
                            title = title_el.get_text(strip=True) if title_el else ""
                            link = card.select_one("a[href]")
                            href = link["href"] if link else ""
                        if not title or len(title) < 5 or title in seen:
                            continue
                        seen.add(title)
                        job_url = f"https://www.geekhunter.com.br{href}" if href.startswith("/") else href
                        jobs.append(ScrapedJob(
                            title=title, company="GeekHunter", location="Brasil",
                            is_remote=False, description="", url=job_url,
                            external_id=f"geekhunter_{hash(job_url)}",
                            source_platform=self.PLATFORM_NAME,
                            posted_at=datetime.utcnow(), technologies=[],
                        ))
                        if len(jobs) >= limit:
                            break
                    except Exception:
                        pass

        except Exception as e:
            logger.error(f"GeekHunterScraper: failed: {e}")
        logger.info(f"GeekHunterScraper: found {len(jobs)} results for '{query}'")
        return jobs

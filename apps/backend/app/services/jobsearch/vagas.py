"""Vagas.com.br Scraper - HTML scraping with BeautifulSoup."""
import logging
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class VagasScraper(BaseScraper):
    PLATFORM_NAME = "vagas.com.br"
    BASE_URL = "https://www.vagas.com.br/vagas-de"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        query_formatted = query.replace(" ", "-")
        url = f"{self.BASE_URL}-{query_formatted}"
        logger.info(f"VagasScraper: Searching '{query}' at {url}")
        jobs = []
        try:
            resp = await self.fetch(url, referer="https://www.vagas.com.br/")
            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.select("a.link-detalhes-vaga")
            for a in job_cards[:limit]:
                try:
                    title = a.get_text(strip=True)
                    job_url = "https://www.vagas.com.br" + a.get("href", "")
                    parent = a.find_parent("li")
                    if not parent:
                        continue
                    company_elem = parent.find(class_="empresa")
                    company = company_elem.get_text(strip=True) if company_elem else "Nao revelado"
                    loc_elem = parent.find(class_="vaga-local")
                    location = loc_elem.get_text(strip=True) if loc_elem else "Brasil"
                    is_remote = "remoto" in location.lower() or "home office" in location.lower()
                    desc_elem = parent.find(class_="detalhes")
                    desc_preview = desc_elem.get_text(strip=True) if desc_elem else ""
                    external_id = f"{self.PLATFORM_NAME}_{hash(job_url)}"
                    jobs.append(ScrapedJob(
                        title=title, company=company, location=location, is_remote=is_remote,
                        description=desc_preview, url=job_url, external_id=external_id,
                        source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(),
                        technologies=[],
                    ))
                except Exception as e:
                    logger.warning(f"VagasScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"VagasScraper: failed: {e}")
        logger.info(f"VagasScraper: found {len(jobs)} results for '{query}'")
        return jobs

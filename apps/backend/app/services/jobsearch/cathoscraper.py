"""Catho Scraper - HTML scraping from catho.com.br."""
import logging
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class CathoScraper(BaseScraper):
    PLATFORM_NAME = "catho"
    BASE_URL = "https://www.catho.com.br/vagas"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        url = f"{self.BASE_URL}/?q={query}"
        logger.info(f"CathoScraper: Searching for '{query}'")
        jobs = []
        try:
            resp = await self.fetch(url, referer="https://www.catho.com.br/")
            soup = BeautifulSoup(resp.text, "html.parser")

            job_lists = soup.find("ul", class_=lambda x: x and "gtm-job-list" in x) or soup.find("ul", {"id": "search-result"})
            if not job_lists:
                job_cards = soup.find_all("article")
            else:
                job_cards = job_lists.find_all("li")

            logger.info(f"CathoScraper: found {len(job_cards)} candidate cards")
            for card in job_cards[:limit]:
                try:
                    job = self._parse_job_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.warning(f"CathoScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"CathoScraper: failed: {e}")
        logger.info(f"CathoScraper: returning {len(jobs)} jobs")
        return jobs

    def _parse_job_card(self, card) -> Optional[ScrapedJob]:
        title_elem = card.find("h2")
        if not title_elem:
            return None
        link_elem = title_elem.find("a")
        if not link_elem:
            return None
        title = title_elem.get_text(strip=True)
        job_url = link_elem.get("href", "")
        external_id = f"{self.PLATFORM_NAME}_{hash(job_url)}"

        company = "Nao revelado (Catho)"
        company_candidate = card.find("span", attrs={"data-gtm-element": "job-company-name"})
        if company_candidate:
            company = company_candidate.get_text(strip=True)

        salary_min = salary_max = None
        salary_elem = card.find(string=lambda s: s and "R$" in s)
        if salary_elem:
            sal_text = str(salary_elem).replace(".", "").replace(",", ".").replace("R$", "")
            parts = [p.strip() for p in sal_text.split("a") if p.strip().replace(".", "", 1).isdigit()]
            try:
                if parts:
                    salary_min = int(float(parts[0]))
                    salary_max = int(float(parts[-1])) if len(parts) > 1 else salary_min
            except Exception:
                pass

        location = "Brasil"
        is_remote = False
        loc_elem = card.find("a", href=lambda h: h and "/vagas/" in h)
        if loc_elem:
            location = loc_elem.get_text(strip=True)
        if "Home Office" in card.get_text() or "Remoto" in card.get_text():
            is_remote = True

        desc_preview = ""
        desc_elem = card.find("span", class_=lambda x: x and "job-description" in x)
        if not desc_elem:
            desc_elem = card.find("div", class_=lambda x: x and "job-description" in x)
        if desc_elem:
            desc_preview = desc_elem.get_text(strip=True)
        else:
            desc_preview = card.get_text(separator=" ", strip=True)[:300] + "..."

        return ScrapedJob(
            title=title, company=company, location=location, is_remote=is_remote,
            salary_min=salary_min, salary_max=salary_max, salary_currency="BRL",
            description=desc_preview,
            url=job_url if job_url.startswith("http") else f"https://www.catho.com.br{job_url}",
            external_id=external_id, source_platform=self.PLATFORM_NAME,
            posted_at=datetime.utcnow(), technologies=[],
        )

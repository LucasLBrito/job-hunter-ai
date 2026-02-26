"""
Scrapers TI Brasil — ProgramaThor, GeekHunter, Coodesh, APInfo
Todos usam BeautifulSoup + httpx async seguindo o padrão BaseScraper.
"""
import logging
import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime

from app.services.scrapers.base import BaseScraper
from app.services.scrapers.models import ScrapedJob

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


class ProgramaThorScraper(BaseScraper):
    PLATFORM_NAME = "programathor"
    BASE_URL = "https://programathor.com.br/jobs"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        url = f"{self.BASE_URL}?search={query.replace(' ', '+')}"
        jobs: List[ScrapedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=HEADERS)
                if resp.status_code != 200:
                    logger.warning(f"ProgramaThorScraper: HTTP {resp.status_code}")
                    return []
                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("div.cell-list")
                for card in cards[:limit]:
                    try:
                        title_el = card.select_one("h3") or card.select_one("h2")
                        title = title_el.get_text(strip=True) if title_el else "N/A"
                        company_el = card.select_one("h4") or card.select_one(".company")
                        company = company_el.get_text(strip=True) if company_el else "Confidencial"
                        link_el = card.select_one("a")
                        href = link_el["href"] if link_el and link_el.get("href") else ""
                        job_url = f"https://programathor.com.br{href}" if href.startswith("/") else href
                        location_el = card.select_one(".location") or card.select_one(".city")
                        location = location_el.get_text(strip=True) if location_el else "Brasil"
                        is_remote = "remoto" in location.lower() or "home office" in location.lower()
                        desc_el = card.select_one(".description") or card.select_one("p")
                        desc = desc_el.get_text(strip=True) if desc_el else ""
                        external_id = f"programathor_{hash(job_url)}"
                        jobs.append(ScrapedJob(
                            title=title, company=company, location=location, is_remote=is_remote,
                            description=desc, url=job_url, external_id=external_id,
                            source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(),
                            employment_type=None, technologies=[],
                        ))
                    except Exception as e:
                        logger.warning(f"ProgramaThorScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"ProgramaThorScraper: request failed: {e}")
        logger.info(f"ProgramaThorScraper: found {len(jobs)} results for '{query}'")
        return jobs

    async def get_job_details(self, job_url: str) -> Optional[ScrapedJob]:
        return None


class GeekHunterScraper(BaseScraper):
    PLATFORM_NAME = "geekhunter"
    BASE_URL = "https://www.geekhunter.com.br/vagas"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        url = f"{self.BASE_URL}?q={query.replace(' ', '+')}"
        jobs: List[ScrapedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=HEADERS)
                if resp.status_code != 200:
                    logger.warning(f"GeekHunterScraper: HTTP {resp.status_code}")
                    return []
                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("div.job-listing-item, article.job-card, div[class*='job']")
                for card in cards[:limit]:
                    try:
                        title_el = card.select_one("h2, h3, .job-title, [class*='title']")
                        title = title_el.get_text(strip=True) if title_el else "N/A"
                        company_el = card.select_one(".company, [class*='company']")
                        company = company_el.get_text(strip=True) if company_el else "Confidencial"
                        link_el = card.select_one("a")
                        href = link_el["href"] if link_el and link_el.get("href") else ""
                        job_url = f"https://www.geekhunter.com.br{href}" if href.startswith("/") else href
                        location_el = card.select_one(".location, [class*='location']")
                        location = location_el.get_text(strip=True) if location_el else "Brasil"
                        is_remote = "remoto" in location.lower()
                        desc_el = card.select_one("p, .description")
                        desc = desc_el.get_text(strip=True) if desc_el else ""
                        external_id = f"geekhunter_{hash(job_url)}"
                        jobs.append(ScrapedJob(
                            title=title, company=company, location=location, is_remote=is_remote,
                            description=desc, url=job_url, external_id=external_id,
                            source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(),
                            employment_type=None, technologies=[],
                        ))
                    except Exception as e:
                        logger.warning(f"GeekHunterScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"GeekHunterScraper: request failed: {e}")
        logger.info(f"GeekHunterScraper: found {len(jobs)} results for '{query}'")
        return jobs

    async def get_job_details(self, job_url: str) -> Optional[ScrapedJob]:
        return None


class CoodeshScraper(BaseScraper):
    PLATFORM_NAME = "coodesh"
    BASE_URL = "https://coodesh.com/vagas"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        url = f"{self.BASE_URL}?search={query.replace(' ', '+')}"
        jobs: List[ScrapedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=HEADERS)
                if resp.status_code != 200:
                    logger.warning(f"CoodeshScraper: HTTP {resp.status_code}")
                    return []
                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("div.vacancy-card, article, div[class*='card']")
                for card in cards[:limit]:
                    try:
                        title_el = card.select_one("h2, h3, [class*='title']")
                        title = title_el.get_text(strip=True) if title_el else "N/A"
                        company_el = card.select_one("[class*='company']")
                        company = company_el.get_text(strip=True) if company_el else "Confidencial"
                        link_el = card.select_one("a")
                        href = link_el["href"] if link_el and link_el.get("href") else ""
                        job_url = f"https://coodesh.com{href}" if href.startswith("/") else (href or url)
                        location_el = card.select_one("[class*='location']")
                        location = location_el.get_text(strip=True) if location_el else "Remoto"
                        is_remote = "remoto" in location.lower() or location == "Remoto"
                        desc_el = card.select_one("p")
                        desc = desc_el.get_text(strip=True) if desc_el else ""
                        external_id = f"coodesh_{hash(job_url)}"
                        jobs.append(ScrapedJob(
                            title=title, company=company, location=location, is_remote=is_remote,
                            description=desc, url=job_url, external_id=external_id,
                            source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(),
                            employment_type=None, technologies=[],
                        ))
                    except Exception as e:
                        logger.warning(f"CoodeshScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"CoodeshScraper: request failed: {e}")
        logger.info(f"CoodeshScraper: found {len(jobs)} results for '{query}'")
        return jobs

    async def get_job_details(self, job_url: str) -> Optional[ScrapedJob]:
        return None


class APInfoScraper(BaseScraper):
    PLATFORM_NAME = "apinfo"
    BASE_URL = "https://www.apinfo.com/apinfo/asp/formvagas.cfm"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        params = {"texto": query, "acao": "listar"}
        jobs: List[ScrapedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(self.BASE_URL, params=params, headers=HEADERS)
                if resp.status_code != 200:
                    logger.warning(f"APInfoScraper: HTTP {resp.status_code}")
                    return []
                soup = BeautifulSoup(resp.text, "html.parser")
                rows = soup.select("table tr")
                for row in rows[:limit]:
                    try:
                        cells = row.select("td")
                        if len(cells) < 2:
                            continue
                        title = cells[0].get_text(strip=True)
                        if not title or title.lower() in ("cargo", "função"):
                            continue
                        company = cells[1].get_text(strip=True) if len(cells) > 1 else "Confidencial"
                        link_el = cells[0].select_one("a") or row.select_one("a")
                        href = link_el["href"] if link_el and link_el.get("href") else ""
                        job_url = f"https://www.apinfo.com{href}" if href.startswith("/") else (href or self.BASE_URL)
                        location = cells[2].get_text(strip=True) if len(cells) > 2 else "Brasil"
                        is_remote = "remoto" in location.lower()
                        external_id = f"apinfo_{hash(job_url)}"
                        jobs.append(ScrapedJob(
                            title=title, company=company, location=location, is_remote=is_remote,
                            description="", url=job_url, external_id=external_id,
                            source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(),
                            employment_type=None, technologies=[],
                        ))
                    except Exception as e:
                        logger.warning(f"APInfoScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"APInfoScraper: request failed: {e}")
        logger.info(f"APInfoScraper: found {len(jobs)} results for '{query}'")
        return jobs

    async def get_job_details(self, job_url: str) -> Optional[ScrapedJob]:
        return None

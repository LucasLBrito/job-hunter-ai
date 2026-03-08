"""Catho Scraper - Uses Catho's internal search API (JSON)."""
import logging
import json
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class CathoScraper(BaseScraper):
    PLATFORM_NAME = "catho"
    # Catho's SPA uses an internal GraphQL/REST API
    SEARCH_URL = "https://www.catho.com.br/vagas"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        logger.info(f"CathoScraper: Searching for '{query}'")
        jobs = []

        try:
            # Try Catho's internal API first (their SPA uses this)
            api_url = "https://api-vagas.catho.com.br/v2/vagas"
            params = {"q": query, "page": 1, "order": "relevancia", "tamanhoPagina": min(limit, 50)}
            headers = {
                "Accept": "application/json",
                "Origin": "https://www.catho.com.br",
            }
            try:
                resp = await self.fetch(api_url, params=params, headers=headers, referer="https://www.catho.com.br/vagas/")
                data = resp.json()
                items = data.get("vagas", data.get("data", data.get("results", [])))
                if isinstance(items, dict):
                    items = items.get("vagas", items.get("data", []))
                for item in (items or [])[:limit]:
                    try:
                        title = item.get("cargo", item.get("titulo", item.get("title", "N/A")))
                        company = item.get("empresa", item.get("company", "Confidencial"))
                        if isinstance(company, dict):
                            company = company.get("nome", company.get("name", "Confidencial"))
                        location = item.get("cidade", item.get("localizacao", "Brasil"))
                        if isinstance(location, dict):
                            location = location.get("nome", "Brasil")
                        is_remote = item.get("homeOffice", False) or "remoto" in str(location).lower()
                        desc = item.get("descricao", item.get("description", ""))
                        slug = item.get("id", item.get("idVaga", ""))
                        job_url = item.get("url", f"https://www.catho.com.br/vagas/{slug}")
                        external_id = f"catho_{slug or hash(job_url)}"
                        salary_min = item.get("salarioMinimo", item.get("faixaSalarial", {}).get("minimo"))
                        salary_max = item.get("salarioMaximo", item.get("faixaSalarial", {}).get("maximo"))
                        try:
                            salary_min = int(float(salary_min)) if salary_min else None
                            salary_max = int(float(salary_max)) if salary_max else None
                        except (ValueError, TypeError):
                            salary_min = salary_max = None
                        jobs.append(ScrapedJob(
                            title=title, company=str(company), location=str(location),
                            is_remote=is_remote, salary_min=salary_min, salary_max=salary_max,
                            salary_currency="BRL", description=str(desc)[:3000],
                            url=job_url, external_id=external_id,
                            source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(),
                            technologies=[],
                        ))
                    except Exception as e:
                        logger.warning(f"CathoScraper: parse error: {e}")
                if jobs:
                    logger.info(f"CathoScraper (API): found {len(jobs)} results")
                    return jobs
            except Exception as e:
                logger.info(f"CathoScraper: API failed ({e}), trying HTML")

            # Fallback to HTML scraping
            url = f"{self.SEARCH_URL}/?q={query}"
            resp = await self.fetch(url, referer="https://www.catho.com.br/")
            soup = BeautifulSoup(resp.text, "html.parser")

            # Try __NEXT_DATA__ first (if Catho uses Next.js)
            script = soup.find("script", id="__NEXT_DATA__")
            if script:
                try:
                    next_data = json.loads(script.string)
                    page_props = next_data.get("props", {}).get("pageProps", {})
                    items = page_props.get("jobs", page_props.get("vagas", []))
                    for item in (items or [])[:limit]:
                        title = item.get("cargo", item.get("title", "N/A"))
                        company = item.get("empresa", "Confidencial")
                        if isinstance(company, dict):
                            company = company.get("nome", "Confidencial")
                        job_url = item.get("url", "")
                        external_id = f"catho_{item.get('id', hash(job_url))}"
                        jobs.append(ScrapedJob(
                            title=title, company=str(company), location="Brasil",
                            is_remote=False, description="",
                            url=job_url, external_id=external_id,
                            source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(),
                            technologies=[],
                        ))
                    if jobs:
                        logger.info(f"CathoScraper (__NEXT_DATA__): found {len(jobs)} results")
                        return jobs
                except Exception:
                    pass

            # Broad HTML parsing
            job_cards = soup.select("article, li[class*='job'], div[class*='job-card'], div[class*='vaga']")
            for card in job_cards[:limit]:
                try:
                    title_el = card.select_one("h2, h3, a[class*='title']")
                    if not title_el:
                        continue
                    title = title_el.get_text(strip=True)
                    if not title or len(title) < 3:
                        continue
                    link = card.select_one("a[href]")
                    href = link["href"] if link else ""
                    job_url = href if href.startswith("http") else f"https://www.catho.com.br{href}"
                    company_el = card.select_one("[class*='company'], [class*='empresa']")
                    company = company_el.get_text(strip=True) if company_el else "Confidencial"
                    external_id = f"catho_{hash(job_url)}"
                    jobs.append(ScrapedJob(
                        title=title, company=company, location="Brasil",
                        is_remote="remoto" in card.get_text().lower(),
                        description=card.get_text(strip=True)[:300],
                        url=job_url, external_id=external_id,
                        source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(),
                        technologies=[],
                    ))
                except Exception:
                    pass

        except Exception as e:
            logger.error(f"CathoScraper: failed: {e}")
        logger.info(f"CathoScraper: returning {len(jobs)} jobs")
        return jobs

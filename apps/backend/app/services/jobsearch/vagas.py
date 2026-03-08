"""Vagas.com.br Scraper - HTML scraping with multiple selector strategies."""
import logging
import json
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

            # Try __NEXT_DATA__ first
            script = soup.find("script", id="__NEXT_DATA__")
            if script:
                try:
                    next_data = json.loads(script.string)
                    page_props = next_data.get("props", {}).get("pageProps", {})
                    items = page_props.get("jobs", page_props.get("vagas", page_props.get("results", [])))
                    for item in (items or [])[:limit]:
                        title = item.get("titulo", item.get("title", "N/A"))
                        company = item.get("empresa", item.get("company", "Confidencial"))
                        if isinstance(company, dict):
                            company = company.get("nome", "Confidencial")
                        location = item.get("cidade", item.get("location", "Brasil"))
                        job_url = item.get("url", item.get("link", ""))
                        if not job_url.startswith("http"):
                            job_url = f"https://www.vagas.com.br{job_url}"
                        external_id = f"vagas_{item.get('id', hash(job_url))}"
                        jobs.append(ScrapedJob(
                            title=title, company=str(company), location=str(location),
                            is_remote="remoto" in str(location).lower(),
                            description=item.get("descricao", "")[:3000],
                            url=job_url, external_id=external_id,
                            source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(),
                            technologies=[],
                        ))
                    if jobs:
                        logger.info(f"VagasScraper (__NEXT_DATA__): found {len(jobs)} results")
                        return jobs
                except Exception as e:
                    logger.warning(f"VagasScraper: __NEXT_DATA__ parse error: {e}")

            # Strategy 1: Original selectors
            job_cards = soup.select("a.link-detalhes-vaga")
            if not job_cards:
                # Strategy 2: Updated selectors
                job_cards = soup.select("header.info-header a, h2.cargo a, a[href*='/vagas/']")
            if not job_cards:
                # Strategy 3: Broad selectors
                job_cards = soup.select("li.vaga, div.vaga, article")

            seen = set()
            for elem in job_cards[:limit * 2]:
                try:
                    if elem.name == "a":
                        title = elem.get_text(strip=True)
                        href = elem.get("href", "")
                        parent = elem.find_parent("li") or elem.find_parent("div") or elem.find_parent("article")
                    else:
                        title_el = elem.select_one("a.link-detalhes-vaga, h2 a, h3 a, a[href*='/vagas/']")
                        if not title_el:
                            continue
                        title = title_el.get_text(strip=True)
                        href = title_el.get("href", "")
                        parent = elem

                    if not title or len(title) < 3 or title in seen:
                        continue
                    seen.add(title)

                    job_url = f"https://www.vagas.com.br{href}" if href.startswith("/") else href
                    company = "Confidencial"
                    if parent:
                        company_el = parent.select_one(".emprVaga, .empresa, span[class*='empresa'], [class*='company']")
                        if company_el:
                            company = company_el.get_text(strip=True)
                    location = "Brasil"
                    if parent:
                        loc_el = parent.select_one(".vaga-local, [class*='local'], [class*='location']")
                        if loc_el:
                            location = loc_el.get_text(strip=True)
                    is_remote = "remoto" in location.lower() or "home office" in location.lower()
                    desc = ""
                    if parent:
                        desc_el = parent.select_one(".detalhes, [class*='descricao'], p")
                        if desc_el:
                            desc = desc_el.get_text(strip=True)
                    external_id = f"vagas_{hash(job_url)}"
                    jobs.append(ScrapedJob(
                        title=title, company=company, location=location, is_remote=is_remote,
                        description=desc[:3000], url=job_url, external_id=external_id,
                        source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(),
                        technologies=[],
                    ))
                    if len(jobs) >= limit:
                        break
                except Exception as e:
                    logger.warning(f"VagasScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"VagasScraper: failed: {e}")
        logger.info(f"VagasScraper: found {len(jobs)} results for '{query}'")
        return jobs

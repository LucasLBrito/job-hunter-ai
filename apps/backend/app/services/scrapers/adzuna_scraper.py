import httpx
import logging
from typing import List, Optional
from datetime import datetime

from app.services.scrapers.base import BaseScraper
from app.services.scrapers.models import ScrapedJob
from app.core.config import settings

logger = logging.getLogger(__name__)


class AdzunaScraper(BaseScraper):
    """
    Scraper for Adzuna API.
    Adzuna aggregates jobs from thousands of sources including:
    - Vagas.com.br, Catho, InfoJobs (Brazil)
    - International job boards
    
    Requires free API key from developer.adzuna.com
    """

    BASE_URL = "https://api.adzuna.com/v1/api/jobs"
    
    # Supported countries with their codes
    COUNTRIES = {
        "br": "Brazil",
        "us": "United States", 
        "gb": "United Kingdom",
        "de": "Germany",
        "ca": "Canada",
    }

    def __init__(self):
        self.app_id = getattr(settings, "ADZUNA_APP_ID", None)
        self.app_key = getattr(settings, "ADZUNA_APP_KEY", None)

    @property
    def is_configured(self) -> bool:
        return bool(self.app_id and self.app_key)

    async def search_jobs(self, query: str, limit: int = 10, country: str = "br") -> List[ScrapedJob]:
        """Search Adzuna API for jobs."""
        if not self.is_configured:
            logger.warning("Adzuna: Not configured (missing ADZUNA_APP_ID/ADZUNA_APP_KEY). Skipping.")
            return []

        logger.info(f"Adzuna: Searching for '{query}' in {country}")

        jobs = []
        try:
            url = f"{self.BASE_URL}/{country}/search/1"
            params = {
                "app_id": self.app_id,
                "app_key": self.app_key,
                "results_per_page": min(limit, 50),
                "what": query,
                "content-type": "application/json",
            }

            proxy_url = settings.SCRAPER_PROXY_URL if settings.SCRAPER_PROXY_URL else None
            async with httpx.AsyncClient(proxy=proxy_url) as client:
                response = await client.get(url, params=params, timeout=15.0)
                response.raise_for_status()
                data = response.json()

            results = data.get("results", [])
            logger.info(f"Adzuna: Found {len(results)} results")

            for item in results:
                try:
                    job = self._parse_result(item, country)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.warning(f"Adzuna: Failed to parse result: {e}")
                    continue

        except httpx.HTTPStatusError as e:
            logger.error(f"Adzuna API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Adzuna scraper failed: {e}")

        return jobs

    def _parse_result(self, item: dict, country: str) -> Optional[ScrapedJob]:
        """Parse Adzuna API result into ScrapedJob."""
        title = item.get("title", "").strip()
        company_data = item.get("company", {})
        company = company_data.get("display_name", "Unknown") if isinstance(company_data, dict) else str(company_data)

        if not title or not company:
            return None

        # Location
        location_data = item.get("location", {})
        location_parts = []
        if isinstance(location_data, dict):
            for area in location_data.get("area", []):
                location_parts.append(area)
            display_name = location_data.get("display_name", "")
            if display_name and not location_parts:
                location_parts = [display_name]
        location = ", ".join(location_parts) if location_parts else self.COUNTRIES.get(country, country)

        # Description
        description = item.get("description", title)

        # URL
        url = item.get("redirect_url", item.get("url", ""))

        # External ID
        external_id = f"adzuna_{item.get('id', hash(url))}"

        # Salary
        salary_min = None
        salary_max = None
        try:
            if item.get("salary_min"):
                salary_min = int(float(item["salary_min"]))
            if item.get("salary_max"):
                salary_max = int(float(item["salary_max"]))
        except (ValueError, TypeError):
            pass

        # Remote check
        is_remote = False
        title_lower = title.lower()
        desc_lower = description.lower()
        if any(kw in title_lower or kw in desc_lower for kw in ["remote", "remoto", "home office", "trabalho remoto"]):
            is_remote = True

        # Posted date
        posted_at = None
        try:
            created = item.get("created")
            if created:
                posted_at = datetime.fromisoformat(created.replace("Z", "+00:00"))
        except Exception:
            pass

        # Contract type
        contract_type = item.get("contract_type", "")
        
        # Category
        category = item.get("category", {})
        category_label = category.get("label", "") if isinstance(category, dict) else ""

        return ScrapedJob(
            title=title,
            company=company,
            location=location,
            is_remote=is_remote,
            salary_min=salary_min,
            salary_max=salary_max,
            salary_currency="BRL" if country == "br" else "USD",
            description=description[:5000],
            url=url,
            external_id=external_id,
            source_platform="adzuna",
            posted_at=posted_at,
            employment_type=contract_type,
            technologies=[],
        )

    async def get_job_details(self, job_url: str) -> Optional[ScrapedJob]:
        """Not needed — search returns full details."""
        return None

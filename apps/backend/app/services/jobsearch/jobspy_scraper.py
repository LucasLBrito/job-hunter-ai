"""JobSpy Scraper - Uses python-jobspy library (LinkedIn, Indeed, Glassdoor, etc.)."""
import logging
import asyncio
from typing import List, Optional
from datetime import datetime
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class JobSpyScraper(BaseScraper):
    PLATFORM_NAME = "jobspy"
    PLATFORMS = ["indeed", "linkedin", "glassdoor", "google", "zip_recruiter"]

    async def search_jobs(self, query: str, limit: int = 10, location: str = "Brazil") -> List[ScrapedJob]:
        logger.info(f"JobSpyScraper: Searching for '{query}' across {self.PLATFORMS}")
        try:
            results = await asyncio.to_thread(self._scrape_sync, query, limit, location)
            logger.info(f"JobSpyScraper: Found {len(results)} jobs")
            return results
        except Exception as e:
            logger.error(f"JobSpyScraper: failed: {e}")
            return []

    def _scrape_sync(self, query: str, limit: int, location: str) -> List[ScrapedJob]:
        from jobspy import scrape_jobs
        from app.core.config import settings
        jobs = []
        for platform in self.PLATFORMS:
            try:
                logger.info(f"JobSpyScraper: Scraping {platform}...")
                proxies = [settings.SCRAPER_PROXY_URL] if settings.SCRAPER_PROXY_URL else None
                df = scrape_jobs(
                    site_name=[platform], search_term=query, location=location,
                    results_wanted=min(limit, 15), hours_old=72,
                    country_indeed="Brazil" if platform == "indeed" else None,
                    proxies=proxies,
                )
                if df is None or df.empty:
                    continue
                for _, row in df.iterrows():
                    try:
                        job = self._row_to_scraped_job(row, platform)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.warning(f"JobSpyScraper: parse row error ({platform}): {e}")
                logger.info(f"JobSpyScraper: Got {len(df)} results from {platform}")
            except Exception as e:
                logger.warning(f"JobSpyScraper: Platform {platform} failed: {e}")
        return jobs

    def _row_to_scraped_job(self, row, platform: str) -> Optional[ScrapedJob]:
        title = str(row.get("title", "")).strip()
        company = str(row.get("company_name", row.get("company", ""))).strip()
        if not title or not company or title == "nan" or company == "nan":
            return None
        job_url = str(row.get("job_url", row.get("link", "")))
        external_id = f"{platform}_{hash(job_url)}"
        location = str(row.get("location", ""))
        if location == "nan":
            location = ""
        is_remote = bool(row.get("is_remote", False))
        if not is_remote:
            is_remote = "remote" in location.lower() or "remoto" in location.lower()
        salary_min = salary_max = None
        try:
            sal_min = row.get("min_amount", row.get("salary_min"))
            sal_max = row.get("max_amount", row.get("salary_max"))
            if sal_min and str(sal_min) != "nan":
                salary_min = int(float(sal_min))
            if sal_max and str(sal_max) != "nan":
                salary_max = int(float(sal_max))
        except (ValueError, TypeError):
            pass
        salary_currency = str(row.get("currency", "BRL"))
        if salary_currency == "nan":
            salary_currency = "BRL"
        description = str(row.get("description", ""))
        if description == "nan":
            description = title
        posted_at = None
        try:
            date_val = row.get("date_posted")
            if date_val and str(date_val) not in ("nan", "NaT"):
                posted_at = date_val if isinstance(date_val, datetime) else datetime.fromisoformat(str(date_val))
        except Exception:
            pass
        job_type = str(row.get("job_type", ""))
        if job_type == "nan":
            job_type = ""
        return ScrapedJob(
            title=title, company=company,
            location=location or "Not specified", is_remote=is_remote,
            salary_min=salary_min, salary_max=salary_max, salary_currency=salary_currency,
            description=description[:5000],
            url=job_url if job_url != "nan" else "",
            external_id=external_id, source_platform=platform,
            posted_at=posted_at, employment_type=job_type, technologies=[],
        )

import logging
import asyncio
from typing import List, Optional
from datetime import datetime

from app.services.scrapers.base import BaseScraper
from app.services.scrapers.models import ScrapedJob

logger = logging.getLogger(__name__)


class JobSpyScraper(BaseScraper):
    """
    Scraper that uses python-jobspy to aggregate jobs from:
    - LinkedIn
    - Indeed
    - Glassdoor
    - Google Jobs
    - ZipRecruiter
    """

    # Platforms to search (all supported by jobspy)
    PLATFORMS = ["indeed", "linkedin", "glassdoor", "google", "zip_recruiter"]

    async def search_jobs(self, query: str, limit: int = 10, location: str = "Brazil") -> List[ScrapedJob]:
        """Search across multiple platforms using python-jobspy."""
        logger.info(f"JobSpy: Searching for '{query}' across {self.PLATFORMS}")

        try:
            # jobspy is sync, run in thread pool
            results = await asyncio.to_thread(
                self._scrape_sync, query, limit, location
            )
            logger.info(f"JobSpy: Found {len(results)} jobs for '{query}'")
            return results
        except Exception as e:
            logger.error(f"JobSpy scraper failed: {e}")
            return []

    def _scrape_sync(self, query: str, limit: int, location: str) -> List[ScrapedJob]:
        """Synchronous scraping wrapper for jobspy."""
        from jobspy import scrape_jobs

        jobs = []

        # Search each platform individually for better error isolation
        for platform in self.PLATFORMS:
            try:
                logger.info(f"JobSpy: Scraping {platform}...")
                df = scrape_jobs(
                    site_name=[platform],
                    search_term=query,
                    location=location,
                    results_wanted=min(limit, 15),  # Per platform limit
                    hours_old=72,  # Last 3 days
                    country_indeed="Brazil" if platform == "indeed" else None,
                )

                if df is None or df.empty:
                    logger.info(f"JobSpy: No results from {platform}")
                    continue

                for _, row in df.iterrows():
                    try:
                        job = self._row_to_scraped_job(row, platform)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.warning(f"JobSpy: Failed to parse row from {platform}: {e}")
                        continue

                logger.info(f"JobSpy: Got {len(df)} results from {platform}")

            except Exception as e:
                logger.warning(f"JobSpy: Platform {platform} failed: {e}")
                continue

        return jobs

    def _row_to_scraped_job(self, row, platform: str) -> Optional[ScrapedJob]:
        """Convert a pandas row to ScrapedJob model."""
        title = str(row.get("title", "")).strip()
        company = str(row.get("company_name", row.get("company", ""))).strip()

        if not title or not company or title == "nan" or company == "nan":
            return None

        # Build external ID
        job_url = str(row.get("job_url", row.get("link", "")))
        external_id = f"{platform}_{hash(job_url)}"

        # Location
        location = str(row.get("location", ""))
        if location == "nan":
            location = ""

        is_remote = bool(row.get("is_remote", False))
        if not is_remote:
            # Check if location contains "remote"
            is_remote = "remote" in location.lower() or "remoto" in location.lower()

        # Salary
        salary_min = None
        salary_max = None
        try:
            sal_min = row.get("min_amount", row.get("salary_min"))
            sal_max = row.get("max_amount", row.get("salary_max"))
            if sal_min and str(sal_min) != "nan":
                salary_min = int(float(sal_min))
            if sal_max and str(sal_max) != "nan":
                salary_max = int(float(sal_max))
        except (ValueError, TypeError):
            pass

        # Currency
        salary_currency = str(row.get("currency", "BRL"))
        if salary_currency == "nan":
            salary_currency = "BRL"

        # Description
        description = str(row.get("description", ""))
        if description == "nan":
            description = title  # Fallback

        # Posted date
        posted_at = None
        try:
            date_val = row.get("date_posted")
            if date_val and str(date_val) != "nan" and str(date_val) != "NaT":
                if isinstance(date_val, datetime):
                    posted_at = date_val
                else:
                    posted_at = datetime.fromisoformat(str(date_val))
        except Exception:
            pass

        # Job type
        job_type = str(row.get("job_type", ""))
        if job_type == "nan":
            job_type = ""

        return ScrapedJob(
            title=title,
            company=company,
            location=location or "Not specified",
            is_remote=is_remote,
            salary_min=salary_min,
            salary_max=salary_max,
            salary_currency=salary_currency,
            description=description[:5000],  # Truncate very long descriptions
            url=job_url if job_url != "nan" else "",
            external_id=external_id,
            source_platform=platform,
            posted_at=posted_at,
            employment_type=job_type,
            technologies=[],
        )

    async def get_job_details(self, job_url: str) -> Optional[ScrapedJob]:
        """Not implemented for JobSpy — search already returns full details."""
        return None

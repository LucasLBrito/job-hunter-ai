"""
Robust BaseScraper with stealth HTTP client for job scraping.
Features:
  - Rotating User-Agent pool (Chrome, Firefox, Edge on Windows/Mac/Linux)
  - Realistic browser headers (Accept, Sec-Ch-Ua, etc.)
  - Automatic retry with exponential backoff (3 attempts)
  - Optional proxy support via settings.SCRAPER_PROXY_URL
  - Configurable timeouts
"""
import httpx
import random
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stealth User-Agent Pool
# ---------------------------------------------------------------------------
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    # Chrome on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    # Firefox on Linux
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    # Safari on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15",
]


def _build_stealth_headers(referer: str = "") -> dict:
    """Build realistic browser headers to avoid bot detection."""
    ua = random.choice(USER_AGENTS)
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    # Add Sec-Ch-Ua for Chrome-like UAs
    if "Chrome" in ua:
        headers["Sec-Ch-Ua"] = '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"'
        headers["Sec-Ch-Ua-Mobile"] = "?0"
        headers["Sec-Ch-Ua-Platform"] = '"Windows"'
    if referer:
        headers["Referer"] = referer
    return headers


class BaseScraper(ABC):
    """
    Abstract base class for all job scrapers.
    Provides a robust HTTP client via `self.fetch()` with retries,
    stealth headers, and optional proxy support.
    """

    MAX_RETRIES = 3
    BASE_TIMEOUT = 20.0  # seconds

    async def fetch(
        self,
        url: str,
        *,
        params: dict = None,
        headers: dict = None,
        referer: str = "",
        timeout: float = None,
        json_response: bool = False,
    ) -> httpx.Response:
        """
        Fetch a URL with stealth headers, retries, and optional proxy.
        Returns the httpx.Response object.
        Raises the last exception if all retries fail.
        """
        stealth = _build_stealth_headers(referer)
        if headers:
            stealth.update(headers)

        proxy_url = None
        try:
            from app.core.config import settings
            proxy_url = settings.SCRAPER_PROXY_URL if settings.SCRAPER_PROXY_URL else None
        except Exception:
            pass

        last_error = None
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(
                    proxy=proxy_url,
                    timeout=timeout or self.BASE_TIMEOUT,
                    follow_redirects=True,
                ) as client:
                    response = await client.get(url, params=params, headers=stealth)
                    response.raise_for_status()
                    return response

            except (httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                last_error = e
                wait = 2 ** attempt + random.uniform(0, 1)
                logger.warning(
                    f"{type(self).__name__}: attempt {attempt}/{self.MAX_RETRIES} failed for {url}: {e}. "
                    f"Retrying in {wait:.1f}s..."
                )
                await asyncio.sleep(wait)

            except Exception as e:
                last_error = e
                logger.error(f"{type(self).__name__}: unexpected error on {url}: {e}")
                break

        raise last_error  # type: ignore

    async def fetch_json(self, url: str, *, params: dict = None, headers: dict = None, referer: str = "") -> dict:
        """Convenience: fetch and return parsed JSON."""
        resp = await self.fetch(url, params=params, headers=headers, referer=referer)
        return resp.json()

    @abstractmethod
    async def search_jobs(self, query: str, limit: int = 10) -> List[ScrapedJob]:
        """Search for jobs. Must be implemented by each scraper."""
        pass

    async def get_job_details(self, job_url: str) -> Optional[ScrapedJob]:
        """Optional: Fetch full details for a specific job URL."""
        return None

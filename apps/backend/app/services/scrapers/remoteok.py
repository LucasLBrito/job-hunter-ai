import httpx
import logging
import feedparser
from typing import List, Optional
from datetime import datetime
from app.services.scrapers.base import BaseScraper
from app.services.scrapers.models import ScrapedJob
from app.core.config import settings

logger = logging.getLogger(__name__)

class RemoteOKScraper(BaseScraper):
    """
    Scraper for RemoteOK using their RSS feed.
    """
    API_URL = "https://remoteok.com/api"
    
    async def search_jobs(self, query: str, limit: int = 10) -> List[ScrapedJob]:
        logger.info(f"Searching RemoteOK for: {query}")
        
        # RemoteOK uses tags in URL for filtering, e.g. remoteok.com/remote-python-jobs.json
        # But RSS is more reliable for recent jobs.
        # Let's try the RSS feed with query param? No, RemoteOK RSS is "recent jobs".
        # Better: Filter client side or use tags if possible.
        # For simplicity in V1: Fetch RSS and filter by title/description match.
        
        try:
            proxy_url = settings.SCRAPER_PROXY_URL if settings.SCRAPER_PROXY_URL else None
            async with httpx.AsyncClient(proxy=proxy_url) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
                }
                response = await client.get(self.API_URL, headers=headers, timeout=15.0)
                response.raise_for_status()
                
            data = response.json()
            jobs = []
            
            # First item in RemoteOK API is often legal/metadata
            job_items = data[1:] if isinstance(data, list) else []
            
            search_terms = query.lower().split()
            
            for entry in job_items:
                if len(jobs) >= limit:
                    break
                    
                title = entry.get("position", "")
                company = entry.get("company", "")
                description = entry.get("description", "")
                
                # Broad matching: any of the terms match title or company or tags
                match = not search_terms # True if empty query
                if not match:
                    tags = entry.get('tags')
                    tags_str = ' '.join(tags) if isinstance(tags, list) else str(tags or '')
                    text_to_search = f"{title} {company} {tags_str}".lower()
                    match = any(term in text_to_search for term in search_terms)
                
                # FALLBACK: If we still have very few jobs, we'll take some more broad ones to ensure the user sees results
                if not match and len(jobs) < min(limit, 10):
                    match = True 
                
                if not match:
                    continue
                
                # Date can be ISO or timestamp
                raw_date = entry.get("date")
                posted_at = datetime.utcnow()
                if raw_date:
                    try:
                        if "T" in str(raw_date):
                            posted_at = datetime.fromisoformat(str(raw_date).replace("Z", "+00:00"))
                        else:
                            posted_at = datetime.fromtimestamp(int(raw_date))
                    except:
                        pass
                
                job = ScrapedJob(
                    title=title,
                    company=company,
                    location=entry.get("location", "Remote"),
                    is_remote=True,
                    description=description,
                    url=entry.get("url", ""),
                    external_id=str(entry.get("id", hash(title + company))),
                    source_platform="remoteok",
                    posted_at=posted_at,
                    technologies=entry.get("tags", []),
                    salary_min=None,
                    salary_max=None
                )
                
                jobs.append(job)
                
            logger.info(f"Found {len(jobs)} jobs in RemoteOK API for query '{query}'")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping RemoteOK: {e}")
            return []

    async def get_job_details(self, job_url: str) -> Optional[ScrapedJob]:
        # RemoteOK RSS provides full description usually, so this might not be needed immediately
        # unless we want to parse the HTML page for more attributes.
        return None

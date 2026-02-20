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
    RSS_URL = "https://remoteok.com/rss"
    
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
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = await client.get(self.RSS_URL, headers=headers, timeout=10.0)
                logger.info(f"RemoteOK RSS Status: {response.status_code}")
                response.raise_for_status()
                
            feed = feedparser.parse(response.text)
            jobs = []
            
            for entry in feed.entries:
                if len(jobs) >= limit:
                    break
                    
                # Basic client-side filtering
                if query.lower() not in entry.title.lower() and query.lower() not in entry.description.lower():
                    continue
                
                # Title often is "Company calls for Role" or similar
                # RemoteOK RSS title format: "Role at Company"
                title_parts = entry.title.split(" at ")
                if len(title_parts) >= 2:
                    role = title_parts[0].strip()
                    company = title_parts[1].strip()
                else:
                    role = entry.title
                    company = "Unknown"

                # Salary extraction (basic heuristic)
                salary_min = None
                salary_max = None
                # RemoteOK description often contains salary range
                
                job = ScrapedJob(
                    title=role,
                    company=company,
                    location="Remote",
                    is_remote=True,
                    description=entry.description,
                    url=entry.link,
                    external_id=entry.id, # GUID
                    source_platform="remoteok",
                    posted_at=datetime.utcnow(), # RSS doesn't always frame it well, using now or entry.published
                    technologies=[tag.term for tag in entry.tags] if hasattr(entry, 'tags') else []
                )
                
                # Check for published date
                if hasattr(entry, 'published_parsed'):
                    try:
                        dt = datetime(*entry.published_parsed[:6])
                        job.posted_at = dt
                    except:
                        pass
                        
                jobs.append(job)
                
            logger.info(f"Found {len(jobs)} jobs in RemoteOK matching '{query}'")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping RemoteOK: {e}")
            return []

    async def get_job_details(self, job_url: str) -> Optional[ScrapedJob]:
        # RemoteOK RSS provides full description usually, so this might not be needed immediately
        # unless we want to parse the HTML page for more attributes.
        return None

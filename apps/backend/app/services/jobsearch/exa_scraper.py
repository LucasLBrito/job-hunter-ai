import os
import logging
from typing import List, Optional
from datetime import datetime

from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)

class ExaScraper(BaseScraper):
    """
    Search for jobs using Exa's semantic search API.
    """
    
    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get("EXA_API_KEY")
        if not self.api_key:
            logger.warning("EXA_API_KEY is not set. ExaScraper will not function properly.")

    async def search_jobs(self, query: str, limit: int = 10) -> List[ScrapedJob]:
        if not self.api_key:
            logger.error("Skipping Exa search because EXA_API_KEY is missing.")
            return []

        jobs = []
        try:
            url = "https://api.exa.ai/search"
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Semantic search query
            semantic_query = f"career pages or job boards listing remote {query} roles"
            
            payload = {
                "query": semantic_query,
                "useAutoprompt": True,
                "numResults": limit,
                "contents": {
                    "text": {"maxCharacters": 500}
                }
            }
            
            logger.info(f"ExaScraper: Executing semantic search for '{semantic_query}'")
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                
            results = data.get("results", [])
            
            for index, item in enumerate(results):
                title = item.get("title") or "Unknown Job Listing"
                link = item.get("url") or ""
                text = item.get("text") or ""
                author = item.get("author") or "Exa Semantic Search"
                ext_id = item.get("id") or f"exa_{index}_{hash(link)}"
                
                # Exa results can be generic links, so we'll parse them roughly
                job = ScrapedJob(
                     title=str(title)[:100],
                     company=str(author),
                     location="Remote",
                     is_remote=True,
                     description=str(text),
                     url=str(link),
                     external_id=str(ext_id),
                     source_platform="exa",
                     posted_at=datetime.utcnow()
                )
                jobs.append(job)
                
            logger.info(f"ExaScraper: Found {len(jobs)} semantic results")
            return jobs

        except Exception as e:
            logger.error(f"ExaScraper error: {e}")
            return []

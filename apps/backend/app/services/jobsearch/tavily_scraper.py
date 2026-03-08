import os
import json
import logging
from typing import List, Optional
from datetime import datetime

from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)

class TavilyScraper(BaseScraper):
    """
    Search for jobs using the Tavily API, optimized for AI agents and research.
    """
    
    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get("TAVILY_API_KEY")
        if not self.api_key:
            logger.warning("TAVILY_API_KEY is not set. TavilyScraper will not function properly.")

    async def search_jobs(self, query: str, limit: int = 10) -> List[ScrapedJob]:
        if not self.api_key:
            logger.error("Skipping Tavily search because TAVILY_API_KEY is missing.")
            return []

        jobs = []
        try:
            # Tavily Search API endpoint
            url = "https://api.tavily.com/search"
            
            # Formulate the query specifically for job search
            search_query = f"{query} remote jobs recent openings site:lever.co OR site:greenhouse.io OR site:workable.com OR site:remotive.com OR site:weworkremotely.com"
            
            payload = {
                "api_key": self.api_key,
                "query": search_query,
                "search_depth": "advanced",
                "max_results": limit,
                "include_images": False,
                "include_answer": False,
                "include_raw_content": False,
            }
            
            logger.info(f"TavilyScraper: Searching for '{search_query}'")
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    url, 
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                resp.raise_for_status()
                data = resp.json()
            
            results = data.get("results", [])
            
            for index, item in enumerate(results):
                title = item.get("title", "Unknown Title")
                url = item.get("url", "")
                content = item.get("content", "")
                
                # Basic parsing to infer job details from the search result snippet
                description = content
                
                # Fallbacks for parsing companies from URLs if possible
                company = "Tavily Extracted"
                if "lever.co" in url:
                    parts = url.split("lever.co/")
                    if len(parts) > 1:
                        company = parts[1].split("/")[0].capitalize()
                elif "greenhouse.io" in url:
                    parts = url.split("greenhouse.io/")
                    if len(parts) > 1:
                        company = parts[1].split("/")[0].capitalize()
                
                # Construct ScrapedJob
                job = ScrapedJob(
                    title=title[:100],
                    company=company,
                    location="Remote",
                    is_remote=True,
                    description=description,
                    url=url,
                    external_id=f"tavily_{index}_{hash(url)}",
                    source_platform="tavily",
                    posted_at=datetime.utcnow(),
                )
                jobs.append(job)
                
            logger.info(f"TavilyScraper: Found {len(jobs)} jobs for query '{query}'")
            return jobs

        except Exception as e:
            logger.error(f"TavilyScraper error: {e}")
            return []

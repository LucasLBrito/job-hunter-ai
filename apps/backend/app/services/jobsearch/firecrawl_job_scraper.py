import os
import logging
from typing import List, Optional
from datetime import datetime

from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)

class FirecrawlJobScraper(BaseScraper):
    """
    Perform deep web scraping using Firecrawl API to extract job listings from specific URLs.
    """
    
    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get("FIRECRAWL_API_KEY")
        if not self.api_key:
            logger.warning("FIRECRAWL_API_KEY is not set. FirecrawlJobScraper will not function properly.")

    async def search_jobs(self, query: str, limit: int = 10) -> List[ScrapedJob]:
        if not self.api_key:
            logger.error("Skipping Firecrawl search because FIRECRAWL_API_KEY is missing.")
            return []

        jobs = []
        try:
            # For Firecrawl, we usually crawl a specific URL that blocks us (e.g., a specific Vagas URL)
            # In this generic implementation, we will use it to scrape a known remote job board or an aggregated search page.
            # Example using a common board that we can't easily parse normally:
            target_url = "https://remoteok.com/?q=python"  # Just an example target for demonstration, you can change this
            
            api_url = "https://api.firecrawl.dev/v0/scrape"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "url": target_url,
                "pageOptions": {
                    "includeHtml": False,
                    "onlyMainContent": True
                }
            }
            
            logger.info(f"FirecrawlJobScraper: Scraping '{target_url}'")
            # Note: We do not use self.fetch() because we want to send a POST payload here.
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(api_url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                
            # Firecrawl returns markdown content by default
            markdown = data.get("data", {}).get("markdown", "")
            
            # If no content was retrieved
            if not markdown:
                return []
                
            # Fallback trivial extraction from markdown
            # This is a stub for extracting the titles from raw markdown, but realistically you'd use LLM extraction
            # or structured data output capabilities of Firecrawl.
            lines = markdown.split("\\n")
            title = ""
            company = "Firecrawl Scraped"
            
            for i, line in enumerate(lines[:min(len(lines), limit * 10)]): # rough boundary
                if "python" in line.lower() or "developer" in line.lower() or "engineer" in line.lower():
                    title = line.strip("#").strip()
                    job = ScrapedJob(
                         title=title[:100],
                         company=company,
                         location="Remote",
                         is_remote=True,
                         description=f"Extracted snippet: {line}",
                         url=target_url,
                         external_id=f"firecrawl_{i}_{hash(line)}",
                         source_platform="firecrawl",
                         posted_at=datetime.utcnow()
                    )
                    jobs.append(job)
                    if len(jobs) >= limit:
                        break
            
            logger.info(f"FirecrawlJobScraper: Extracted {len(jobs)} jobs from {target_url}")
            return jobs

        except Exception as e:
            logger.error(f"FirecrawlJobScraper error: {e}")
            return []

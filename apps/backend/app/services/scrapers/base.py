from abc import ABC, abstractmethod
from typing import List
from app.services.scrapers.models import ScrapedJob
import logging

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Abstract base class for all job scrapers.
    """
    
    @abstractmethod
    async def search_jobs(self, query: str, limit: int = 10) -> List[ScrapedJob]:
        """
        Search for jobs based on a query string.
        Should return a list of standardized ScrapedJob objects.
        """
        pass
    
    @abstractmethod
    async def get_job_details(self, job_url: str) -> Optional[ScrapedJob]:
        """
        Fetch full details for a specific job URL.
        Useful for "deep" scraping when the search listing is incomplete.
        """
        pass

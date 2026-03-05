import logging
import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime

from app.services.scrapers.base import BaseScraper
from app.services.scrapers.models import ScrapedJob

logger = logging.getLogger(__name__)

class VagasScraper(BaseScraper):
    PLATFORM_NAME = "vagas.com.br"
    BASE_URL = "https://www.vagas.com.br/vagas-de"

    async def search_jobs(self, query: str, limit: int = 20, location: str = "") -> List[ScrapedJob]:
        query_formatted = query.replace(" ", "-")
        url = f"{self.BASE_URL}-{query_formatted}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }

        jobs = []
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                if response.status_code != 200:
                    logger.error(f"VagasScraper: HTTP {response.status_code} at {url}")
                    return []
                
                soup = BeautifulSoup(response.text, "html.parser")
                job_cards = soup.select("a.link-detalhes-vaga")
                
                for a in job_cards[:limit]:
                    try:
                        title = a.get_text(strip=True)
                        job_url = "https://www.vagas.com.br" + a.get("href", "")
                        
                        parent = a.find_parent("li")
                        if not parent:
                            continue
                            
                        company_elem = parent.find(class_="empresa")
                        company = company_elem.get_text(strip=True) if company_elem else "Não revelado"
                        
                        loc_elem = parent.find(class_="vaga-local")
                        location = loc_elem.get_text(strip=True) if loc_elem else "Brasil"
                        is_remote = "remoto" in location.lower() or "home office" in location.lower()
                        
                        desc_elem = parent.find(class_="detalhes")
                        desc_preview = desc_elem.get_text(strip=True) if desc_elem else ""

                        external_id = f"{self.PLATFORM_NAME}_{hash(job_url)}"
                        
                        jobs.append(ScrapedJob(
                            title=title,
                            company=company,
                            location=location,
                            is_remote=is_remote,
                            salary_min=None,
                            salary_max=None,
                            salary_currency="BRL",
                            description=desc_preview,
                            url=job_url,
                            external_id=external_id,
                            source_platform=self.PLATFORM_NAME,
                            posted_at=datetime.utcnow(),
                            employment_type="",
                            technologies=[]
                        ))
                    except Exception as e:
                        logger.warning(f"VagasScraper: Erro ao fazer parse de um card: {e}")
                        
        except Exception as e:
            logger.error(f"VagasScraper: Falha geral: {e}")
            
        return jobs

    async def get_job_details(self, job_url: str) -> Optional[ScrapedJob]:
        return None

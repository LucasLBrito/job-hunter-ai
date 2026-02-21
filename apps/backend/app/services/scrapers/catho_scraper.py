import logging
import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime

from app.services.scrapers.base import BaseScraper
from app.services.scrapers.models import ScrapedJob

logger = logging.getLogger(__name__)

class CathoScraper(BaseScraper):
    """
    Scraper customizado para a plataforma Catho (catho.com.br).
    Busca vagas públicas utilizando parse de HTML.
    """

    PLATFORM_NAME = "catho"
    BASE_URL = "https://www.catho.com.br/vagas"

    async def search_jobs(self, query: str, limit: int = 20, location: str = "") -> List[ScrapedJob]:
        """
        Busca vagas na Catho. 
        Para simplificar, usaremos o httpx assíncrono para buscar o HTML da página de pesquisa 
        e o BeautifulSoup para buscar os dados básicos dos cards de vagas.
        """
        logger.info(f"CathoScraper: Buscando por '{query}' na Catho...")
        
        # Try the most standard query parameter URL
        url = f"{self.BASE_URL}/?q={query}"
        
        # Se location for provida (ex: são paulo), a Catho geralmente anexa com ?cidade_id=
        # Mas para não errar no Regex do id da cidade, faremos a busca ampla primeiro.
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Referer": "https://www.catho.com.br/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

        jobs = []
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code != 200:
                    logger.error(f"CathoScraper: Erro {response.status_code} ao acessar {url}")
                    return []
                
                html = response.text
                soup = BeautifulSoup(html, "html.parser")
                
                # Encontrar os blocos principais de vagas
                # Na layout padrão da catho (Pode mudar frequentemente)
                # Geralmente fica dentro de <li> com classes específicas para listagem de vagas
                job_lists = soup.find("ul", class_=lambda x: x and "gtm-job-list" in x) or soup.find("ul", {"id": "search-result"})
                
                if not job_lists:
                    # Alternative approach se o de cima falhar (Catho costuma usar <article> pros cards)
                    job_cards = soup.find_all("article")
                else:
                    job_cards = job_lists.find_all("li")

                logger.info(f"CathoScraper: Encontrou {len(job_cards)} possiveis cards de vagas")

                for card in job_cards[:limit]:
                    try:
                        job = self._parse_job_card(card)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.warning(f"CathoScraper: Erro ao fazer parse de um card: {e}")
                        continue

        except Exception as e:
            logger.error(f"CathoScraper: Falha geral durante a busca: {e}")
            
        logger.info(f"CathoScraper: Retornando {len(jobs)} vagas.")
        return jobs

    def _parse_job_card(self, card) -> Optional[ScrapedJob]:
        """Faz o parse de um bloco HTML individual de vaga da Catho."""
        
        # Título e Link
        title_elem = card.find("h2")
        if not title_elem:
            return None
            
        link_elem = title_elem.find("a")
        if not link_elem:
            return None
            
        title = title_elem.get_text(strip=True)
        job_url = link_elem.get("href", "")
        
        # ID externo
        external_id = f"{self.PLATFORM_NAME}_{hash(job_url)}"
        
        # Empresa
        company = "Não revelado (Catho)"
        company_elem = card.find("p", string=lambda s: s and "Empresa" in s)
        # Note: na Catho às vezes é sigiloso. Muitas vezes está escondido atrás de um modal ou num <p> especifico.
        if not company_elem:
            # Tentar achar algum text normal
            company_candidate = card.find("span", attrs={"data-gtm-element": "job-company-name"})
            if company_candidate:
                company = company_candidate.get_text(strip=True)

        # Salário
        salary_min = None
        salary_max = None
        salary_currency = "BRL"
        salary_elem = card.find(string=lambda s: s and "R$" in s)
        if salary_elem:
             # Basic regex extraction would be ideal here. 
             # Lets use a simple try hack for "A Combinar" or "R$ 5.000 a R$ 6.000"
             sal_text = str(salary_elem).replace(".", "").replace(",", ".").replace("R$", "")
             parts = [p.strip() for p in sal_text.split("a") if p.strip().replace(".", "", 1).isdigit()]
             try:
                 if parts:
                     salary_min = int(float(parts[0]))
                     salary_max = int(float(parts[-1])) if len(parts) > 1 else salary_min
             except:
                 pass
                 
        # Localização e Remoto
        location = "Brasil"
        is_remote = False
        loc_elem = card.find("a", href=lambda h: h and "/vagas/" in h and ("-sp" in h or "-rj" in h or "estado=" in h))
        # A Catho tem classes pra isso também
        if loc_elem:
            location = loc_elem.get_text(strip=True)
            
        if "Home Office" in card.get_text() or "Remoto" in card.get_text():
            is_remote = True

        # Descrição preview
        desc_preview = ""
        desc_elem = card.find("span", class_=lambda x: x and "job-description" in x)
        if not desc_elem:
             desc_elem = card.find("div", class_=lambda x: x and "job-description" in x)
             
        if desc_elem:
            desc_preview = desc_elem.get_text(strip=True)
        else:
            # Fallback
            desc_preview = card.get_text(separator=' ', strip=True)[:300] + "..."

        # Date posted
        posted_at = None
        date_elem = card.find("time")
        if date_elem:
             raw_date = date_elem.get_text(strip=True) # "Hoje", "Ontem", "2 de Fev" - Hard to parse perfectly without full logic.
             # We'll default to today for scraped jobs on Catho unless clearly parsed
             posted_at = datetime.utcnow()
        else:
             posted_at = datetime.utcnow()

        return ScrapedJob(
            title=title,
            company=company,
            location=location,
            is_remote=is_remote,
            salary_min=salary_min,
            salary_max=salary_max,
            salary_currency=salary_currency,
            description=desc_preview,
            url=job_url if job_url.startswith("http") else f"https://www.catho.com.br{job_url}",
            external_id=external_id,
            source_platform=self.PLATFORM_NAME,
            posted_at=posted_at,
            employment_type="",
            technologies=[],
        )

    async def get_job_details(self, job_url: str) -> Optional[ScrapedJob]:
        # Para MVP, a preview na search já serve bem 
        return None

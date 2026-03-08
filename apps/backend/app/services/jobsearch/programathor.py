"""ProgramaThor Scraper - HTML scraping from programathor.com.br."""
import logging
import re
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class ProgramaThorScraper(BaseScraper):
    PLATFORM_NAME = "programathor"
    BASE_URL = "https://programathor.com.br/jobs"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        search_term = query.split()[0] if query else "developer"
        url = f"{self.BASE_URL}?search={search_term}"
        logger.info(f"ProgramaThorScraper: Searching at {url}")
        jobs = []
        try:
            resp = await self.fetch(url, referer="https://programathor.com.br/")
            soup = BeautifulSoup(resp.text, "html.parser")

            # ProgramaThor uses links to /jobs/ID-slug with job data in the link text
            job_links = soup.select("a[href*='/jobs/']")
            seen_urls = set()
            for link in job_links:
                if len(jobs) >= limit:
                    break
                try:
                    href = link.get("href", "")
                    # Only process actual job links (not navigation)
                    if not re.search(r'/jobs/\d+', href):
                        continue
                    job_url = f"https://programathor.com.br{href}" if href.startswith("/") else href
                    if job_url in seen_urls:
                        continue
                    seen_urls.add(job_url)

                    # Extract text content from the link
                    full_text = link.get_text(separator="|", strip=True)
                    parts = [p.strip() for p in full_text.split("|") if p.strip()]

                    if not parts:
                        continue

                    # The link text contains: Title, Company, Location, Size, Salary, Level, Type, Technologies...
                    # Try to find the h3 title first
                    title_el = link.find_previous("h3")
                    if title_el:
                        title = title_el.get_text(strip=True)
                        # Remove location prefixes like "📍 PRESENCIAL..."
                        title = re.sub(r'^📍.*?LOCAL\s*', '', title).strip()
                    else:
                        title = parts[0] if parts else "N/A"

                    # Company is usually the second part
                    company = parts[1] if len(parts) > 1 else "Confidencial"
                    # Location
                    location = parts[2] if len(parts) > 2 else "Brasil"
                    is_remote = "remoto" in location.lower() or "remote" in location.lower()

                    # Salary extraction
                    salary_min = salary_max = None
                    salary_match = re.search(r'R\$\s*([\d.]+)', full_text)
                    if salary_match:
                        try:
                            salary_max = int(salary_match.group(1).replace(".", ""))
                        except (ValueError, IndexError):
                            pass

                    # Technologies from the link text
                    tech_keywords = ["Python", "Java", "JavaScript", "TypeScript", "React", "Angular",
                                     "Vue", "Node", "PHP", "Ruby", "Go", "C#", ".NET", "SQL",
                                     "PostgreSQL", "MySQL", "Docker", "AWS", "Laravel", "Spring"]
                    techs = [t for t in tech_keywords if t.lower() in full_text.lower()]

                    external_id = f"programathor_{href.split('/')[-1].split('-')[0] if '/' in href else hash(job_url)}"

                    jobs.append(ScrapedJob(
                        title=title, company=company, location=location, is_remote=is_remote,
                        salary_max=salary_max, description=full_text[:500],
                        url=job_url, external_id=external_id,
                        source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(),
                        technologies=techs,
                    ))
                except Exception as e:
                    logger.warning(f"ProgramaThorScraper: parse error: {e}")
        except Exception as e:
            logger.error(f"ProgramaThorScraper: failed: {e}")
        logger.info(f"ProgramaThorScraper: found {len(jobs)} results for '{query}'")
        return jobs

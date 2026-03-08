"""RemoteOK Scraper - Uses RemoteOK's public JSON API."""
import logging
import json
from typing import List
from datetime import datetime
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class RemoteOKScraper(BaseScraper):
    PLATFORM_NAME = "remoteok"
    API_URL = "https://remoteok.com/api"

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        logger.info(f"RemoteOKScraper: Searching for '{query}'")
        try:
            # RemoteOK requires specific headers to return JSON
            resp = await self.fetch(
                self.API_URL,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                referer="https://remoteok.com/",
                timeout=30.0,
            )

            # Parse JSON - handle encoding issues
            try:
                data = resp.json()
            except Exception:
                text = resp.content.decode("utf-8", errors="replace")
                # RemoteOK sometimes wraps in HTML, try to extract JSON
                if text.strip().startswith("["):
                    data = json.loads(text)
                elif '{"' in text:
                    json_start = text.find("[")
                    json_end = text.rfind("]") + 1
                    if json_start >= 0 and json_end > json_start:
                        data = json.loads(text[json_start:json_end])
                    else:
                        logger.warning("RemoteOKScraper: Could not extract JSON from response")
                        return await self._fallback_html(query, limit)
                else:
                    logger.warning("RemoteOKScraper: Response is not JSON, falling back to HTML")
                    return await self._fallback_html(query, limit)

            # First item is metadata, skip it
            job_items = data[1:] if isinstance(data, list) and len(data) > 1 else []

            if not job_items:
                logger.info("RemoteOKScraper: API returned no jobs, trying HTML fallback")
                return await self._fallback_html(query, limit)

            search_terms = query.lower().split()
            jobs = []
            for entry in job_items:
                if len(jobs) >= limit:
                    break
                if not isinstance(entry, dict):
                    continue
                title = entry.get("position", "")
                company = entry.get("company", "")
                description = entry.get("description", "")
                tags = entry.get("tags")
                tags_str = " ".join(tags) if isinstance(tags, list) else str(tags or "")
                text_to_search = f"{title} {company} {tags_str} {description}".lower()

                match = not search_terms or any(t in text_to_search for t in search_terms)
                if not match:
                    continue

                raw_date = entry.get("date")
                posted_at = datetime.utcnow()
                if raw_date:
                    try:
                        if "T" in str(raw_date):
                            posted_at = datetime.fromisoformat(str(raw_date).replace("Z", "+00:00"))
                        else:
                            posted_at = datetime.fromtimestamp(int(raw_date))
                    except Exception:
                        pass

                job_url = entry.get("url", "")
                if not job_url and entry.get("slug"):
                    job_url = f"https://remoteok.com/remote-jobs/{entry['slug']}"

                jobs.append(ScrapedJob(
                    title=title, company=company,
                    location=entry.get("location", "Remote"), is_remote=True,
                    description=description[:3000],
                    url=job_url,
                    external_id=f"remoteok_{entry.get('id', hash(title + company))}",
                    source_platform=self.PLATFORM_NAME, posted_at=posted_at,
                    technologies=entry.get("tags", []),
                ))

            # If no matches for query, take latest as fallback
            if not jobs and job_items:
                logger.info(f"RemoteOKScraper: No match for '{query}', using latest {limit} jobs")
                for entry in job_items[:limit]:
                    if not isinstance(entry, dict):
                        continue
                    title = entry.get("position", "")
                    if not title:
                        continue
                    company = entry.get("company", "")
                    job_url = entry.get("url", "")
                    if not job_url and entry.get("slug"):
                        job_url = f"https://remoteok.com/remote-jobs/{entry['slug']}"
                    jobs.append(ScrapedJob(
                        title=title, company=company,
                        location=entry.get("location", "Remote"), is_remote=True,
                        description=entry.get("description", "")[:3000],
                        url=job_url,
                        external_id=f"remoteok_{entry.get('id', hash(title + company))}",
                        source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(),
                        technologies=entry.get("tags", []),
                    ))

            logger.info(f"RemoteOKScraper: found {len(jobs)} results for '{query}'")
            return jobs
        except Exception as e:
            logger.error(f"RemoteOKScraper: API failed: {e}, trying HTML fallback")
            return await self._fallback_html(query, limit)

    async def _fallback_html(self, query: str, limit: int) -> List[ScrapedJob]:
        """Fallback: scrape RemoteOK HTML page."""
        from bs4 import BeautifulSoup
        jobs = []
        try:
            resp = await self.fetch(
                f"https://remoteok.com/remote-dev-jobs",
                referer="https://remoteok.com/",
                timeout=30.0,
            )
            soup = BeautifulSoup(resp.text, "html.parser")
            # RemoteOK uses <tr> with class="job" for job rows
            rows = soup.select("tr.job, tr[data-slug]")
            search_lower = query.lower()
            for row in rows:
                if len(jobs) >= limit:
                    break
                try:
                    title_el = row.select_one("h2, [itemprop='title'], td.company h2")
                    company_el = row.select_one("h3, [itemprop='name'], td.company h3")
                    title = title_el.get_text(strip=True) if title_el else ""
                    company = company_el.get_text(strip=True) if company_el else ""
                    if not title:
                        continue
                    # Filter by query
                    if search_lower and search_lower not in (title + " " + company).lower():
                        continue
                    slug = row.get("data-slug", "")
                    job_url = f"https://remoteok.com/remote-jobs/{slug}" if slug else ""
                    tag_els = row.select("td.tags a, span.tag")
                    techs = [t.get_text(strip=True) for t in tag_els]
                    external_id = f"remoteok_{slug or hash(title + company)}"
                    jobs.append(ScrapedJob(
                        title=title, company=company, location="Remote", is_remote=True,
                        description="", url=job_url, external_id=external_id,
                        source_platform=self.PLATFORM_NAME, posted_at=datetime.utcnow(),
                        technologies=techs,
                    ))
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"RemoteOKScraper HTML fallback failed: {e}")
        logger.info(f"RemoteOKScraper (HTML fallback): found {len(jobs)} jobs")
        return jobs

"""RemoteOK Scraper - Uses RemoteOK's public JSON API with broader matching."""
import logging
from typing import List
from datetime import datetime
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class RemoteOKScraper(BaseScraper):
    PLATFORM_NAME = "remoteok"
    API_URL = "https://remoteok.com/api"

    async def search_jobs(self, query: str, limit: int = 10) -> List[ScrapedJob]:
        logger.info(f"RemoteOKScraper: Searching for '{query}'")
        try:
            resp = await self.fetch(self.API_URL, headers={"Accept": "application/json"})
            # RemoteOK sometimes returns non-UTF-8 data; force encoding
            try:
                data = resp.json()
            except Exception:
                text = resp.content.decode("utf-8", errors="replace")
                import json
                data = json.loads(text)
            job_items = data[1:] if isinstance(data, list) else []

            search_terms = query.lower().split()
            jobs = []
            for entry in job_items:
                if len(jobs) >= limit:
                    break
                title = entry.get("position", "")
                company = entry.get("company", "")
                description = entry.get("description", "")
                tags = entry.get("tags")
                tags_str = " ".join(tags) if isinstance(tags, list) else str(tags or "")
                text_to_search = f"{title} {company} {tags_str} {description}".lower()

                # Broader matching: match ANY search term in the full text
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

                jobs.append(ScrapedJob(
                    title=title, company=company,
                    location=entry.get("location", "Remote"), is_remote=True,
                    description=description[:3000],
                    url=entry.get("url", ""),
                    external_id=str(entry.get("id", hash(title + company))),
                    source_platform=self.PLATFORM_NAME, posted_at=posted_at,
                    technologies=entry.get("tags", []),
                ))

            # If still empty after filtering, take the latest N jobs as fallback
            if not jobs and job_items:
                logger.info(f"RemoteOKScraper: No match for '{query}', using latest {limit} jobs as fallback")
                for entry in job_items[:limit]:
                    title = entry.get("position", "")
                    company = entry.get("company", "")
                    if not title:
                        continue
                    raw_date = entry.get("date")
                    posted_at = datetime.utcnow()
                    if raw_date:
                        try:
                            if "T" in str(raw_date):
                                posted_at = datetime.fromisoformat(str(raw_date).replace("Z", "+00:00"))
                        except Exception:
                            pass
                    jobs.append(ScrapedJob(
                        title=title, company=company,
                        location=entry.get("location", "Remote"), is_remote=True,
                        description=entry.get("description", "")[:3000],
                        url=entry.get("url", ""),
                        external_id=str(entry.get("id", hash(title + company))),
                        source_platform=self.PLATFORM_NAME, posted_at=posted_at,
                        technologies=entry.get("tags", []),
                    ))

            logger.info(f"RemoteOKScraper: found {len(jobs)} results for '{query}'")
            return jobs
        except Exception as e:
            logger.error(f"RemoteOKScraper: failed: {e}")
            return []

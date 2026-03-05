"""We Work Remotely Scraper - Uses RSS feed for reliability."""
import logging
import feedparser
from typing import List
from datetime import datetime
from app.services.jobsearch.base import BaseScraper
from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)


class WeWorkRemotelyScraper(BaseScraper):
    PLATFORM_NAME = "weworkremotely"
    # RSS feeds are more reliable than HTML scraping for WWR (avoids 403)
    RSS_CATEGORIES = [
        "https://weworkremotely.com/categories/remote-programming-jobs.rss",
        "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
        "https://weworkremotely.com/categories/remote-design-jobs.rss",
    ]

    async def search_jobs(self, query: str, limit: int = 20) -> List[ScrapedJob]:
        logger.info(f"WeWorkRemotelyScraper: Searching for '{query}' via RSS")
        jobs = []
        search_terms = query.lower().split()

        for rss_url in self.RSS_CATEGORIES:
            if len(jobs) >= limit:
                break
            try:
                resp = await self.fetch(rss_url, headers={"Accept": "application/rss+xml, application/xml, text/xml"})
                feed = feedparser.parse(resp.text)

                for entry in feed.entries:
                    if len(jobs) >= limit:
                        break
                    title = entry.get("title", "")
                    summary = entry.get("summary", entry.get("description", ""))
                    company = ""
                    # WWR format: "Company: Title"
                    if ":" in title:
                        parts = title.split(":", 1)
                        company = parts[0].strip()
                        title = parts[1].strip()

                    text = f"{title} {summary} {company}".lower()
                    if search_terms and not any(t in text for t in search_terms):
                        continue

                    link = entry.get("link", "")
                    external_id = f"weworkremotely_{hash(link)}"

                    posted_at = datetime.utcnow()
                    if entry.get("published_parsed"):
                        try:
                            import time
                            posted_at = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                        except Exception:
                            pass

                    jobs.append(ScrapedJob(
                        title=title, company=company or "WWR Listing",
                        location="Remote (Worldwide)", is_remote=True,
                        description=summary[:3000] if summary else "",
                        url=link, external_id=external_id,
                        source_platform=self.PLATFORM_NAME,
                        posted_at=posted_at, technologies=[],
                    ))

            except Exception as e:
                logger.warning(f"WeWorkRemotelyScraper: RSS {rss_url} failed: {e}")

        logger.info(f"WeWorkRemotelyScraper: found {len(jobs)} results for '{query}'")
        return jobs

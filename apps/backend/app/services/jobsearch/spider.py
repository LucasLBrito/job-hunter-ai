"""
Job Spider - High-Volume Data Ingestion Pipeline
=================================================
Orchestrates ALL job scrapers concurrently and ingests raw results into
the MongoDB Data Lake (collection: raw_jobs) with status "pending_processing".
The ETL worker (etl/worker.py) then transforms and loads data into PostgreSQL.

Architecture (Data Engineering best practices):
  [Spider] -> [MongoDB raw_jobs] -> [ETL Worker] -> [PostgreSQL jobs]

Usage:
  python -m app.services.jobsearch.spider --query "python developer" --limit 50
"""

import asyncio
import os
import sys
import json
import hashlib
import logging
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError, BulkWriteError

from app.services.jobsearch.models import ScrapedJob

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "job_lake")
DEFAULT_QUERIES = [
    "python developer",
    "data engineer",
    "backend developer",
    "fullstack developer",
    "devops engineer",
    "machine learning",
    "react developer",
    "node.js developer",
]
DEFAULT_LIMIT_PER_SCRAPER = 50


# ---------------------------------------------------------------------------
# Scraper Registry - ALL scrapers in the jobsearch module
# ---------------------------------------------------------------------------
def _build_scraper_registry() -> list:
    """
    Lazy-loads and instantiates all available scrapers.
    If a scraper fails to import (missing dependency), it is skipped gracefully.
    """
    scrapers = []
    registry = [
        ("app.services.jobsearch.cathoscraper", "CathoScraper"),
        ("app.services.jobsearch.vagas", "VagasScraper"),
        ("app.services.jobsearch.jobspy_scraper", "JobSpyScraper"),
        # AI API Scrapers
        ("app.services.jobsearch.tavily_scraper", "TavilyScraper"),
        ("app.services.jobsearch.firecrawl_job_scraper", "FirecrawlJobScraper"),
        ("app.services.jobsearch.exa_scraper", "ExaScraper"),
        ("app.services.jobsearch.gupy", "GupyScraper"),
        ("app.services.jobsearch.remoteok", "RemoteOKScraper"),
        ("app.services.jobsearch.adzuna", "AdzunaScraper"),
        ("app.services.jobsearch.remotar", "RemotarScraper"),
        ("app.services.jobsearch.geekhunter", "GeekHunterScraper"),
        ("app.services.jobsearch.coodesh", "CoodeshScraper"),
        ("app.services.jobsearch.freela", "FreelaScraper"),
        ("app.services.jobsearch.weworkremotely", "WeWorkRemotelyScraper"),
        ("app.services.jobsearch.workana", "WorkanaScraper"),
        ("app.services.jobsearch.apinfo", "APInfoScraper"),
        ("app.services.jobsearch.programathor", "ProgramaThorScraper"),
    ]
    for module_path, class_name in registry:
        try:
            import importlib
            mod = importlib.import_module(module_path)
            cls = getattr(mod, class_name)
            instance = cls()
            # Skip scrapers that require configuration but aren't configured
            if hasattr(instance, "is_configured") and not instance.is_configured:
                logger.info(f"⏭️  {class_name}: not configured, skipping.")
                continue
            scrapers.append(instance)
            logger.info(f"✅ {class_name}: loaded successfully.")
        except Exception as e:
            logger.warning(f"⚠️  {class_name}: failed to load ({e}), skipping.")
    return scrapers


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _generate_doc_id(job: ScrapedJob) -> str:
    """Generate a deterministic unique _id for MongoDB to prevent duplicates."""
    raw = f"{job.source_platform}:{job.external_id}:{job.url}"
    return hashlib.md5(raw.encode()).hexdigest()


def _scraped_job_to_raw_doc(job: ScrapedJob) -> Dict[str, Any]:
    """Convert a ScrapedJob pydantic model to a raw MongoDB document."""
    doc = job.model_dump()
    doc["_id"] = _generate_doc_id(job)
    doc["status"] = "pending_processing"
    doc["source"] = job.source_platform
    doc["ingested_at"] = datetime.now(timezone.utc)
    # Convert datetime fields to strings for JSON safety
    if doc.get("posted_at"):
        doc["posted_at"] = doc["posted_at"].isoformat() if isinstance(doc["posted_at"], datetime) else str(doc["posted_at"])
    return doc


# ---------------------------------------------------------------------------
# Spider Core
# ---------------------------------------------------------------------------
class JobSpider:
    """
    High-volume job spider that orchestrates all scrapers concurrently
    and ingests raw data into MongoDB Data Lake.
    """

    def __init__(self, mongo_uri: str = MONGO_URI, db_name: str = MONGO_DB_NAME):
        self.mongo_client = AsyncIOMotorClient(mongo_uri)
        self.db = self.mongo_client[db_name]
        self.raw_jobs_collection = self.db["raw_jobs"]
        self.scrapers = _build_scraper_registry()
        self.stats = {
            "total_scraped": 0,
            "total_inserted": 0,
            "total_duplicates": 0,
            "total_errors": 0,
            "scraper_results": {},
        }

    async def _run_single_scraper(self, scraper, query: str, limit: int) -> List[ScrapedJob]:
        """Run a single scraper with error isolation."""
        scraper_name = type(scraper).__name__
        try:
            logger.info(f"🔍 {scraper_name}: starting search for '{query}' (limit={limit})")
            results = await asyncio.wait_for(
                scraper.search_jobs(query, limit=limit),
                timeout=120.0,  # 2 minutes max per scraper
            )
            logger.info(f"✅ {scraper_name}: found {len(results)} jobs for '{query}'")
            return results
        except asyncio.TimeoutError:
            logger.error(f"⏰ {scraper_name}: TIMEOUT after 120s for '{query}'")
            self.stats["total_errors"] += 1
            return []
        except Exception as e:
            logger.error(f"❌ {scraper_name}: FAILED for '{query}': {e}")
            self.stats["total_errors"] += 1
            return []

    async def _ingest_to_mongo(self, jobs: List[ScrapedJob]) -> int:
        """
        Bulk insert scraped jobs into MongoDB with duplicate handling.
        Returns the number of newly inserted documents.
        """
        if not jobs:
            return 0

        docs = [_scraped_job_to_raw_doc(job) for job in jobs]
        inserted_count = 0

        try:
            # Use ordered=False so that duplicates don't stop the batch
            result = await self.raw_jobs_collection.insert_many(docs, ordered=False)
            inserted_count = len(result.inserted_ids)
        except BulkWriteError as bwe:
            # Some succeeded, some were duplicates
            inserted_count = bwe.details.get("nInserted", 0)
            n_duplicates = len(bwe.details.get("writeErrors", []))
            self.stats["total_duplicates"] += n_duplicates
            logger.info(f"📋 Bulk insert: {inserted_count} new, {n_duplicates} duplicates skipped")
        except Exception as e:
            logger.error(f"❌ MongoDB insert error: {e}")
            # Fallback: insert one by one
            for doc in docs:
                try:
                    await self.raw_jobs_collection.insert_one(doc)
                    inserted_count += 1
                except DuplicateKeyError:
                    self.stats["total_duplicates"] += 1
                except Exception as inner_e:
                    logger.error(f"❌ Single insert error: {inner_e}")

        return inserted_count

    async def crawl(
        self,
        queries: Optional[List[str]] = None,
        limit_per_scraper: int = DEFAULT_LIMIT_PER_SCRAPER,
        concurrency: int = 5,
    ) -> Dict[str, Any]:
        """
        Execute the full spider pipeline:
        1. For each query, run ALL scrapers concurrently (with semaphore).
        2. Ingest results into MongoDB Data Lake.
        3. Return aggregated statistics.
        """
        if queries is None:
            queries = DEFAULT_QUERIES

        logger.info("=" * 70)
        logger.info(f"🕷️  JOB SPIDER STARTING")
        logger.info(f"   Queries: {queries}")
        logger.info(f"   Scrapers loaded: {len(self.scrapers)}")
        logger.info(f"   Limit per scraper: {limit_per_scraper}")
        logger.info(f"   Concurrency: {concurrency}")
        logger.info("=" * 70)

        start_time = datetime.now(timezone.utc)
        semaphore = asyncio.Semaphore(concurrency)

        async def _scrape_with_semaphore(scraper, query):
            async with semaphore:
                return await self._run_single_scraper(scraper, query, limit_per_scraper)

        for query in queries:
            logger.info(f"\n{'─' * 50}")
            logger.info(f"📌 Processing query: '{query}'")
            logger.info(f"{'─' * 50}")

            # Run all scrapers concurrently for this query
            tasks = [
                _scrape_with_semaphore(scraper, query)
                for scraper in self.scrapers
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Aggregate and ingest results
            all_jobs_for_query: List[ScrapedJob] = []
            for i, result in enumerate(results):
                scraper_name = type(self.scrapers[i]).__name__
                if isinstance(result, Exception):
                    logger.error(f"❌ {scraper_name}: unhandled exception: {result}")
                    self.stats["total_errors"] += 1
                    continue
                if isinstance(result, list):
                    all_jobs_for_query.extend(result)
                    # Track per-scraper stats
                    key = scraper_name
                    self.stats["scraper_results"][key] = (
                        self.stats["scraper_results"].get(key, 0) + len(result)
                    )

            self.stats["total_scraped"] += len(all_jobs_for_query)

            # Bulk ingest into MongoDB
            if all_jobs_for_query:
                inserted = await self._ingest_to_mongo(all_jobs_for_query)
                self.stats["total_inserted"] += inserted
                logger.info(
                    f"💾 Query '{query}': {len(all_jobs_for_query)} scraped, "
                    f"{inserted} newly inserted into MongoDB"
                )

        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        # Final summary
        logger.info("\n" + "=" * 70)
        logger.info("🏁 SPIDER COMPLETED")
        logger.info(f"   Duration: {duration:.1f}s")
        logger.info(f"   Total Scraped: {self.stats['total_scraped']}")
        logger.info(f"   Total Inserted (new): {self.stats['total_inserted']}")
        logger.info(f"   Total Duplicates: {self.stats['total_duplicates']}")
        logger.info(f"   Total Errors: {self.stats['total_errors']}")
        logger.info(f"   Per-Scraper Breakdown:")
        for name, count in sorted(self.stats["scraper_results"].items(), key=lambda x: -x[1]):
            logger.info(f"     {name}: {count} jobs")
        logger.info("=" * 70)

        self.stats["duration_seconds"] = duration
        return self.stats

    async def close(self):
        """Close MongoDB connection."""
        self.mongo_client.close()


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
async def main():
    parser = argparse.ArgumentParser(description="Job Spider - High Volume Data Ingestion Pipeline")
    parser.add_argument(
        "--query", "-q",
        type=str,
        nargs="*",
        default=None,
        help="Search queries (space-separated). Defaults to a built-in list of tech queries.",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=DEFAULT_LIMIT_PER_SCRAPER,
        help=f"Max jobs per scraper per query (default: {DEFAULT_LIMIT_PER_SCRAPER})",
    )
    parser.add_argument(
        "--concurrency", "-c",
        type=int,
        default=5,
        help="Max concurrent scrapers (default: 5)",
    )
    args = parser.parse_args()

    spider = JobSpider()
    try:
        stats = await spider.crawl(
            queries=args.query,
            limit_per_scraper=args.limit,
            concurrency=args.concurrency,
        )
        print(json.dumps(stats, indent=2, default=str))
    finally:
        await spider.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    asyncio.run(main())

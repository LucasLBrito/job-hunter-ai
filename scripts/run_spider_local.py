"""
Local Spider Runner - Runs for N hours, saving jobs directly to the local database.
Bypasses MongoDB (not available locally) and saves directly to SQLite/PostgreSQL.

Usage:
    python scripts/run_spider_local.py --hours 4
"""
import asyncio
import sys
import os
import logging
import argparse
import hashlib
from datetime import datetime, timezone, timedelta

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/backend")))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("spider-local")

# Default search queries - covering a broad range of tech roles
QUERIES = [
    "python developer",
    "data engineer",
    "backend developer",
    "fullstack developer",
    "devops engineer",
    "machine learning",
    "react developer",
    "node.js developer",
    "data scientist",
    "software engineer",
    "cloud engineer",
    "java developer",
    "golang developer",
    "SRE",
    "tech lead",
    "engenheiro de dados",
    "desenvolvedor python",
    "desenvolvedor fullstack",
    "analista de dados",
    "engenheiro de software",
]

LIMIT_PER_SCRAPER = 50
CONCURRENCY = 5
PAUSE_BETWEEN_CYCLES_SECONDS = 300  # 5 minutes between cycles


def _build_scrapers():
    """Load all available scrapers."""
    scrapers = []
    registry = [
        ("app.services.jobsearch.cathoscraper", "CathoScraper"),
        ("app.services.jobsearch.vagas", "VagasScraper"),
        ("app.services.jobsearch.jobspy_scraper", "JobSpyScraper"),
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
    import importlib
    for module_path, class_name in registry:
        try:
            mod = importlib.import_module(module_path)
            cls = getattr(mod, class_name)
            instance = cls()
            if hasattr(instance, "is_configured") and not instance.is_configured:
                logger.info(f"⏭️  {class_name}: not configured, skipping.")
                continue
            scrapers.append(instance)
            logger.info(f"✅ {class_name}: loaded.")
        except Exception as e:
            logger.warning(f"⚠️  {class_name}: failed ({e}), skipping.")
    return scrapers


async def run_single_scraper(scraper, query, limit):
    """Run a single scraper with timeout."""
    name = type(scraper).__name__
    try:
        results = await asyncio.wait_for(
            scraper.search_jobs(query, limit=limit),
            timeout=120.0,
        )
        return results
    except asyncio.TimeoutError:
        logger.error(f"⏰ {name}: TIMEOUT for '{query}'")
        return []
    except Exception as e:
        logger.error(f"❌ {name}: FAILED for '{query}': {e}")
        return []


async def save_jobs_to_db(db_session, scraped_jobs):
    """Save scraped jobs directly to the local database with robust deduplication."""
    from app.models.job import Job
    from sqlalchemy import select
    from sqlalchemy.exc import IntegrityError

    inserted = 0
    duplicates = 0
    
    # Pre-filter duplicates within the same batch using a set
    seen_ids = set()
    unique_jobs = []
    for sj in scraped_jobs:
        key = f"{sj.external_id}|{sj.url}"
        if key not in seen_ids:
            seen_ids.add(key)
            unique_jobs.append(sj)
        else:
            duplicates += 1

    for sj in unique_jobs:
        try:
            # Check for existing by external_id
            stmt = select(Job.id).where(Job.external_id == sj.external_id)
            result = await db_session.execute(stmt)
            if result.scalar():
                duplicates += 1
                continue

            # Also check by URL
            stmt_url = select(Job.id).where(Job.source_url == sj.url)
            result_url = await db_session.execute(stmt_url)
            if result_url.scalar():
                duplicates += 1
                continue

            new_job = Job(
                external_id=sj.external_id,
                title=sj.title,
                company=sj.company,
                description=sj.description[:5000] if sj.description else "",
                location=sj.location,
                is_remote=sj.is_remote,
                salary_min=sj.salary_min,
                salary_max=sj.salary_max,
                salary_currency=sj.salary_currency,
                source_platform=sj.source_platform,
                source_url=sj.url,
                posted_date=sj.posted_at or datetime.now(timezone.utc),
            )
            
            # Use savepoint so IntegrityError only rolls back this one insert
            try:
                async with db_session.begin_nested():
                    db_session.add(new_job)
                inserted += 1
            except IntegrityError:
                duplicates += 1
                continue

        except Exception as e:
            logger.warning(f"⚠️  Error saving job '{sj.title}': {e}")

    # Final commit for all successful inserts
    try:
        await db_session.commit()
    except Exception as e:
        logger.error(f"❌ Final commit error: {e}")
        await db_session.rollback()

    return inserted, duplicates


async def run_spider_cycle(scrapers, db_session, queries, cycle_num):
    """Run one complete cycle of all scrapers across all queries."""
    semaphore = asyncio.Semaphore(CONCURRENCY)
    total_scraped = 0
    total_inserted = 0
    total_duplicates = 0

    logger.info(f"\n{'═' * 70}")
    logger.info(f"🕷️  CYCLE {cycle_num} STARTING - {len(queries)} queries × {len(scrapers)} scrapers")
    logger.info(f"{'═' * 70}")

    for query in queries:
        logger.info(f"\n📌 Query: '{query}'")

        async def scrape_with_sem(s, q):
            async with semaphore:
                return await run_single_scraper(s, q, LIMIT_PER_SCRAPER)

        tasks = [scrape_with_sem(s, query) for s in scrapers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_jobs = []
        for i, result in enumerate(results):
            if isinstance(result, list):
                all_jobs.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"❌ {type(scrapers[i]).__name__}: {result}")

        total_scraped += len(all_jobs)

        if all_jobs:
            inserted, dups = await save_jobs_to_db(db_session, all_jobs)
            total_inserted += inserted
            total_duplicates += dups
            logger.info(f"   ✅ '{query}': {len(all_jobs)} scraped, {inserted} new, {dups} duplicates")

    return total_scraped, total_inserted, total_duplicates


async def count_total_jobs(db_session):
    """Count total jobs in the database."""
    from sqlalchemy import func, select
    from app.models.job import Job
    stmt = select(func.count(Job.id))
    result = await db_session.execute(stmt)
    return result.scalar() or 0


async def main():
    parser = argparse.ArgumentParser(description="Local Spider Runner")
    parser.add_argument("--hours", type=float, default=4, help="Hours to run (default: 4)")
    args = parser.parse_args()

    run_duration = timedelta(hours=args.hours)
    end_time = datetime.now(timezone.utc) + run_duration

    logger.info("=" * 70)
    logger.info(f"🚀 LOCAL SPIDER STARTING")
    logger.info(f"   Duration: {args.hours} hours")
    logger.info(f"   End time: {end_time.astimezone().strftime('%H:%M:%S')}")
    logger.info(f"   Queries: {len(QUERIES)}")
    logger.info(f"   Pause between cycles: {PAUSE_BETWEEN_CYCLES_SECONDS}s")
    logger.info("=" * 70)

    # Initialize database
    from app.database import AsyncSessionLocal, init_db, engine
    
    # Ensure data directory exists for SQLite
    os.makedirs("data", exist_ok=True)
    
    await init_db()

    # Load scrapers
    scrapers = _build_scrapers()
    if not scrapers:
        logger.error("❌ No scrapers loaded! Exiting.")
        return

    logger.info(f"✅ Loaded {len(scrapers)} scrapers")

    # Get initial count
    async with AsyncSessionLocal() as session:
        initial_count = await count_total_jobs(session)
    logger.info(f"📊 Initial jobs in database: {initial_count}")

    grand_total_scraped = 0
    grand_total_inserted = 0
    grand_total_duplicates = 0
    cycle = 0

    start_time = datetime.now(timezone.utc)

    while datetime.now(timezone.utc) < end_time:
        cycle += 1
        remaining = end_time - datetime.now(timezone.utc)
        logger.info(f"\n⏳ Time remaining: {str(remaining).split('.')[0]}")

        async with AsyncSessionLocal() as session:
            scraped, inserted, dups = await run_spider_cycle(scrapers, session, QUERIES, cycle)
            grand_total_scraped += scraped
            grand_total_inserted += inserted
            grand_total_duplicates += dups

            current_total = await count_total_jobs(session)

        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
        rate = grand_total_inserted / (elapsed / 3600) if elapsed > 0 else 0

        logger.info(f"\n{'━' * 70}")
        logger.info(f"📊 CYCLE {cycle} SUMMARY:")
        logger.info(f"   This cycle: {scraped} scraped, {inserted} new, {dups} duplicates")
        logger.info(f"   Grand total: {grand_total_scraped} scraped, {grand_total_inserted} inserted")
        logger.info(f"   Database total: {current_total} jobs")
        logger.info(f"   Insertion rate: {rate:.0f} jobs/hour")
        logger.info(f"   Projected 4h total: ~{int(rate * 4)} jobs")
        logger.info(f"{'━' * 70}")

        # Check if we should continue
        if datetime.now(timezone.utc) + timedelta(seconds=PAUSE_BETWEEN_CYCLES_SECONDS) >= end_time:
            logger.info("⏰ Not enough time for another cycle. Finishing.")
            break

        logger.info(f"💤 Sleeping {PAUSE_BETWEEN_CYCLES_SECONDS}s before next cycle...")
        await asyncio.sleep(PAUSE_BETWEEN_CYCLES_SECONDS)

    # Final report
    async with AsyncSessionLocal() as session:
        final_count = await count_total_jobs(session)

    total_elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()

    logger.info("\n" + "=" * 70)
    logger.info("🏁 SPIDER COMPLETED - FINAL REPORT")
    logger.info(f"   Duration: {total_elapsed / 3600:.1f} hours")
    logger.info(f"   Cycles completed: {cycle}")
    logger.info(f"   Total scraped: {grand_total_scraped}")
    logger.info(f"   Total new inserted: {grand_total_inserted}")
    logger.info(f"   Total duplicates: {grand_total_duplicates}")
    logger.info(f"   Jobs before: {initial_count}")
    logger.info(f"   Jobs after: {final_count}")
    logger.info(f"   Net new jobs: {final_count - initial_count}")
    logger.info("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

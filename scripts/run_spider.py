#!/usr/bin/env python3
"""
Run Spider - CLI wrapper to execute the Job Spider pipeline.

Usage:
  # Run with default queries (python, data engineer, fullstack, etc.)
  python scripts/run_spider.py

  # Run with custom queries
  python scripts/run_spider.py --query "python" "react" "devops"

  # Run with higher limits
  python scripts/run_spider.py --query "python" --limit 100 --concurrency 8
"""
import asyncio
import sys
import os

# Add the backend app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/backend")))

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def run():
    from app.services.jobsearch.spider import JobSpider, main
    await main()


if __name__ == "__main__":
    asyncio.run(run())

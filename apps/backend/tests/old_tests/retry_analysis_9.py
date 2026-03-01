import asyncio
import sys
import os

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.getcwd())

from app.services.analyzer import ResumeAnalyzer

async def retry():
    print("Manually triggering analysis for Resume 9...")
    analyzer = ResumeAnalyzer()
    
    # Check if keys are loaded
    from app.core.config import settings
    print(f"OpenAI Key present: {bool(settings.OPENAI_API_KEY)}")
    print(f"Gemini Key present: {bool(settings.GEMINI_API_KEY)}")

    await analyzer.process_resume_task(9)
    print("Analysis task completed.")

if __name__ == "__main__":
    asyncio.run(retry())

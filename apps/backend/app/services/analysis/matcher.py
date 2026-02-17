import json
import logging
from typing import Dict, Any, List

from app.core.config import settings
from app.services.analysis.prompts import JOB_MATCH_PROMPT

# Import Clients
from app.services.analysis.openai_client import OpenAIClient
from app.services.analysis.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class MatcherService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.provider = settings.LLM_PROVIDER.lower()
        self.client = None
        
        try:
            if self.provider == "openai":
                self.client = OpenAIClient() # api_key taken from settings usually
            else:
                self.client = GeminiClient(api_key)
        except Exception as e:
            logger.error(f"Failed to initialize MatcherService client for {self.provider}: {e}")

    async def analyze_fit(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """
        Compare resume with job description and return match score, pros, and cons.
        """
        if not self.client:
             logger.error("MatcherService client not initialized.")
             return {
                "match_score": 0,
                "pros": [],
                "cons": ["AI Service Unavailable"]
             }

        prompt = JOB_MATCH_PROMPT.format(
            resume_text=resume_text,
            job_description=job_description
        )

        try:
            # Use the generic analyze_text method we added to both clients
            if hasattr(self.client, 'analyze_text'):
                data = await self.client.analyze_text(prompt)
            else:
                # Fallback or error if method missing
                raise NotImplementedError(f"Client for {self.provider} does not support analyze_text")
            
            return {
                "match_score": data.get("match_score", 0),
                "pros": data.get("pros", []),
                "cons": data.get("cons", [])
            }
        except Exception as e:
            logger.error(f"Error in MatcherService analyze_fit: {e}")
            return {
                "match_score": 0,
                "pros": [],
                "cons": ["Error analyzing job fit."]
            }

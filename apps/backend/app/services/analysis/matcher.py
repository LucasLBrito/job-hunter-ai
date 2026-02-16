import json
import logging
from typing import Dict, Any, List

from app.core.config import settings
from app.services.analysis.prompts import JOB_MATCH_PROMPT

# Import Gemini/LLM client. Using simple HTTP request for now or existing client if available.
# In Phase 3 we used google.generativeai. Let's keep consistency or use a helper.
# For now, let's implement a simple direct call wrapper or reuse OptimizationService logic pattern.

import google.generativeai as genai

logger = logging.getLogger(__name__)

class Action:
    # Enum for matching actions if needed
    pass

class MatcherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash') # Or use config model

    async def analyze_fit(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """
        Compare resume with job description and return match score, pros, and cons.
        """
        prompt = JOB_MATCH_PROMPT.format(
            resume_text=resume_text,
            job_description=job_description
        )

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text
            
            # Cleaning JSON
            cleaned_text = result_text.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(cleaned_text)
            
            return {
                "match_score": data.get("match_score", 0),
                "pros": data.get("pros", []),
                "cons": data.get("cons", [])
            }
        except Exception as e:
            logger.error(f"Error in MatcherService: {e}")
            # Fallback
            return {
                "match_score": 0,
                "pros": [],
                "cons": ["Error analyzing job fit."]
            }

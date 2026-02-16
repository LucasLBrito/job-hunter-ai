import logging
import httpx
import json
from typing import Optional, Dict, Any
from app.models.user import User
from app.services.analysis.prompts import OPTIMIZE_RESUME_PROMPT

logger = logging.getLogger(__name__)

class OptimizationService:
    GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    
    @staticmethod
    async def optimize_resume(
        user: User,
        resume_text: str,
        job_description: str,
        model: str = "gemini-1.5-flash"
    ) -> Dict[str, Any]:
        """
        Optimize resume using User's LLM API Key.
        Currently supports Gemini.
        """
        if not user.gemini_api_key:
             return {"error": "Gemini API Key not configured in user profile."}

        prompt = OPTIMIZE_RESUME_PROMPT.format(
            resume_text=resume_text,
            job_description=job_description
        )

        try:
            # Call Gemini REST API directly to avoid global state issues with SDK
            async with httpx.AsyncClient() as client:
                url = OptimizationService.GEMINI_BASE_URL.format(model=model)
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }
                
                response = await client.post(
                    url,
                    params={"key": user.gemini_api_key},
                    json=payload,
                    timeout=60.0 # Longer timeout for generation
                )
                
                if response.status_code != 200:
                    logger.error(f"Gemini API Error: {response.text}")
                    return {"error": f"LLM API Error: {response.status_code} - {response.text}"}
                
                data = response.json()
                
                # Extract text from Gemini response structure
                try:
                    optimized_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return {"optimized_content": optimized_text}
                except (KeyError, IndexError) as e:
                    logger.error(f"Failed to parse Gemini response: {data}")
                    return {"error": "Failed to parse LLM response format"}

        except Exception as e:
            logger.error(f"Optimization service error: {e}")
            return {"error": str(e)}

optimization_service = OptimizationService()

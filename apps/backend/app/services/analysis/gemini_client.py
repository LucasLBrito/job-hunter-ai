import google.generativeai as genai
import json
import logging
from typing import Dict, Any, Optional
from app.core.config import settings
from app.services.analysis.prompts import EXTRACT_RESUME_DATA_PROMPT

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for Google Gemini API"""
    
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not set. AI analysis will be disabled.")
            self.model = None
            return
            
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = None
        
        # Try to initialize with available models (Verified via test_gemini.py)
        models_to_try = [
            'gemini-2.0-flash', 
            'gemini-flash-latest', 
            'gemini-1.5-flash', 
            'gemini-pro',
            'models/gemini-flash-latest'
        ]
        
        for model_name in models_to_try:
            try:
                self.model = genai.GenerativeModel(model_name)
                self.model_name = model_name
                logger.info(f"Initialized Gemini with model: {model_name}")
                break
            except Exception as e:
                logger.warning(f"Failed to initialize model {model_name}: {e}")
                
    async def analyze_resume(self, text: str) -> Dict[str, Any]:
        """
        Analyze resume text and return structured data.
        """
        if not self.model:
            raise ValueError("Gemini API not configured")
            
        try:
            prompt = EXTRACT_RESUME_DATA_PROMPT.format(resume_text=text)
            
            # Use the correct async method for Gemini with retry logic
            max_retries = 3
            base_delay = 2
            
            for attempt in range(max_retries):
                try:
                    response = await self.model.generate_content_async(prompt)
                    break
                except Exception as e:
                    if "429" in str(e):
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)
                            logger.warning(f"Rate limit hit (429). Retrying in {delay}s...")
                            import asyncio
                            await asyncio.sleep(delay)
                            continue
                        else:
                            logger.error(f"Rate limit exceeded after {max_retries} attempts.")
                            raise e
                    # If the first model fails (e.g. 404), try fallback if we haven't already
                    elif "404" in str(e) and self.model_name != 'gemini-pro':
                         logger.warning(f"Model {self.model_name} failed with 404, trying gemini-pro")
                         self.model = genai.GenerativeModel('gemini-pro')
                         self.model_name = 'gemini-pro'
                         # Retry immediately with new model
                         continue
                    else:
                        raise e
            
            # Clean up response text to ensure valid JSON
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            try:
                data = json.loads(response_text)
                return data
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from Gemini response: {response_text}")
                # Fallback: return raw text in a wrapper
                return {"_raw": response_text, "error": "JSON parse failed"}
            
        except Exception as e:
            logger.error(f"Error analyzing resume with Gemini: {e}")
            raise

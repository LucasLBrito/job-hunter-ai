import google.generativeai as genai
import json
import logging
from typing import Dict, Any, Optional
from app.core.config import settings
from app.services.analysis.prompts import EXTRACT_RESUME_DATA_PROMPT

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        key = api_key or settings.GEMINI_API_KEY
        if not key:
            logger.warning("GEMINI_API_KEY not set. AI analysis will be disabled.")
            self.model = None
            return
            
        genai.configure(api_key=key)
        self.model = None
        
        # Try to initialize with available models
        models_to_try = [
            'gemini-1.5-flash',
            'gemini-flash-latest', 
            'gemini-pro',
            'models/gemini-1.5-flash'
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
            response = None
            
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
                            raise
                    else:
                        raise
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini")
                        
            # Clean up response text to ensure valid JSON
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
                
            try:
                data = json.loads(response_text)
                return data
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from Gemini response: {response_text[:200]}")
                return {"_raw": response_text, "error": "JSON parse failed"}
            
        except Exception as e:
            logger.error(f"Error analyzing resume with Gemini ({getattr(self, 'model_name', 'unknown')}): {e}")
            raise

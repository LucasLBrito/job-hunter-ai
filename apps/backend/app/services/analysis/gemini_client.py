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
        
        # 1. List available models
        available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            logger.info(f"Available Gemini models: {available_models}")
        except Exception as e:
            logger.warning(f"Failed to list Gemini models: {e}")
            
        # 2. Select best model
        # Preference: 1.5 Flash (fast/cheap) -> 1.5 Pro -> Pro -> 1.0
        preferences = [
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro',
            'models/gemini-pro',
            'models/gemini-1.0-pro'
        ]
        
        selected_model = None
        
        # Check preferences against available
        for pref in preferences:
            if pref in available_models:
                selected_model = pref
                break
                
        # Fallback: check if short names work (sometimes list_models returns absolute paths)
        if not selected_model:
            for pref in preferences:
                short_name = pref.replace('models/', '')
                if short_name in available_models:
                    selected_model = short_name
                    break
        
        # Fallback: take first available
        if not selected_model and available_models:
            selected_model = available_models[0]
            
        # Hard fallback
        if not selected_model:
            selected_model = 'gemini-1.5-flash'
            
        try:
            self.model = genai.GenerativeModel(selected_model)
            self.model_name = selected_model
            logger.info(f"Initialized Gemini with model: {selected_model}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini with {selected_model}: {e}")
            self.model = None
                
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

    async def analyze_text(self, prompt: str) -> Dict[str, Any]:
        """
        Generic text analysis execution.
        """
        if not self.model:
            raise ValueError("Gemini API not configured")
            
        try:
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
                # Try simple clean if failed
                logger.error(f"Failed to parse JSON from Gemini response: {response_text[:200]}")
                return {"_raw": response_text, "error": "JSON parse failed"}
            
        except Exception as e:
            logger.error(f"Error analyzing text with Gemini ({getattr(self, 'model_name', 'unknown')}): {e}")
            raise


import logging
import json
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from app.core.config import settings
from app.services.analysis.prompts import EXTRACT_RESUME_DATA_PROMPT

logger = logging.getLogger(__name__)

class OpenAIClient:
    """Client for OpenAI API"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model_name = "gpt-4o-mini" # Cost-effective model
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set. AI analysis fallback will be disabled.")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info(f"Initialized OpenAI with model: {self.model_name}")

    async def analyze_resume(self, text: str) -> Dict[str, Any]:
        """
        Analyze resume text and return structured data using OpenAI.
        """
        if not self.client:
            raise ValueError("OpenAI API not configured")
            
        try:
            prompt = EXTRACT_RESUME_DATA_PROMPT.format(resume_text=text)
            
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts data from resumes in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")
                
            try:
                data = json.loads(content)
                return data
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from OpenAI response: {content}")
                return {"_raw": content, "error": "JSON parse failed"}
                
        except Exception as e:
            logger.error(f"Error analyzing resume with OpenAI: {e}")
            raise e

    async def analyze_text(self, prompt: str) -> Dict[str, Any]:
        """
        Generic text analysis execution.
        """
        if not self.client:
            raise ValueError("OpenAI API not configured")
            
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Output valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")
                
            try:
                data = json.loads(content)
                return data
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from OpenAI response: {content}")
                return {"_raw": content, "error": "JSON parse failed"}
                
        except Exception as e:
            logger.error(f"Error analyzing text with OpenAI: {e}")
            raise e


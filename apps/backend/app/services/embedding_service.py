import logging
import google.generativeai as genai
from typing import List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            logger.warning("Gemini API Key not found. Embedding service will fail.")
        else:
            genai.configure(api_key=self.api_key)

    async def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text using Gemini.
        Model: models/text-embedding-004
        """
        if not self.api_key:
            raise ValueError("Gemini API Key not configured")
            
        try:
            # Clean text
            text = text.replace("\n", " ")
            
            # Generate embedding
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document",
                title="Embedding of text"
            )
            
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise e

    async def get_query_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a query (search term).
        """
        if not self.api_key:
            raise ValueError("Gemini API Key not configured")

        try:
            # Clean text
            text = text.replace("\n", " ")
            
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_query"
            )
            
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise e

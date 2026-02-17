import logging
import json
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.services.extraction.local import LocalTextExtractor
from app.services.analysis.gemini_client import GeminiClient
from app.services.analysis.openai_client import OpenAIClient
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    """
    Orchestrator service for Resume Analysis.
    Combines Text Extraction (Local) + AI Analysis (Gemini/OpenAI).
    """
    
    def __init__(self):
        self.extractor = LocalTextExtractor()
        self.gemini = GeminiClient()
        self.openai = OpenAIClient()
        
    async def process_resume_task(self, resume_id: int, db: AsyncSession = None):
        """
        Background task to process a resume.
        Creates its own DB session for background execution.
        """
        logger.info(f"Starting analysis for resume {resume_id}")
        
        # Create a new session for background task (request session may be closed)
        async with AsyncSessionLocal() as session:
            try:
                await self._do_analysis(resume_id, session)
            except Exception as e:
                logger.error(f"Unexpected error in process_resume_task for {resume_id}: {e}")
    
    async def _do_analysis(self, resume_id: int, db: AsyncSession):
        """Core analysis logic with its own DB session."""
        
        # 1. Get Resume
        resume = await crud.resume.get(db=db, id=resume_id)
        if not resume:
            logger.error(f"Resume {resume_id} not found during background task")
            return

        # 2. Extract Text
        try:
            raw_text = await self.extractor.extract_text(Path(resume.file_path))
            if not raw_text or len(raw_text) < 50:
                logger.warning(f"Extracted text for resume {resume_id} is too short or empty.")
        except Exception as e:
            logger.error(f"Extraction failed for resume {resume_id}: {e}")
            return

        # 3. AI Analysis
        ai_data = {}
        analysis_successful = False
        
        # 3. AI Analysis
        ai_data = {}
        analysis_successful = False
        
        from app.core.config import settings
        provider = settings.LLM_PROVIDER.lower()
        
        # Function to try Gemini
        async def try_gemini():
            if self.gemini.model:
                try:
                    logger.info(f"Sending resume {resume_id} text to Gemini...")
                    return await self.gemini.analyze_resume(raw_text), True
                except Exception as e:
                    logger.error(f"Gemini Analysis failed for resume {resume_id}: {e}")
            else:
                logger.warning("Gemini not configured.")
            return {}, False

        # Function to try OpenAI
        async def try_openai():
            if self.openai.client:
                try:
                    logger.info(f"Sending resume {resume_id} text to OpenAI...")
                    return await self.openai.analyze_resume(raw_text), True
                except Exception as e:
                    logger.error(f"OpenAI Analysis failed for resume {resume_id}: {e}")
            else:
                logger.warning("OpenAI not configured.")
            return {}, False

        # Logic based on provider
        if provider == "openai":
            ai_data, analysis_successful = await try_openai()
            # Fallback to Gemini if OpenAI fails (optional, maybe not desired if explicit)
            if not analysis_successful:
                 ai_data, analysis_successful = await try_gemini()
        else:
            # Default/Gemini
            ai_data, analysis_successful = await try_gemini()
            if not analysis_successful:
                ai_data, analysis_successful = await try_openai()
        
        if not analysis_successful:
            logger.error("All AI services failed to analyze the resume.")

        # 4. Generate & Store Embedding (Pinecone) - optional
        try:
            from app.services.embedding_service import EmbeddingService
            from app.services.pinecone_service import PineconeService
            
            embed_text = ""
            if ai_data:
                embed_text = f"{ai_data.get('ai_summary', '')} {' '.join(ai_data.get('technical_skills', []))} {' '.join(ai_data.get('soft_skills', []))}"
            else:
                embed_text = raw_text[:8000]
            
            if embed_text:
                embedding_service = EmbeddingService()
                if embedding_service.api_key:
                    vector = await embedding_service.get_embedding(embed_text)
                    
                    pinecone_service = PineconeService()
                    pinecone_service.upsert_resume(
                        resume_id=resume.id,
                        embedding=vector,
                        metadata={
                            "user_id": resume.user_id,
                            "skills": ai_data.get('technical_skills', []) if ai_data else [],
                            "filename": resume.filename
                        }
                    )
        except Exception as e:
            logger.warning(f"Embedding/Pinecone skipped for resume {resume_id}: {e}")

        # 5. Prepare Update Data
        ai_data = ai_data or {}
        has_data = bool(ai_data and not ai_data.get('error'))
        
        if has_data:
            update_data = schemas.ResumeUpdate(
                raw_text=raw_text,
                structured_data=json.dumps(ai_data),
                is_analyzed=True,
                ai_summary=ai_data.get("ai_summary"),
                years_of_experience=ai_data.get("years_of_experience"),
                technical_skills=json.dumps(ai_data.get("technical_skills", [])),
                soft_skills=json.dumps(ai_data.get("soft_skills", [])),
                education=json.dumps(ai_data.get("education", [])),
                work_experience=json.dumps(ai_data.get("work_experience", [])),
                certifications=json.dumps(ai_data.get("certifications", []))
            )
            await crud.resume.update(db=db, db_obj=resume, obj_in=update_data)
            
            resume.analyzed_at = datetime.utcnow()
            await db.commit()
            logger.info(f"Successfully analyzed resume {resume_id}")
        else:
            error_msg = f"ERROR: Analysis failed. Please try again. (Details: {ai_data.get('error', 'Unknown error')})"
            
            update_data = schemas.ResumeUpdate(
                raw_text=raw_text,
                ai_summary=error_msg,
                is_analyzed=False 
            )
            await crud.resume.update(db=db, db_obj=resume, obj_in=update_data)
            await db.commit()
            logger.warning(f"Analysis failed for resume {resume_id}. Error saved to summary.")

resume_analyzer = ResumeAnalyzer()

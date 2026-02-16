import logging
import json
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.services.extraction.local import LocalTextExtractor
from app.services.analysis.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    """
    Orchestrator service for Resume Analysis.
    Combines Text Extraction (Local) + AI Analysis (Gemini).
    """
    
    def __init__(self):
        self.extractor = LocalTextExtractor()
        self.ai = GeminiClient()
        
    async def process_resume_task(self, resume_id: int, db: AsyncSession):
        """
        Background task to process a resume.
        1. Get resume from DB.
        2. Extract text from file.
        3. Send text to LLM for analysis.
        4. Update DB with results.
        """
        logger.info(f"Starting analysis for resume {resume_id}")
        
        try:
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
            if self.ai.model:
                try:
                    logger.info(f"Sending resume {resume_id} text to Gemini...")
                    ai_data = await self.ai.analyze_resume(raw_text)
                except Exception as e:
                    logger.error(f"AI Analysis failed for resume {resume_id}: {e}")
            else:
                logger.warning("Gemini not configured. Skipping AI analysis.")

            # 4. Generate & Store Embedding (Pinecone)
            try:
                from app.services.embedding_service import EmbeddingService
                from app.services.pinecone_service import PineconeService
                
                # Check for API key before proceeding (avoid crash if just extracting text)
                # But we want to fail gracefully
                
                # Create text representation for embedding (summary + skills + experience)
                # Use what we have from AI, or raw text if AI failed but we want semantic search on raw text
                # Ideally use structured data if available.
                
                embed_text = ""
                if ai_data:
                    embed_text = f"{ai_data.get('ai_summary', '')} {' '.join(ai_data.get('technical_skills', []))} {' '.join(ai_data.get('soft_skills', []))}"
                else:
                    embed_text = raw_text[:8000] # Truncate for embedding model limit if needed
                
                if embed_text:
                    # Generate embedding
                    embedding_service = EmbeddingService()
                    if embedding_service.api_key:
                        vector = await embedding_service.get_embedding(embed_text)
                        
                        # Upsert to Pinecone
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
                logger.error(f"Embedding/Pinecone failed for resume {resume_id}: {e}")
                # Don't throw, continue to save DB record

            # 5. Prepare Update Data
            ai_data = ai_data or {} # Ensure it's a dict if None
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
                # Save error state
                # We use ai_summary to store the error if analysis failed completely
                # This allows frontend to see something went wrong
                error_msg = f"ERROR: Analysis failed. Please try again. (Details: {ai_data.get('error', 'Unknown error')})"
                
                update_data = schemas.ResumeUpdate(
                    raw_text=raw_text,
                    ai_summary=error_msg,
                    is_analyzed=False 
                )
                await crud.resume.update(db=db, db_obj=resume, obj_in=update_data)
                await db.commit()
                logger.warning(f"Analysis failed for resume {resume_id}. Error saved to summary.")

        except Exception as e:
            logger.error(f"Unexpected error in process_resume_task for {resume_id}: {e}")

        except Exception as e:
            logger.error(f"Unexpected error in process_resume_task for {resume_id}: {e}")

resume_analyzer = ResumeAnalyzer()

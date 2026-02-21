import logging
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self):
        self.api_key = settings.PINECONE_KEY or settings.PINECONE_API_KEY
        self.index_name = settings.PINECONE_INDEX_NAME
        self.pc = None
        self.index = None
        
        if self.api_key:
            try:
                self.pc = Pinecone(api_key=self.api_key)
                # Check if index exists, if not create (careful with serverless specs)
                # For now, let's assume index exists or user creates it. 
                # Auto-creation can be complex with regions.
                self.index = self.pc.Index(self.index_name)
            except Exception as e:
                logger.error(f"Failed to initialize Pinecone: {e}")

    def upsert_resume(self, resume_id: int, embedding: List[float], metadata: Dict[str, Any]):
        """
        Upsert a resume vector.
        Namespace: 'resumes'
        """
        if not self.index:
            logger.warning("Pinecone index not initialized.")
            return

        try:
            # Flatten metadata if needed or ensure simple types
            # Pinecone metadata: string, number, boolean, list of strings
            clean_metadata = {k: v for k, v in metadata.items() if v is not None}
            
            self.index.upsert(
                vectors=[
                    {
                        "id": str(resume_id), 
                        "values": embedding, 
                        "metadata": clean_metadata
                    }
                ],
                namespace="resumes"
            )
            logger.info(f"Upserted resume {resume_id} to Pinecone.")
        except Exception as e:
            logger.error(f"Error upserting resume {resume_id}: {e}")

    def upsert_job(self, job_id: int, embedding: List[float], metadata: Dict[str, Any]):
        """
        Upsert a job vector.
        Namespace: 'jobs'
        """
        if not self.index:
            logger.warning("Pinecone index not initialized.")
            return

        try:
            clean_metadata = {k: v for k, v in metadata.items() if v is not None}
            
            self.index.upsert(
                vectors=[
                    {
                        "id": str(job_id), 
                        "values": embedding, 
                        "metadata": clean_metadata
                    }
                ],
                namespace="jobs"
            )
            logger.info(f"Upserted job {job_id} to Pinecone.")
        except Exception as e:
            logger.error(f"Error upserting job {job_id}: {e}")

    def get_resume_vector(self, resume_id: int) -> Optional[List[float]]:
        """
        Fetch resume vector from Pinecone.
        """
        if not self.index:
            return None
            
        try:
            fetch_response = self.index.fetch(ids=[str(resume_id)], namespace="resumes")
            if fetch_response and fetch_response.vectors and str(resume_id) in fetch_response.vectors:
                return fetch_response.vectors[str(resume_id)].values
            return None
        except Exception as e:
            logger.error(f"Error fetching resume vector {resume_id}: {e}")
            return None

    def search_jobs(self, query_embedding: List[float], top_k: int = 10, filter: Optional[Dict] = None) -> List[Dict]:
        """
        Search for jobs similar to the query embedding.
        """
        if not self.index:
            logger.warning("Pinecone index not initialized.")
            return []

        try:
            results = self.index.query(
                namespace="jobs",
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter
            )
            
            return [
                {
                    "id": int(match.id),
                    "score": match.score,
                    "metadata": match.metadata
                }
                for match in results.matches
            ]
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            return []

import logging
from pathlib import Path
from typing import Optional
import pypdf
import docx

from app.services.extraction.base import TextExtractor

logger = logging.getLogger(__name__)

class LocalTextExtractor(TextExtractor):
    """Local implementation using pypdf and python-docx"""
    
    async def extract_text(self, file_path: Path) -> str:
        """Extract text from PDF or DOCX using local libraries"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == '.pdf':
                return self._extract_pdf(file_path)
            elif suffix in ['.docx', '.doc']:
                return self._extract_docx(file_path)
            elif suffix in ['.txt', '.md', '.markdown']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise ValueError(f"Unsupported file type: {suffix}")
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            raise

    def _extract_pdf(self, file_path: Path) -> str:
        text = []
        with open(file_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text() or "")
        return "\n".join(text)

    def _extract_docx(self, file_path: Path) -> str:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

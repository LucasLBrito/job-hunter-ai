from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

class TextExtractor(ABC):
    """Base interface for text extraction services"""
    
    @abstractmethod
    async def extract_text(self, file_path: Path) -> str:
        """
        Extract text from a file
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Extracted text as string
            
        Raises:
            ValueError: If file type is not supported
            Exception: If extraction fails
        """
        pass

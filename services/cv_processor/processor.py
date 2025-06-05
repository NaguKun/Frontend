import fitz  # PyMuPDF
import logging
from typing import Optional, Union
import os
import io
from app.core.config import settings

logger = logging.getLogger(__name__)

class CVProcessor:
    def __init__(self):
        self.supported_extensions = {'.pdf'}
    
    def extract_text(self, file_path_or_bytes: Union[str, bytes]) -> str:
        """
        Extract text from a PDF file or bytes.
        
        Args:
            file_path_or_bytes: Either a path to the PDF file or bytes content of the PDF
            
        Returns:
            str: Extracted text from the PDF
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file does not exist (when using file path)
            Exception: For other processing errors
        """
        if isinstance(file_path_or_bytes, str):
            return self._extract_text_from_file(file_path_or_bytes)
        elif isinstance(file_path_or_bytes, bytes):
            return self._extract_text_from_bytes(file_path_or_bytes)
        else:
            raise ValueError("Input must be either a file path (str) or bytes")
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text from a PDF file path."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        try:
            # Open the PDF
            doc = fitz.open(file_path)
            text = self._extract_text_from_doc(doc)
            doc.close()
            return text
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            raise
    
    def _extract_text_from_bytes(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes."""
        try:
            # Open the PDF from bytes
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = self._extract_text_from_doc(doc)
            doc.close()
            return text
            
        except Exception as e:
            logger.error(f"Error processing PDF bytes: {str(e)}")
            raise
    
    def _extract_text_from_doc(self, doc: fitz.Document) -> str:
        """Extract and clean text from a PyMuPDF document."""
        text = ""
        for page in doc:
            text += page.get_text()
        
        return self._clean_text(text)
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters that might interfere with processing
        text = text.replace('\x00', '')
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove multiple consecutive newlines
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        
        return text.strip()
    
    def validate_pdf(self, file_path_or_bytes: Union[str, bytes]) -> bool:
        """
        Validate if a PDF file is readable and not corrupted.
        
        Args:
            file_path_or_bytes: Either a path to the PDF file or bytes content of the PDF
            
        Returns:
            bool: True if PDF is valid, False otherwise
        """
        try:
            if isinstance(file_path_or_bytes, str):
                doc = fitz.open(file_path_or_bytes)
            else:
                doc = fitz.open(stream=file_path_or_bytes, filetype="pdf")
                
            # Try to read the first page
            if doc.page_count > 0:
                doc[0].get_text()
            doc.close()
            return True
        except Exception as e:
            logger.error(f"PDF validation failed: {str(e)}")
            return False 
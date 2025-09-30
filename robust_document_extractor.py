#!/usr/bin/env python3
"""
Robust Document Text Extractor with Multiple Fallback Methods
Handles corrupted files and various document formats for BRD compliance
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Tuple

# Try importing different text extraction libraries
try:
    import fitz  # PyMuPDF for PDF
except ImportError:
    fitz = None

try:
    import docx  # python-docx for DOCX
except ImportError:
    docx = None

try:
    import docx2txt  # docx2txt as fallback
except ImportError:
    docx2txt = None

try:
    import textract  # textract as universal fallback
except ImportError:
    textract = None

try:
    import subprocess  # For command-line tools
except ImportError:
    subprocess = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustDocumentExtractor:
    """
    Enhanced document text extractor with multiple fallback methods
    for achieving BRD compliance with document format compatibility
    """

    def __init__(self):
        self.extraction_methods = []
        self._initialize_methods()

    def _initialize_methods(self):
        """Initialize available extraction methods in priority order"""

        # PDF extraction methods
        if fitz:
            self.extraction_methods.append(('pdf_pymupdf', self._extract_pdf_pymupdf))

        # DOCX extraction methods
        if docx:
            self.extraction_methods.append(('docx_python_docx', self._extract_docx_python_docx))
        if docx2txt:
            self.extraction_methods.append(('docx_docx2txt', self._extract_docx_docx2txt))

        # Legacy DOC extraction methods
        if textract:
            self.extraction_methods.append(('doc_textract', self._extract_doc_textract))
        if subprocess:
            self.extraction_methods.append(('doc_antiword', self._extract_doc_antiword))
            self.extraction_methods.append(('doc_catdoc', self._extract_doc_catdoc))

        # Universal fallback
        if textract:
            self.extraction_methods.append(('universal_textract', self._extract_universal_textract))

        logger.info(f"Initialized {len(self.extraction_methods)} extraction methods")

    def extract_text(self, file_path: str, filename: str = None) -> Tuple[str, str]:
        """
        Extract text from document with multiple fallback methods

        Args:
            file_path: Path to the document file
            filename: Optional filename (will be derived from path if not provided)

        Returns:
            Tuple of (extracted_text, method_used)
        """
        if filename is None:
            filename = os.path.basename(file_path)

        file_ext = Path(filename).suffix.lower()

        logger.info(f"Extracting text from {filename} (format: {file_ext})")

        # Try each extraction method in order
        for method_name, method_func in self.extraction_methods:
            if not self._method_supports_format(method_name, file_ext):
                continue

            try:
                logger.debug(f"Trying extraction method: {method_name}")
                text = method_func(file_path, file_ext)

                if text and len(text.strip()) > 50:  # Ensure we got meaningful content
                    logger.info(f"Successfully extracted text using {method_name}")
                    return text, method_name
                else:
                    logger.debug(f"Method {method_name} returned insufficient content")

            except Exception as e:
                logger.debug(f"Method {method_name} failed: {str(e)}")
                continue

        # If all methods failed
        error_msg = f"All extraction methods failed for {filename} (format: {file_ext})"
        logger.error(error_msg)
        return f"Error: {error_msg}", "none"

    def _method_supports_format(self, method_name: str, file_ext: str) -> bool:
        """Check if extraction method supports the file format"""

        format_support = {
            'pdf_pymupdf': ['.pdf'],
            'docx_python_docx': ['.docx', '.doc'],
            'docx_docx2txt': ['.docx'],
            'doc_textract': ['.doc', '.docx'],
            'doc_antiword': ['.doc'],
            'doc_catdoc': ['.doc'],
            'universal_textract': ['.pdf', '.doc', '.docx', '.txt', '.rtf']
        }

        supported_formats = format_support.get(method_name, [])
        return file_ext in supported_formats

    def _extract_pdf_pymupdf(self, file_path: str, file_ext: str) -> str:
        """Extract text from PDF using PyMuPDF"""
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text

    def _extract_docx_python_docx(self, file_path: str, file_ext: str) -> str:
        """Extract text from DOCX/DOC using python-docx"""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def _extract_docx_docx2txt(self, file_path: str, file_ext: str) -> str:
        """Extract text from DOCX using docx2txt"""
        return docx2txt.process(file_path)

    def _extract_doc_textract(self, file_path: str, file_ext: str) -> str:
        """Extract text from DOC using textract"""
        return textract.process(file_path).decode('utf-8', errors='ignore')

    def _extract_doc_antiword(self, file_path: str, file_ext: str) -> str:
        """Extract text from DOC using antiword command-line tool"""
        try:
            result = subprocess.run(['antiword', file_path],
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        raise Exception("antiword extraction failed")

    def _extract_doc_catdoc(self, file_path: str, file_ext: str) -> str:
        """Extract text from DOC using catdoc command-line tool"""
        try:
            result = subprocess.run(['catdoc', file_path],
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        raise Exception("catdoc extraction failed")

    def _extract_universal_textract(self, file_path: str, file_ext: str) -> str:
        """Extract text using textract as universal fallback"""
        return textract.process(file_path).decode('utf-8', errors='ignore')

    def get_available_methods(self) -> list:
        """Get list of available extraction methods"""
        return [method_name for method_name, _ in self.extraction_methods]

# Convenience function for easy usage
def extract_text_robust(file_path: str, filename: str = None) -> Tuple[str, str]:
    """
    Convenience function to extract text with robust fallback

    Returns:
        Tuple of (extracted_text, method_used)
    """
    extractor = RobustDocumentExtractor()
    return extractor.extract_text(file_path, filename)

if __name__ == "__main__":
    # Test the extractor
    if len(sys.argv) != 2:
        print("Usage: python3 robust_document_extractor.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    text, method = extract_text_robust(file_path)

    print(f"Extraction method used: {method}")
    print(f"Text length: {len(text)} characters")
    print(f"First 200 characters:\n{text[:200]}...")
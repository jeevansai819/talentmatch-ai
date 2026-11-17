import os
import pymupdf  # PyMuPDF
from typing import Tuple, Optional

class PDFExtractionError(Exception):
    """Custom exception raised when PDF parsing or validation fails."""
    pass

class PDFExtractor:
    """Service to safely inspect, validate and extract text from PDF resumes."""

    @staticmethod
    def extract_text(file_path: str) -> Tuple[str, int]:
        """
        Extract full textual content and page count from a PDF file.

        Args:
            file_path: Absolute or relative path to the PDF file.

        Returns:
            Tuple of (extracted_text, page_count)

        Raises:
            PDFExtractionError: If file is missing, encrypted, corrupted, or empty.
        """
        if not os.path.exists(file_path):
            raise PDFExtractionError(f"File not found at path: {file_path}")

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise PDFExtractionError("The uploaded PDF file is empty (0 bytes).")

        try:
            doc = pymupdf.open(file_path)
        except Exception as e:
            raise PDFExtractionError(f"Corrupted or invalid PDF file: {str(e)}")

        try:
            if doc.is_encrypted:
                raise PDFExtractionError("Password-protected or encrypted PDFs are not supported. Please upload an unlocked PDF.")

            page_count = len(doc)
            if page_count == 0:
                raise PDFExtractionError("The uploaded PDF contains no pages.")

            text_chunks = []
            for page_idx in range(page_count):
                page = doc[page_idx]
                page_text = page.get_text("text")
                if page_text:
                    text_chunks.append(page_text.strip())

            full_text = "\n\n".join(text_chunks).strip()

            if not full_text:
                raise PDFExtractionError(
                    "No readable text could be extracted. The PDF may be a scanned image or empty. "
                    "Please upload a searchable text-based PDF."
                )

            return full_text, page_count

        finally:
            doc.close()

    @staticmethod
    def extract_metadata(file_path: str) -> dict:
        """Extract internal PDF metadata (title, author, creation date) if available."""
        try:
            doc = pymupdf.open(file_path)
            metadata = doc.metadata or {}
            doc.close()
            return metadata
        except Exception:
            return {}

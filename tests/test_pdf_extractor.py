import os
import pytest
import pymupdf
from app.services.pdf_extractor import PDFExtractor, PDFExtractionError

def test_extract_text_valid_pdf(tmp_path):
    pdf_path = os.path.join(tmp_path, "sample.pdf")
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Jane Doe\nPython Developer with 5 years experience.")
    doc.save(pdf_path)
    doc.close()

    text, page_count = PDFExtractor.extract_text(pdf_path)
    assert page_count == 1
    assert "Jane Doe" in text
    assert "Python Developer" in text

def test_extract_text_missing_file():
    with pytest.raises(PDFExtractionError) as exc_info:
        PDFExtractor.extract_text("non_existent_file.pdf")
    assert "not found" in str(exc_info.value).lower()

def test_extract_text_empty_file(tmp_path):
    empty_path = os.path.join(tmp_path, "empty.pdf")
    with open(empty_path, "wb") as f:
        pass

    with pytest.raises(PDFExtractionError) as exc_info:
        PDFExtractor.extract_text(empty_path)
    assert "empty" in str(exc_info.value).lower()

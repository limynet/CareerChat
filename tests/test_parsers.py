"""Unit tests for PDF and DOCX text extraction parsers."""
import io

import pytest
from docx import Document

from src.parsers.pdf_parser import extract_text_from_pdf
from src.parsers.docx_parser import extract_text_from_docx


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_docx_bytes(paragraphs: list[str]) -> bytes:
    """Create a DOCX file in memory with the given paragraphs and return its bytes."""
    doc = Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# Minimal valid PDF with text "Hello World".
# Built by hand: 1 page, Helvetica font, one text object.
_MINIMAL_PDF = (
    b"%PDF-1.0\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R"
    b"/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj\n"
    b"4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n"
    b"5 0 obj<</Length 44>>stream\n"
    b"BT /F1 12 Tf 100 700 Td (Hello World) Tj ET\n"
    b"endstream\nendobj\n"
    b"xref\n0 6\n"
    b"0000000000 65535 f \n"
    b"0000000009 00000 n \n"
    b"0000000058 00000 n \n"
    b"0000000115 00000 n \n"
    b"0000000266 00000 n \n"
    b"0000000340 00000 n \n"
    b"trailer<</Size 6/Root 1 0 R>>\n"
    b"startxref\n434\n%%EOF\n"
)


# ---------------------------------------------------------------------------
# PDF parser tests
# ---------------------------------------------------------------------------

class TestPdfParser:
    def test_extracts_text_from_valid_pdf(self):
        text = extract_text_from_pdf(_MINIMAL_PDF)
        assert "Hello World" in text

    def test_raises_on_empty_bytes(self):
        # Empty bytes is not a valid PDF — pdfplumber will raise
        with pytest.raises(Exception):
            extract_text_from_pdf(b"")

    def test_returns_string(self):
        text = extract_text_from_pdf(_MINIMAL_PDF)
        assert isinstance(text, str)

    def test_strips_whitespace(self):
        text = extract_text_from_pdf(_MINIMAL_PDF)
        assert text == text.strip()


# ---------------------------------------------------------------------------
# DOCX parser tests
# ---------------------------------------------------------------------------

class TestDocxParser:
    def test_extracts_text_from_valid_docx(self):
        docx_bytes = _make_docx_bytes(["Hello from DOCX", "Second paragraph"])
        text = extract_text_from_docx(docx_bytes)
        assert "Hello from DOCX" in text
        assert "Second paragraph" in text

    def test_raises_on_empty_docx(self):
        # DOCX with no paragraphs
        docx_bytes = _make_docx_bytes([])
        with pytest.raises(ValueError, match="No text could be extracted"):
            extract_text_from_docx(docx_bytes)

    def test_ignores_blank_paragraphs(self):
        docx_bytes = _make_docx_bytes(["Hello", "", "   ", "World"])
        text = extract_text_from_docx(docx_bytes)
        assert "Hello" in text
        assert "World" in text

    def test_returns_string(self):
        docx_bytes = _make_docx_bytes(["Test content"])
        text = extract_text_from_docx(docx_bytes)
        assert isinstance(text, str)

    def test_raises_on_non_docx_bytes(self):
        with pytest.raises(Exception):
            extract_text_from_docx(b"this is not a docx file")

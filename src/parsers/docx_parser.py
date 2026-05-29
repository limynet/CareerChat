"""DOCX text extraction using python-docx."""
import io

from docx import Document


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file given its raw bytes.

    Args:
        file_bytes: Raw bytes of the DOCX file.

    Returns:
        Extracted text from all paragraphs joined by newlines.

    Raises:
        ValueError: If no text could be extracted from the DOCX.
    """
    doc = Document(io.BytesIO(file_bytes))
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip()
    if not text:
        raise ValueError("No text could be extracted from the DOCX")
    return text

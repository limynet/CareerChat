"""PDF text extraction using pdfplumber."""
import io

import pdfplumber


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file given its raw bytes.

    Args:
        file_bytes: Raw bytes of the PDF file.

    Returns:
        Extracted text from all pages joined by newlines.

    Raises:
        ValueError: If no text could be extracted from the PDF.
    """
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    text = "\n".join(text_parts).strip()
    if not text:
        raise ValueError("No text could be extracted from the PDF")
    return text

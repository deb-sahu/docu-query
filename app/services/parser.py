"""
Document Text Extraction
"""

from pathlib import Path
import pdfplumber
import docx


def extract_text_from_pdf(path: Path) -> str:
    """Extract text from a PDF file."""
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            try:
                text = page.extract_text() or ""
                if text.strip():
                    text_parts.append(text)
            except Exception:
                continue
    return "\n\n".join(text_parts)


def extract_text_from_docx(path: Path) -> str:
    """Extract text from a DOCX file."""
    doc = docx.Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def extract_text_from_txt(path: Path) -> str:
    """Read text from a plain text file."""
    return path.read_text(encoding="utf-8", errors="ignore")

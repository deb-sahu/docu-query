"""
Document Parser
===============

Text extraction and chunking utilities for different document formats.

This module provides functions to:
- Extract text from PDF files using pdfplumber
- Extract text from DOCX files using python-docx
- Extract text from plain TXT files
- Split text into overlapping chunks for similarity search

The chunking strategy uses a sliding window approach with configurable
size and overlap to ensure relevant passages aren't split awkwardly.
"""

from pathlib import Path
from typing import List
import pdfplumber
import docx
from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP


def extract_text_from_pdf(path: Path) -> str:
    """
    Extract text content from a PDF file.
    
    Uses pdfplumber to iterate through all pages and extract text.
    Pages that fail to parse are silently skipped.
    
    Args:
        path: Path to the PDF file.
        
    Returns:
        Extracted text with pages separated by double newlines.
        
    Example:
        >>> text = extract_text_from_pdf(Path("document.pdf"))
        >>> print(text[:100])
    """
    text_parts = []
    
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            try:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_parts.append(page_text)
            except Exception:
                # Skip pages that fail to parse (e.g., scanned images without OCR)
                continue
                
    return "\n\n".join(text_parts)


def extract_text_from_docx(path: Path) -> str:
    """
    Extract text content from a DOCX file.
    
    Uses python-docx to read paragraphs from the document.
    Only non-empty paragraphs are included.
    
    Args:
        path: Path to the DOCX file.
        
    Returns:
        Extracted text with paragraphs separated by double newlines.
        
    Example:
        >>> text = extract_text_from_docx(Path("document.docx"))
        >>> print(text[:100])
    """
    doc = docx.Document(str(path))
    
    # Extract only paragraphs with actual content
    paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
    
    return "\n\n".join(paragraphs)


def extract_text_from_txt(path: Path) -> str:
    """
    Read text content from a plain text file.
    
    Args:
        path: Path to the TXT file.
        
    Returns:
        The file's text content. Invalid characters are ignored.
        
    Example:
        >>> text = extract_text_from_txt(Path("notes.txt"))
    """
    return path.read_text(encoding="utf-8", errors="ignore")


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks for similarity search.
    
    Uses a sliding window approach where each chunk overlaps with the
    previous one. This helps maintain context when relevant information
    spans chunk boundaries.
    
    Algorithm:
        1. Start at position 0
        2. Take chunk_size characters
        3. Move forward by (chunk_size - overlap) characters
        4. Repeat until end of text
    
    Args:
        text: The input text to split.
        chunk_size: Maximum characters per chunk (default: from config).
        overlap: Characters to overlap between chunks (default: from config).
        
    Returns:
        List of text chunks. Empty if input is empty/whitespace.
        
    Example:
        >>> chunks = chunk_text("A very long document...", chunk_size=100, overlap=20)
        >>> len(chunks)
        15
        >>> len(chunks[0])  # First chunk is at most chunk_size
        100
    """
    if not text:
        return []
    
    # Normalize whitespace: remove carriage returns
    text = text.replace("\r", "")
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        # Define chunk boundaries
        end = start + chunk_size
        
        # Extract and clean the chunk
        chunk = text[start:end].strip()
        
        if chunk:
            chunks.append(chunk)
        
        # Stop if we've reached the end
        if end >= text_length:
            break
            
        # Move window forward, maintaining overlap with previous chunk
        start = end - overlap
    
    return chunks

"""
Storage Manager
===============

File storage utilities for handling document uploads and cleanup.

This module handles:
- Saving uploaded files to the uploads directory
- Validating file types (PDF, DOCX, TXT only)
- Generating unique document IDs
- Cleaning up files when documents are deleted
"""

from fastapi import UploadFile, HTTPException
from pathlib import Path
import shutil
from uuid import uuid4
from app.core.config import UPLOAD_DIR

# Supported file extensions for document upload
ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"]


def save_upload(file: UploadFile) -> tuple[str, Path]:
    """
    Save an uploaded file to the uploads directory.
    
    Generates a unique document ID (UUID) and saves the file with
    that ID as the filename, preserving the original extension.
    
    Args:
        file: FastAPI UploadFile object from the request.
        
    Returns:
        Tuple of (doc_id, file_path):
        - doc_id: Unique identifier for this document (UUID string)
        - file_path: Path object pointing to the saved file
        
    Raises:
        HTTPException 400: If filename is missing or file type is unsupported.
        
    Example:
        >>> doc_id, path = save_upload(uploaded_file)
        >>> print(doc_id)  # "a1b2c3d4-..."
        >>> print(path)    # "uploads/a1b2c3d4-....pdf"
    """
    # Validate filename exists
    if not file.filename:
        raise HTTPException(
            status_code=400, 
            detail="File must have a filename"
        )
    
    # Extract and validate file extension
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Generate unique document ID
    doc_id = str(uuid4())
    
    # Create destination path with UUID filename
    destination = UPLOAD_DIR / f"{doc_id}{extension}"
    
    try:
        # Stream file content to disk (memory-efficient for large files)
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        # Always close the uploaded file handle
        file.file.close()
    
    return doc_id, destination


def delete_file(path: Path) -> None:
    """
    Delete a file from the filesystem.
    
    Silently handles cases where the file doesn't exist or
    cannot be deleted (e.g., permission issues).
    
    Args:
        path: Path to the file to delete.
        
    Note:
        This function does not raise exceptions. Failed deletions
        are silently ignored. Add logging here if needed for debugging.
    """
    try:
        if path.exists():
            path.unlink()
    except Exception:
        # Silently ignore deletion failures
        # TODO: Add logging here for production debugging
        pass

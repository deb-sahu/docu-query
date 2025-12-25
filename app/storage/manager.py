"""
File Storage Management
"""

from fastapi import UploadFile, HTTPException
from pathlib import Path
import shutil
from uuid import uuid4
from app.core.config import UPLOAD_DIR

ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"]


def save_upload(file: UploadFile) -> tuple[str, Path]:
    """Save uploaded file and return (doc_id, file_path)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a filename")
    
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Supported formats: {', '.join(ALLOWED_EXTENSIONS)}")
    
    doc_id = str(uuid4())
    dest = UPLOAD_DIR / f"{doc_id}{ext}"
    
    try:
        with dest.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()
    
    return doc_id, dest


def delete_file(path: Path):
    """Delete a file if it exists."""
    try:
        if path and path.exists():
            path.unlink()
    except Exception:
        pass

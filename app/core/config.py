"""
Configuration Settings
======================

Central configuration for the DocuQuery application.

This module defines:
- Directory paths for file storage
- Text chunking parameters for document processing

Modify these values to tune the system's behavior for different use cases.
"""

from pathlib import Path

# Base directory is the project root (two levels up from this file)
BASE_DIR = Path(__file__).resolve().parents[2]

# Directory where uploaded files are stored
# Created automatically if it doesn't exist
UPLOAD_DIR = BASE_DIR / "uploads"

# Directory for storing document metadata as JSON files
# Created automatically if it doesn't exist
DATA_DIR = BASE_DIR / "data"

# Ensure directories exist on module import
UPLOAD_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)


# =============================================================================
# Text Chunking Configuration
# =============================================================================
# These parameters control how documents are split into searchable chunks.
# Adjust based on your use case:
#   - Smaller chunks = more precise retrieval, but may lose context
#   - Larger chunks = more context, but may include irrelevant text
#   - More overlap = better continuity, but increases storage/compute

# Maximum number of characters per text chunk
CHUNK_SIZE = 1200

# Number of overlapping characters between consecutive chunks.
# Overlap helps preserve context when relevant text spans chunk boundaries.
CHUNK_OVERLAP = 200

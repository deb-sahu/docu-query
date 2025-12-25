"""
Application Configuration
"""

from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Provider: "gemini" or "ollama" (for Llama)
    LLM_PROVIDER: Literal["gemini", "ollama"] = "gemini"
    
    # Gemini Configuration (free tier)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # Ollama Configuration (local Llama)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    
    # Embedding model (runs locally via sentence-transformers)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Text chunking settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # RAG settings
    TOP_K_RESULTS: int = 4
    
    class Config:
        env_file = ".env"
        extra = "ignore"


# Load settings
settings = Settings()

# Directory paths
BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = DATA_DIR / "chroma"

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)

"""
DocuQuery - Document Q&A System
================================

Main FastAPI application entry point.

This module initializes the FastAPI application, configures middleware,
and sets up routing for the document-based question answering system.

The application provides:
- REST API endpoints for document upload and querying
- CORS support for frontend integration
- Static file serving for production deployment
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.api import routes

# Initialize FastAPI application with metadata for OpenAPI documentation
app = FastAPI(
    title="DocuQuery - Document Q&A System",
    description="""
    A document-based Question Answering API that allows users to:
    - Upload documents (PDF, DOCX, TXT)
    - Process direct text input
    - Ask questions and receive answers with source references
    - View confidence scores for retrieved passages
    
    The system uses TF-IDF vectorization for similarity-based retrieval.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware to allow frontend applications to communicate with the API.
# In production, replace "*" with specific allowed origins for security.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the API router with /api prefix.
# All document and question-answering endpoints are defined in routes.py
app.include_router(routes.router, prefix="/api")

# Serve the built React frontend in production.
# If the frontend/dist folder exists (after running npm build),
# serve it as static files at the root path.
frontend_path = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        dict: Status object indicating the service is running.
    """
    return {"status": "healthy", "service": "DocuQuery Backend"}

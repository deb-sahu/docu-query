"""
DocuQuery - Document Q&A System with LLM-powered RAG
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.api import routes

app = FastAPI(
    title="DocuQuery",
    description="Document Q&A system using RAG with Gemini or Llama",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix="/api")

# Serve frontend in production
frontend_path = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


@app.get("/health")
async def health_check():
    from app.core.config import settings
    return {
        "status": "healthy",
        "llm_provider": settings.LLM_PROVIDER
    }

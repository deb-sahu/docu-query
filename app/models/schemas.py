"""
API Request/Response Schemas
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    chunks_count: int
    message: str = "Document uploaded successfully"


class TextInputRequest(BaseModel):
    text: str = Field(..., min_length=1)
    title: str = Field(default="Direct Text Input")


class TextInputResponse(BaseModel):
    doc_id: str
    title: str
    chunks_count: int
    message: str = "Text processed successfully"


class AnswerRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: Optional[int] = Field(default=4, ge=1, le=10)
    doc_ids: Optional[List[str]] = None


class SourceDocument(BaseModel):
    filename: str
    doc_id: str
    chunk_index: int
    score: float
    text: str


class AnswerResponse(BaseModel):
    answer: str
    query: str
    sources: List[SourceDocument]
    llm_provider: str


class DocumentMeta(BaseModel):
    doc_id: str
    filename: str
    chunks: int
    file_type: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentMeta]
    total_count: int


class ConfigResponse(BaseModel):
    llm_provider: str
    llm_model: str
    embedding_model: str

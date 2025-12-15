from typing import List, Optional
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    chunks_count: int
    message: str = "Document uploaded successfully"


class TextInputRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw text content to process")
    title: str = Field(default="Direct Text Input", description="Optional title for the text")


class TextInputResponse(BaseModel):
    doc_id: str
    title: str
    chunks_count: int
    message: str = "Text processed successfully"


class ExtractRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: Optional[int] = Field(5, ge=1, le=50)
    doc_ids: Optional[List[str]] = Field(None, description="Filter to specific documents")


class ExtractResult(BaseModel):
    doc_id: str
    chunk_id: int
    score: float
    text: str
    source: str
    highlight_start: Optional[int] = None
    highlight_end: Optional[int] = None


class ExtractResponse(BaseModel):
    results: List[ExtractResult]
    query: str


class AnswerRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: Optional[int] = Field(3, ge=1, le=10)
    doc_ids: Optional[List[str]] = Field(None, description="Filter to specific documents")


class AnswerSource(BaseModel):
    filename: str
    doc_id: str
    chunk_id: int
    score: float
    confidence: str  # "high", "medium", "low"
    text: str
    highlight_indices: Optional[List[dict]] = None  # [{start: int, end: int}]


class AnswerResponse(BaseModel):
    answer: str
    query: str
    sources: List[AnswerSource]
    confidence_score: float  # Overall confidence 0-1


class DocumentMeta(BaseModel):
    doc_id: str
    filename: str
    chunks: int
    file_type: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentMeta]
    total_count: int

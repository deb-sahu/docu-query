"""
Pydantic Schemas
================

Request and response models for the DocuQuery API.

These schemas provide:
- Input validation for API requests
- Response structure documentation
- Automatic OpenAPI schema generation

All models use Pydantic v2 for validation and serialization.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# =============================================================================
# Document Upload Schemas
# =============================================================================

class UploadResponse(BaseModel):
    """Response returned after successfully uploading a document."""
    
    doc_id: str = Field(description="Unique identifier for the uploaded document")
    filename: str = Field(description="Original filename of the uploaded document")
    chunks_count: int = Field(description="Number of text chunks created from the document")
    message: str = Field(
        default="Document uploaded successfully",
        description="Human-readable status message"
    )


# =============================================================================
# Text Input Schemas
# =============================================================================

class TextInputRequest(BaseModel):
    """Request body for direct text input (no file upload)."""
    
    text: str = Field(
        ...,  # Required field
        min_length=1,
        description="Raw text content to process and add to the knowledge base"
    )
    title: str = Field(
        default="Direct Text Input",
        description="Optional title to identify this text in the document list"
    )


class TextInputResponse(BaseModel):
    """Response returned after processing direct text input."""
    
    doc_id: str = Field(description="Unique identifier for this text document")
    title: str = Field(description="Title assigned to this text")
    chunks_count: int = Field(description="Number of text chunks created")
    message: str = Field(
        default="Text processed successfully",
        description="Human-readable status message"
    )


# =============================================================================
# Passage Extraction Schemas
# =============================================================================

class ExtractRequest(BaseModel):
    """Request body for extracting relevant passages from documents."""
    
    query: str = Field(
        ...,  # Required field
        min_length=1,
        description="The search query to find relevant passages"
    )
    top_k: Optional[int] = Field(
        default=5,
        ge=1,  # Minimum 1
        le=50,  # Maximum 50
        description="Number of top matching passages to return"
    )
    doc_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional list of document IDs to search. If empty, searches all documents."
    )


class ExtractResult(BaseModel):
    """A single extracted passage result."""
    
    doc_id: str = Field(description="ID of the document containing this passage")
    chunk_id: int = Field(description="Index of this chunk within the document")
    score: float = Field(description="Similarity score (0-1, higher is more relevant)")
    text: str = Field(description="The extracted passage text")
    source: str = Field(description="Filename or title of the source document")
    highlight_start: Optional[int] = Field(
        default=None,
        description="Start position of matching text for highlighting"
    )
    highlight_end: Optional[int] = Field(
        default=None,
        description="End position of matching text for highlighting"
    )


class ExtractResponse(BaseModel):
    """Response containing extracted passages for a query."""
    
    results: List[ExtractResult] = Field(description="List of matching passages")
    query: str = Field(description="The original query that was searched")


# =============================================================================
# Question Answering Schemas
# =============================================================================

class AnswerRequest(BaseModel):
    """Request body for asking a question about uploaded documents."""
    
    query: str = Field(
        ...,  # Required field
        min_length=1,
        description="The question to answer based on document content"
    )
    top_k: Optional[int] = Field(
        default=3,
        ge=1,  # Minimum 1
        le=10,  # Maximum 10
        description="Number of source passages to include in the answer"
    )
    doc_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional list of document IDs to search. If empty, searches all documents."
    )


class AnswerSource(BaseModel):
    """A source passage that contributed to the answer."""
    
    filename: str = Field(description="Name of the source file")
    doc_id: str = Field(description="Unique ID of the source document")
    chunk_id: int = Field(description="Index of this chunk within the document")
    score: float = Field(description="Relevance score (0-1)")
    confidence: str = Field(description="Confidence level: 'high', 'medium', or 'low'")
    text: str = Field(description="The source passage text")
    highlight_indices: Optional[List[dict]] = Field(
        default=None,
        description="List of {start, end} positions for highlighting query terms"
    )


class AnswerResponse(BaseModel):
    """Response containing the answer and its sources."""
    
    answer: str = Field(description="The answer text composed from relevant passages")
    query: str = Field(description="The original question that was asked")
    sources: List[AnswerSource] = Field(description="Source passages used to compose the answer")
    confidence_score: float = Field(description="Overall confidence score (0-1)")


# =============================================================================
# Document Management Schemas
# =============================================================================

class DocumentMeta(BaseModel):
    """Metadata about a single document in the knowledge base."""
    
    doc_id: str = Field(description="Unique document identifier")
    filename: str = Field(description="Original filename or title")
    chunks: int = Field(description="Number of searchable text chunks")
    file_type: str = Field(description="File type: PDF, DOCX, TXT, or TEXT")


class DocumentListResponse(BaseModel):
    """Response containing list of all documents in the knowledge base."""
    
    documents: List[DocumentMeta] = Field(description="List of document metadata")
    total_count: int = Field(description="Total number of documents")

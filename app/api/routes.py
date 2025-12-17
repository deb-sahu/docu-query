"""
API Routes
==========

REST API endpoints for the DocuQuery document Q&A system.

Endpoints:
-----------
POST /api/upload       - Upload a document (PDF, DOCX, TXT)
POST /api/text-input   - Process direct text input
POST /api/answer       - Ask a question and get answers with sources
POST /api/extract      - Extract relevant passages for a query
GET  /api/documents    - List all uploaded documents
DELETE /api/documents/{doc_id} - Delete a specific document
DELETE /api/documents  - Clear all documents

The system maintains an in-memory document store where each document
is parsed into chunks and indexed using TF-IDF for similarity search.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from pathlib import Path
import json
import re
from uuid import uuid4
from app.storage.manager import save_upload, delete_file
from app.services import parser, vector_store
from app.models.schemas import (
    UploadResponse, ExtractRequest, ExtractResponse, ExtractResult,
    AnswerRequest, AnswerResponse, AnswerSource, DocumentMeta,
    TextInputRequest, TextInputResponse, DocumentListResponse
)
from app.core.config import DATA_DIR

router = APIRouter()

# =============================================================================
# In-Memory Document Store
# =============================================================================
# Structure: doc_store[doc_id] = {
#     "filename": str,           - Original filename or title
#     "filepath": Path|None,     - Path to uploaded file (None for text input)
#     "chunks": List[str],       - List of text chunks
#     "store": SimpleTfidfStore, - TF-IDF index for similarity search
#     "file_type": str           - File type (PDF, DOCX, TXT, TEXT)
# }
_doc_store = {}


# =============================================================================
# Helper Functions
# =============================================================================

def get_confidence_label(score: float) -> str:
    """
    Convert a numeric similarity score to a human-readable confidence label.
    
    Thresholds are tuned for TF-IDF cosine similarity scores:
    - High (>=0.5): Strong keyword overlap with query
    - Medium (>=0.2): Moderate relevance
    - Low (<0.2): Weak match, may not be relevant
    
    Args:
        score: Cosine similarity score between 0 and 1.
        
    Returns:
        Confidence label: "high", "medium", or "low".
    """
    if score >= 0.5:
        return "high"
    elif score >= 0.2:
        return "medium"
    else:
        return "low"


def find_query_highlights(text: str, query: str) -> list:
    """
    Find positions where query terms appear in the text for highlighting.
    
    Searches for each query term (case-insensitive) and returns their
    positions. Overlapping matches are merged into single ranges.
    
    Args:
        text: The text to search in.
        query: The user's query string.
        
    Returns:
        List of dicts with "start" and "end" keys indicating positions.
        Returns empty list if no matches found.
        
    Example:
        >>> find_query_highlights("Python is great", "python")
        [{"start": 0, "end": 6}]
    """
    highlights = []
    query_terms = query.lower().split()
    text_lower = text.lower()
    
    for term in query_terms:
        # Skip very short terms (articles, prepositions, etc.)
        if len(term) < 3:
            continue
            
        # Find all occurrences of this term
        for match in re.finditer(re.escape(term), text_lower):
            highlights.append({"start": match.start(), "end": match.end()})
    
    # Sort by position for merging
    highlights.sort(key=lambda x: x["start"])
    
    # Merge overlapping ranges
    merged = []
    for h in highlights:
        if merged and h["start"] <= merged[-1]["end"]:
            # Extend previous range if overlapping
            merged[-1]["end"] = max(merged[-1]["end"], h["end"])
        else:
            merged.append(h)
    
    return merged


# =============================================================================
# Document Upload Endpoints
# =============================================================================

@router.post("/upload", response_model=UploadResponse, tags=["Documents"])
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a document to the knowledge base.
    
    Accepts PDF, DOCX, or TXT files. The document is:
    1. Saved to the uploads directory
    2. Text is extracted based on file type
    3. Text is split into overlapping chunks
    4. Chunks are indexed using TF-IDF for similarity search
    
    Args:
        file: The document file to upload.
        
    Returns:
        UploadResponse with document ID and chunk count.
        
    Raises:
        HTTPException 400: If file is empty, unreadable, or unsupported type.
        HTTPException 500: If processing fails unexpectedly.
    """
    try:
        # Save file and get unique document ID
        doc_id, dest = save_upload(file)
        ext = dest.suffix.lower()
        
        # Extract text based on file type
        if ext == ".pdf":
            raw = parser.extract_text_from_pdf(dest)
        elif ext == ".docx":
            raw = parser.extract_text_from_docx(dest)
        else:
            raw = parser.extract_text_from_txt(dest)

        # Validate extracted content
        if not raw.strip():
            delete_file(dest)
            raise HTTPException(
                status_code=400, 
                detail="Document appears to be empty or unreadable"
            )

        # Split into chunks and create search index
        chunks = parser.chunk_text(raw)
        store = vector_store.SimpleTfidfStore(chunks)

        # Store in memory
        file_type = ext.replace(".", "").upper()
        _doc_store[doc_id] = {
            "filename": file.filename,
            "filepath": dest,
            "chunks": chunks,
            "store": store,
            "file_type": file_type
        }

        # Persist metadata to disk for potential recovery
        meta = {
            "doc_id": doc_id, 
            "filename": file.filename, 
            "chunks_count": len(chunks), 
            "file_type": file_type
        }
        meta_path = DATA_DIR / f"{doc_id}.json"
        meta_path.write_text(json.dumps(meta))

        return UploadResponse(
            doc_id=doc_id,
            filename=file.filename,
            chunks_count=len(chunks),
            message=f"Successfully processed {file.filename} into {len(chunks)} searchable chunks"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text-input", response_model=TextInputResponse, tags=["Documents"])
async def process_text_input(req: TextInputRequest = Body(...)):
    """
    Process direct text input for ad-hoc queries.
    
    Allows users to paste text directly without uploading a file.
    The text is chunked and indexed the same way as uploaded documents.
    
    Args:
        req: TextInputRequest with text content and optional title.
        
    Returns:
        TextInputResponse with document ID and chunk count.
        
    Raises:
        HTTPException 400: If text is empty or too short to process.
        HTTPException 500: If processing fails unexpectedly.
    """
    try:
        if not req.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        # Generate document ID and chunk the text
        doc_id = str(uuid4())
        chunks = parser.chunk_text(req.text)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="Text too short to process")

        # Create search index
        store = vector_store.SimpleTfidfStore(chunks)

        # Store in memory (no filepath since it's direct input)
        _doc_store[doc_id] = {
            "filename": req.title,
            "filepath": None,
            "chunks": chunks,
            "store": store,
            "file_type": "TEXT"
        }

        # Persist metadata
        meta = {
            "doc_id": doc_id, 
            "filename": req.title, 
            "chunks_count": len(chunks), 
            "file_type": "TEXT"
        }
        meta_path = DATA_DIR / f"{doc_id}.json"
        meta_path.write_text(json.dumps(meta))

        return TextInputResponse(
            doc_id=doc_id,
            title=req.title,
            chunks_count=len(chunks),
            message=f"Text processed into {len(chunks)} searchable chunks"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Query Endpoints
# =============================================================================

@router.post("/extract", response_model=ExtractResponse, tags=["Query"])
async def extract(req: ExtractRequest = Body(...)):
    """
    Extract relevant text passages for a query.
    
    Searches all (or specified) documents and returns the top-k
    most relevant passages based on TF-IDF similarity.
    
    Args:
        req: ExtractRequest with query, top_k, and optional doc_ids filter.
        
    Returns:
        ExtractResponse with list of matching passages and scores.
        
    Raises:
        HTTPException 404: If no documents are available or specified docs not found.
        HTTPException 400: If query is empty.
    """
    if not _doc_store:
        raise HTTPException(
            status_code=404, 
            detail="No documents available. Upload documents first."
        )

    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Filter to specific documents if requested
    docs_to_search = _doc_store
    if req.doc_ids:
        docs_to_search = {k: v for k, v in _doc_store.items() if k in req.doc_ids}
        if not docs_to_search:
            raise HTTPException(status_code=404, detail="Specified documents not found")

    # Collect top matches from each document
    aggregated = []
    for doc_id, doc in docs_to_search.items():
        store = doc.get("store")
        if not store:
            continue
            
        results = store.top_k(req.query, k=req.top_k)
        for r in results:
            highlights = find_query_highlights(r["text"], req.query)
            aggregated.append({
                "doc_id": doc_id,
                "chunk_id": r["chunk_id"],
                "score": r["score"],
                "text": r["text"],
                "source": doc["filename"],
                "highlight_start": highlights[0]["start"] if highlights else None,
                "highlight_end": highlights[0]["end"] if highlights else None
            })

    # Sort by score across all documents and return top_k overall
    aggregated.sort(key=lambda x: x["score"], reverse=True)
    topk = aggregated[:req.top_k]

    return ExtractResponse(
        results=[ExtractResult(**r) for r in topk], 
        query=req.query
    )


@router.post("/answer", response_model=AnswerResponse, tags=["Query"])
async def answer(req: AnswerRequest = Body(...)):
    """
    Answer a question based on uploaded documents.
    
    This is the main Q&A endpoint. It:
    1. Searches all documents for relevant passages using TF-IDF
    2. Aggregates and ranks results across all documents
    3. Composes an answer from the top passages
    4. Returns sources with confidence scores and highlighting
    
    Args:
        req: AnswerRequest with query, top_k, and optional doc_ids filter.
        
    Returns:
        AnswerResponse with composed answer, sources, and confidence score.
        
    Raises:
        HTTPException 404: If no documents are available.
        HTTPException 400: If query is empty.
    """
    if not _doc_store:
        raise HTTPException(
            status_code=404, 
            detail="No documents available. Upload documents first."
        )

    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Filter to specific documents if requested
    docs_to_search = _doc_store
    if req.doc_ids:
        docs_to_search = {k: v for k, v in _doc_store.items() if k in req.doc_ids}
        if not docs_to_search:
            raise HTTPException(status_code=404, detail="Specified documents not found")

    # Collect top matches from each document
    # Request 2x top_k to have better selection after cross-document ranking
    aggregated = []
    for doc_id, doc in docs_to_search.items():
        store = doc.get("store")
        if not store:
            continue
            
        results = store.top_k(req.query, k=req.top_k * 2)
        for r in results:
            aggregated.append({
                "doc_id": doc_id,
                "chunk_id": r["chunk_id"],
                "score": r["score"],
                "text": r["text"],
                "filename": doc["filename"]
            })

    # Handle case where no relevant passages found
    if not aggregated:
        return AnswerResponse(
            answer="No relevant passages found in the uploaded documents.",
            query=req.query,
            sources=[],
            confidence_score=0.0
        )

    # Sort by score and take overall top_k
    aggregated.sort(key=lambda x: x["score"], reverse=True)
    topk = aggregated[:req.top_k]

    # Calculate overall confidence score
    # Uses weighted average of max and mean scores
    max_score = topk[0]["score"]
    avg_score = sum(item["score"] for item in topk) / len(topk)
    overall_confidence = min(1.0, (max_score + avg_score) / 2 * 2)

    # Compose answer from top passages
    top_texts = [item["text"].strip() for item in topk if item.get("score", 0) > 0]
    if not top_texts:
        answer_text = "No relevant passages found in the uploaded documents."
    else:
        # Join passages with clear separation
        answer_text = "\n\n".join(top_texts)
        # Truncate if too long (prevents huge responses)
        if len(answer_text) > 4000:
            answer_text = answer_text[:4000].rsplit(" ", 1)[0] + "..."

    # Build sources list with highlighting information
    sources = []
    for item in topk:
        highlights = find_query_highlights(item["text"], req.query)
        sources.append(AnswerSource(
            filename=item["filename"],
            doc_id=item["doc_id"],
            chunk_id=item["chunk_id"],
            score=round(item["score"], 4),
            confidence=get_confidence_label(item["score"]),
            text=item["text"],
            highlight_indices=highlights if highlights else None
        ))

    return AnswerResponse(
        answer=answer_text,
        query=req.query,
        sources=sources,
        confidence_score=round(overall_confidence, 4)
    )


# =============================================================================
# Document Management Endpoints
# =============================================================================

@router.get("/documents", response_model=DocumentListResponse, tags=["Documents"])
async def list_documents():
    """
    List all documents in the knowledge base.
    
    Returns metadata for all uploaded documents and text inputs,
    including document ID, filename, chunk count, and file type.
    
    Returns:
        DocumentListResponse with list of documents and total count.
    """
    items = []
    for doc_id, doc in _doc_store.items():
        items.append(DocumentMeta(
            doc_id=doc_id,
            filename=doc["filename"],
            chunks=len(doc.get("chunks", [])),
            file_type=doc.get("file_type", "UNKNOWN")
        ))
    return DocumentListResponse(documents=items, total_count=len(items))


@router.delete("/documents/{doc_id}", tags=["Documents"])
async def delete_document(doc_id: str):
    """
    Delete a specific document from the knowledge base.
    
    Removes the document from memory, deletes the uploaded file
    (if applicable), and removes the metadata file.
    
    Args:
        doc_id: The unique identifier of the document to delete.
        
    Returns:
        Confirmation message with the deleted document ID.
        
    Raises:
        HTTPException 404: If document not found.
    """
    doc = _doc_store.pop(doc_id, None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete the uploaded file if it exists
    filepath = doc.get("filepath")
    if filepath:
        delete_file(filepath)
    
    # Delete metadata file
    meta = DATA_DIR / f"{doc_id}.json"
    if meta.exists():
        meta.unlink()
    
    return {"detail": "Document deleted successfully", "doc_id": doc_id}


@router.delete("/documents", tags=["Documents"])
async def clear_all_documents():
    """
    Clear all documents from the knowledge base.
    
    Removes all documents from memory, deletes all uploaded files,
    and removes all metadata files. Use with caution.
    
    Returns:
        Confirmation message with count of deleted documents.
    """
    count = len(_doc_store)
    
    # Delete each document's file and metadata
    for doc_id, doc in list(_doc_store.items()):
        filepath = doc.get("filepath")
        if filepath:
            delete_file(filepath)
            
        meta = DATA_DIR / f"{doc_id}.json"
        if meta.exists():
            meta.unlink()
    
    # Clear the in-memory store
    _doc_store.clear()
    
    return {"detail": f"Cleared {count} documents from knowledge base"}

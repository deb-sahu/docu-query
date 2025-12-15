from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi import Body
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

# In-memory documents store
# doc_store[doc_id] = {"filename": str, "filepath": Path|None, "chunks": List[str], "store": SimpleTfidfStore, "file_type": str}
_doc_store = {}


def get_confidence_label(score: float) -> str:
    """Convert numeric score to confidence label"""
    if score >= 0.5:
        return "high"
    elif score >= 0.2:
        return "medium"
    else:
        return "low"


def find_query_highlights(text: str, query: str) -> list:
    """Find positions where query terms appear in text"""
    highlights = []
    query_terms = query.lower().split()
    text_lower = text.lower()
    
    for term in query_terms:
        if len(term) < 3:  # Skip very short terms
            continue
        for match in re.finditer(re.escape(term), text_lower):
            highlights.append({"start": match.start(), "end": match.end()})
    
    # Sort by position and merge overlapping
    highlights.sort(key=lambda x: x["start"])
    merged = []
    for h in highlights:
        if merged and h["start"] <= merged[-1]["end"]:
            merged[-1]["end"] = max(merged[-1]["end"], h["end"])
        else:
            merged.append(h)
    
    return merged


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a document (PDF, DOCX, or TXT) to the knowledge base"""
    try:
        doc_id, dest = save_upload(file)
        ext = dest.suffix.lower()
        
        if ext == ".pdf":
            raw = parser.extract_text_from_pdf(dest)
        elif ext == ".docx":
            raw = parser.extract_text_from_docx(dest)
        else:
            raw = parser.extract_text_from_txt(dest)

        if not raw.strip():
            delete_file(dest)
            raise HTTPException(status_code=400, detail="Document appears to be empty or unreadable")

        chunks = parser.chunk_text(raw)
        store = vector_store.SimpleTfidfStore(chunks)

        file_type = ext.replace(".", "").upper()
        _doc_store[doc_id] = {
            "filename": file.filename,
            "filepath": dest,
            "chunks": chunks,
            "store": store,
            "file_type": file_type
        }

        # Persist metadata
        meta = {"doc_id": doc_id, "filename": file.filename, "chunks_count": len(chunks), "file_type": file_type}
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


@router.post("/text-input", response_model=TextInputResponse)
async def process_text_input(req: TextInputRequest = Body(...)):
    """Process direct text input for ad-hoc queries"""
    try:
        if not req.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        doc_id = str(uuid4())
        chunks = parser.chunk_text(req.text)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="Text too short to process")

        store = vector_store.SimpleTfidfStore(chunks)

        _doc_store[doc_id] = {
            "filename": req.title,
            "filepath": None,
            "chunks": chunks,
            "store": store,
            "file_type": "TEXT"
        }

        # Persist metadata
        meta = {"doc_id": doc_id, "filename": req.title, "chunks_count": len(chunks), "file_type": "TEXT"}
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


@router.post("/extract", response_model=ExtractResponse)
async def extract(req: ExtractRequest = Body(...)):
    """Extract relevant text passages for a query"""
    if not _doc_store:
        raise HTTPException(status_code=404, detail="No documents available. Upload documents first.")

    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Filter documents if doc_ids specified
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

    # Sort across all docs and return top_k overall
    aggregated.sort(key=lambda x: x["score"], reverse=True)
    topk = aggregated[:req.top_k]

    out = [ExtractResult(**r) for r in topk]
    return ExtractResponse(results=out, query=req.query)


@router.post("/answer", response_model=AnswerResponse)
async def answer(req: AnswerRequest = Body(...)):
    """Get answers to a question based on uploaded documents"""
    if not _doc_store:
        raise HTTPException(status_code=404, detail="No documents available. Upload documents first.")

    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Filter documents if doc_ids specified
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
        results = store.top_k(req.query, k=req.top_k * 2)  # Get more for better selection
        for r in results:
            aggregated.append({
                "doc_id": doc_id,
                "chunk_id": r["chunk_id"],
                "score": r["score"],
                "text": r["text"],
                "filename": doc["filename"]
            })

    # If nothing found
    if not aggregated:
        return AnswerResponse(
            answer="No relevant passages found in the uploaded documents.",
            query=req.query,
            sources=[],
            confidence_score=0.0
        )

    # Sort across all docs and take overall top_k
    aggregated.sort(key=lambda x: x["score"], reverse=True)
    topk = aggregated[:req.top_k]

    # Calculate overall confidence
    if topk:
        max_score = topk[0]["score"]
        avg_score = sum(item["score"] for item in topk) / len(topk)
        overall_confidence = min(1.0, (max_score + avg_score) / 2 * 2)  # Normalize
    else:
        overall_confidence = 0.0

    # Build concise answer from top passages
    top_texts = [item["text"].strip() for item in topk if item.get("score", 0) > 0]
    if not top_texts:
        answer_text = "No relevant passages found in the uploaded documents."
    else:
        # Join with clear separation
        answer_text = "\n\n".join(top_texts)
        if len(answer_text) > 4000:
            answer_text = answer_text[:4000].rsplit(" ", 1)[0] + "..."

    # Build sources list with highlights
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


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded documents"""
    items = []
    for k, v in _doc_store.items():
        items.append(DocumentMeta(
            doc_id=k,
            filename=v["filename"],
            chunks=len(v.get("chunks", [])),
            file_type=v.get("file_type", "UNKNOWN")
        ))
    return DocumentListResponse(documents=items, total_count=len(items))


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document from the knowledge base"""
    doc = _doc_store.pop(doc_id, None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    filepath = doc.get("filepath")
    if filepath:
        delete_file(filepath)
    
    meta = DATA_DIR / f"{doc_id}.json"
    if meta.exists():
        meta.unlink()
    
    return {"detail": "Document deleted successfully", "doc_id": doc_id}


@router.delete("/documents")
async def clear_all_documents():
    """Clear all documents from the knowledge base"""
    count = len(_doc_store)
    for doc_id, doc in list(_doc_store.items()):
        filepath = doc.get("filepath")
        if filepath:
            delete_file(filepath)
        meta = DATA_DIR / f"{doc_id}.json"
        if meta.exists():
            meta.unlink()
    _doc_store.clear()
    return {"detail": f"Cleared {count} documents from knowledge base"}

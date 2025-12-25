"""
API Routes for Document Q&A System
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Body
import json
from uuid import uuid4
from app.storage.manager import save_upload, delete_file
from app.services.parser import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from app.services.vector_store import document_store
from app.services.llm_service import create_qa_chain, format_context
from app.models.schemas import (
    UploadResponse, AnswerRequest, AnswerResponse, SourceDocument,
    TextInputRequest, TextInputResponse, DocumentListResponse,
    DocumentMeta, ConfigResponse
)
from app.core.config import settings, DATA_DIR

router = APIRouter()

# In-memory document metadata
_doc_meta = {}


@router.get("/config", response_model=ConfigResponse)
async def get_config():
    """Get current LLM configuration."""
    model = settings.GEMINI_MODEL if settings.LLM_PROVIDER == "gemini" else settings.OLLAMA_MODEL
    return ConfigResponse(
        llm_provider=settings.LLM_PROVIDER,
        llm_model=model,
        embedding_model=settings.EMBEDDING_MODEL
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a document (PDF, DOCX, TXT) to the knowledge base."""
    try:
        doc_id, dest = save_upload(file)
        ext = dest.suffix.lower()
        
        # Extract text based on file type
        if ext == ".pdf":
            text = extract_text_from_pdf(dest)
        elif ext == ".docx":
            text = extract_text_from_docx(dest)
        else:
            text = extract_text_from_txt(dest)

        if not text.strip():
            delete_file(dest)
            raise HTTPException(status_code=400, detail="Document is empty or unreadable")

        # Add to vector store
        chunks_count = document_store.add_document(doc_id, file.filename, text)

        # Store metadata
        file_type = ext.replace(".", "").upper()
        _doc_meta[doc_id] = {
            "filename": file.filename,
            "filepath": dest,
            "chunks": chunks_count,
            "file_type": file_type
        }

        # Persist metadata
        meta_path = DATA_DIR / f"{doc_id}.json"
        meta_path.write_text(json.dumps({
            "doc_id": doc_id,
            "filename": file.filename,
            "chunks_count": chunks_count,
            "file_type": file_type
        }))

        return UploadResponse(
            doc_id=doc_id,
            filename=file.filename,
            chunks_count=chunks_count,
            message=f"Processed {file.filename} into {chunks_count} chunks"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text-input", response_model=TextInputResponse)
async def process_text_input(req: TextInputRequest = Body(...)):
    """Process direct text input."""
    try:
        if not req.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        doc_id = str(uuid4())
        chunks_count = document_store.add_document(doc_id, req.title, req.text)
        
        if chunks_count == 0:
            raise HTTPException(status_code=400, detail="Text too short to process")

        _doc_meta[doc_id] = {
            "filename": req.title,
            "filepath": None,
            "chunks": chunks_count,
            "file_type": "TEXT"
        }

        meta_path = DATA_DIR / f"{doc_id}.json"
        meta_path.write_text(json.dumps({
            "doc_id": doc_id,
            "filename": req.title,
            "chunks_count": chunks_count,
            "file_type": "TEXT"
        }))

        return TextInputResponse(
            doc_id=doc_id,
            title=req.title,
            chunks_count=chunks_count,
            message=f"Processed into {chunks_count} chunks"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer", response_model=AnswerResponse)
async def answer_question(req: AnswerRequest = Body(...)):
    """Answer a question using RAG with the configured LLM."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Search for relevant documents
    doc_ids = req.doc_ids if req.doc_ids else None
    documents = document_store.search(req.query, top_k=req.top_k, doc_ids=doc_ids)
    
    if not documents:
        return AnswerResponse(
            answer="No relevant information found in the uploaded documents.",
            query=req.query,
            sources=[],
            llm_provider=settings.LLM_PROVIDER
        )

    # Format context and generate answer
    context = format_context(documents)
    
    try:
        qa_chain = create_qa_chain()
        answer = qa_chain.invoke({"context": context, "question": req.query})
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"LLM error ({settings.LLM_PROVIDER}): {str(e)}"
        )

    # Build source list
    sources = [
        SourceDocument(
            filename=doc.metadata.get("source", "Unknown"),
            doc_id=doc.metadata.get("doc_id", ""),
            chunk_index=doc.metadata.get("chunk_index", 0),
            score=round(doc.metadata.get("score", 0), 4),
            text=doc.page_content
        )
        for doc in documents
    ]

    return AnswerResponse(
        answer=answer,
        query=req.query,
        sources=sources,
        llm_provider=settings.LLM_PROVIDER
    )


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded documents."""
    items = [
        DocumentMeta(
            doc_id=doc_id,
            filename=meta["filename"],
            chunks=meta["chunks"],
            file_type=meta["file_type"]
        )
        for doc_id, meta in _doc_meta.items()
    ]
    return DocumentListResponse(documents=items, total_count=len(items))


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document from the knowledge base."""
    meta = _doc_meta.pop(doc_id, None)
    if not meta:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete from vector store
    document_store.delete_document(doc_id)
    
    # Delete file if exists
    if meta.get("filepath"):
        delete_file(meta["filepath"])
    
    # Delete metadata file
    meta_path = DATA_DIR / f"{doc_id}.json"
    if meta_path.exists():
        meta_path.unlink()
    
    return {"message": "Document deleted", "doc_id": doc_id}


@router.delete("/documents")
async def clear_all_documents():
    """Clear all documents from the knowledge base."""
    count = len(_doc_meta)
    
    # Delete all files
    for doc_id, meta in list(_doc_meta.items()):
        if meta.get("filepath"):
            delete_file(meta["filepath"])
        meta_path = DATA_DIR / f"{doc_id}.json"
        if meta_path.exists():
            meta_path.unlink()
    
    # Clear vector store and metadata
    document_store.clear_all()
    _doc_meta.clear()
    
    return {"message": f"Cleared {count} documents"}

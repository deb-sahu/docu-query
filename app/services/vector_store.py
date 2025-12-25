"""
Vector Store - ChromaDB with Sentence Transformer Embeddings
"""

from typing import List, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings, CHROMA_DIR


# Initialize embedding model (runs locally)
_embeddings = None

def get_embeddings():
    """Get or initialize the embedding model."""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
    return _embeddings


# Text splitter for chunking documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""]
)


class DocumentStore:
    """Manages document storage and retrieval using ChromaDB."""
    
    def __init__(self):
        self.embeddings = get_embeddings()
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self._vectorstore = None
    
    @property
    def vectorstore(self) -> Optional[Chroma]:
        """Get or create the vector store."""
        if self._vectorstore is None:
            self._vectorstore = Chroma(
                client=self.client,
                collection_name="documents",
                embedding_function=self.embeddings
            )
        return self._vectorstore
    
    def add_document(self, doc_id: str, filename: str, text: str) -> int:
        """
        Add a document to the vector store.
        
        Returns the number of chunks created.
        """
        # Split text into chunks
        chunks = text_splitter.split_text(text)
        
        if not chunks:
            return 0
        
        # Create LangChain documents with metadata
        documents = [
            Document(
                page_content=chunk,
                metadata={
                    "doc_id": doc_id,
                    "source": filename,
                    "chunk_index": i
                }
            )
            for i, chunk in enumerate(chunks)
        ]
        
        # Add to vector store
        self.vectorstore.add_documents(documents)
        
        return len(chunks)
    
    def search(self, query: str, top_k: int = None, doc_ids: List[str] = None) -> List[Document]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            top_k: Number of results (default from settings)
            doc_ids: Optional filter to specific documents
        """
        k = top_k or settings.TOP_K_RESULTS
        
        # Build filter if doc_ids specified
        where_filter = None
        if doc_ids:
            where_filter = {"doc_id": {"$in": doc_ids}}
        
        results = self.vectorstore.similarity_search_with_relevance_scores(
            query, k=k, filter=where_filter
        )
        
        # Add score to metadata
        documents = []
        for doc, score in results:
            doc.metadata["score"] = score
            documents.append(doc)
        
        return documents
    
    def delete_document(self, doc_id: str):
        """Delete all chunks for a document."""
        try:
            collection = self.client.get_collection("documents")
            # Get IDs of chunks belonging to this document
            results = collection.get(where={"doc_id": doc_id})
            if results["ids"]:
                collection.delete(ids=results["ids"])
        except Exception:
            pass
    
    def clear_all(self):
        """Delete all documents from the store."""
        try:
            self.client.delete_collection("documents")
            self._vectorstore = None
        except Exception:
            pass
    
    def get_document_count(self) -> int:
        """Get total number of chunks in the store."""
        try:
            collection = self.client.get_collection("documents")
            return collection.count()
        except Exception:
            return 0


# Singleton instance
document_store = DocumentStore()

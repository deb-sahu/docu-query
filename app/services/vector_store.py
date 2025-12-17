"""
Vector Store - TF-IDF Based Similarity Search
==============================================

This module provides a simple but effective text similarity search
using TF-IDF (Term Frequency-Inverse Document Frequency) vectorization.

How TF-IDF works:
-----------------
1. Term Frequency (TF): How often a word appears in a document
2. Inverse Document Frequency (IDF): How rare a word is across all documents
3. TF-IDF score = TF × IDF (important words that appear frequently in a 
   specific document but rarely elsewhere get higher scores)

Limitations:
------------
- Keyword-based matching (no semantic understanding)
- Cannot match synonyms ("car" won't match "automobile")
- No understanding of word order or context

For better semantic search, consider upgrading to:
- Sentence Transformers (e.g., all-MiniLM-L6-v2)
- OpenAI embeddings with vector databases like FAISS or ChromaDB
"""

from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


class SimpleTfidfStore:
    """
    A simple in-memory vector store using TF-IDF for text similarity.
    
    This class takes a list of text chunks, creates TF-IDF vectors for each,
    and provides a method to find the most similar chunks to a query.
    
    Attributes:
        chunks: List of text strings that form the searchable corpus.
        vectorizer: Fitted TF-IDF vectorizer for transforming text.
        tfidf_matrix: Sparse matrix of TF-IDF vectors for all chunks.
        
    Example:
        >>> store = SimpleTfidfStore(["Python is great", "Java is verbose"])
        >>> results = store.top_k("programming language", k=1)
        >>> print(results[0]["text"])
    """
    
    def __init__(self, chunks: List[str]):
        """
        Initialize the store with text chunks.
        
        Args:
            chunks: List of text strings to index. Each chunk becomes
                   a searchable document in the corpus.
        """
        self.chunks = chunks or []
        self.vectorizer = None
        self.tfidf_matrix = None
        
        if self.chunks:
            # Configure TF-IDF vectorizer:
            # - stop_words="english": Ignore common words (the, is, at, etc.)
            # - max_df=0.9: Ignore terms that appear in >90% of documents
            self.vectorizer = TfidfVectorizer(
                stop_words="english",
                max_df=0.9
            )
            
            # Fit the vectorizer and transform chunks into TF-IDF vectors
            self.tfidf_matrix = self.vectorizer.fit_transform(self.chunks)

    def top_k(self, query: str, k: int = 5) -> List[dict]:
        """
        Find the k most similar chunks to the query.
        
        Uses cosine similarity between the query's TF-IDF vector and
        all chunk vectors. Results are sorted by similarity score.
        
        Args:
            query: The search query string.
            k: Number of top results to return (default: 5).
            
        Returns:
            List of dicts, each containing:
            - chunk_id (int): Index of the chunk in the original list
            - score (float): Cosine similarity score (0 to 1)
            - text (str): The chunk's text content
            
            Returns empty list if no chunks are indexed.
            
        Example:
            >>> results = store.top_k("What is machine learning?", k=3)
            >>> for r in results:
            ...     print(f"Score: {r['score']:.2f} - {r['text'][:50]}...")
        """
        # Handle empty corpus
        if self.tfidf_matrix is None or self.tfidf_matrix.shape[0] == 0:
            return []
        
        # Transform query using the same vectorizer (must be fitted first)
        query_vector = self.vectorizer.transform([query])
        
        # Compute cosine similarity between query and all chunks
        # linear_kernel is equivalent to cosine_similarity for normalized vectors
        similarities = linear_kernel(query_vector, self.tfidf_matrix).flatten()
        
        # Get indices of top k results (sorted by similarity, descending)
        top_indices = similarities.argsort()[::-1][:k]
        
        # Build result list with chunk ID, score, and text
        results = []
        for idx in top_indices:
            results.append({
                "chunk_id": int(idx),
                "score": float(similarities[idx]),
                "text": self.chunks[idx]
            })
        
        return results

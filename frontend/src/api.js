/**
 * API Client for DocuQuery
 * ========================
 * 
 * This module provides a clean interface to communicate with the
 * FastAPI backend. All API calls are centralized here for consistency
 * and easier maintenance.
 * 
 * The base URL is set to '/api' which is proxied to the backend
 * server (localhost:8000) by Vite during development.
 * 
 * All methods are async and return parsed JSON responses.
 * Errors are thrown with the detail message from the backend.
 */

const API_BASE = '/api';

/**
 * Helper function to handle API responses.
 * Throws an error with the backend's error message if request fails.
 * 
 * @param {Response} response - Fetch API response object
 * @param {string} fallbackMessage - Error message if no detail provided
 * @returns {Promise<Object>} Parsed JSON response
 * @throws {Error} If response is not ok
 */
async function handleResponse(response, fallbackMessage) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || fallbackMessage);
  }
  return response.json();
}

export const api = {
  /**
   * Upload a document file to the knowledge base.
   * 
   * Supported formats: PDF, DOCX, TXT
   * 
   * @param {File} file - The file object to upload
   * @returns {Promise<Object>} Upload response with doc_id and chunks_count
   * @throws {Error} If upload fails or file type is unsupported
   * 
   * @example
   * const result = await api.uploadFile(selectedFile);
   * console.log(`Uploaded: ${result.filename}, Chunks: ${result.chunks_count}`);
   */
  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    });
    
    return handleResponse(response, 'Upload failed');
  },

  /**
   * Process direct text input without file upload.
   * 
   * Useful for pasting text content directly into the knowledge base.
   * 
   * @param {string} text - The text content to process
   * @param {string} [title='Direct Text Input'] - Optional title for the text
   * @returns {Promise<Object>} Response with doc_id and chunks_count
   * @throws {Error} If text is empty or processing fails
   * 
   * @example
   * const result = await api.processText('Long article content...', 'My Article');
   * console.log(`Processed into ${result.chunks_count} chunks`);
   */
  async processText(text, title = 'Direct Text Input') {
    const response = await fetch(`${API_BASE}/text-input`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, title }),
    });
    
    return handleResponse(response, 'Text processing failed');
  },

  /**
   * Ask a question and get answers from uploaded documents.
   * 
   * This is the main Q&A endpoint. It searches all documents and
   * returns relevant passages with confidence scores.
   * 
   * @param {string} query - The question to ask
   * @param {number} [topK=3] - Number of source passages to return
   * @param {string[]|null} [docIds=null] - Optional filter to specific documents
   * @returns {Promise<Object>} Answer response with answer text, sources, and confidence
   * @throws {Error} If no documents available or query is empty
   * 
   * @example
   * const result = await api.askQuestion('What is machine learning?', 5);
   * console.log(`Answer: ${result.answer}`);
   * console.log(`Confidence: ${result.confidence_score * 100}%`);
   */
  async askQuestion(query, topK = 3, docIds = null) {
    const body = { query, top_k: topK };
    if (docIds && docIds.length > 0) {
      body.doc_ids = docIds;
    }
    
    const response = await fetch(`${API_BASE}/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    
    return handleResponse(response, 'Question answering failed');
  },

  /**
   * Extract relevant passages for a query without composing an answer.
   * 
   * Returns raw passage matches with similarity scores.
   * Useful for debugging or showing detailed search results.
   * 
   * @param {string} query - The search query
   * @param {number} [topK=5] - Number of passages to return
   * @param {string[]|null} [docIds=null] - Optional filter to specific documents
   * @returns {Promise<Object>} Response with list of matching passages
   * @throws {Error} If no documents available or query is empty
   */
  async extractPassages(query, topK = 5, docIds = null) {
    const body = { query, top_k: topK };
    if (docIds && docIds.length > 0) {
      body.doc_ids = docIds;
    }
    
    const response = await fetch(`${API_BASE}/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    
    return handleResponse(response, 'Extraction failed');
  },

  /**
   * Get list of all documents in the knowledge base.
   * 
   * @returns {Promise<Object>} Response with documents array and total_count
   * @throws {Error} If request fails
   * 
   * @example
   * const { documents, total_count } = await api.listDocuments();
   * documents.forEach(doc => console.log(doc.filename));
   */
  async listDocuments() {
    const response = await fetch(`${API_BASE}/documents`);
    return handleResponse(response, 'Failed to fetch documents');
  },

  /**
   * Delete a specific document from the knowledge base.
   * 
   * @param {string} docId - The unique identifier of the document to delete
   * @returns {Promise<Object>} Confirmation response
   * @throws {Error} If document not found or deletion fails
   * 
   * @example
   * await api.deleteDocument('abc-123-def');
   */
  async deleteDocument(docId) {
    const response = await fetch(`${API_BASE}/documents/${docId}`, {
      method: 'DELETE',
    });
    
    return handleResponse(response, 'Delete failed');
  },

  /**
   * Clear all documents from the knowledge base.
   * 
   * Warning: This removes all uploaded documents permanently.
   * 
   * @returns {Promise<Object>} Confirmation response with count of deleted documents
   * @throws {Error} If clearing fails
   */
  async clearAllDocuments() {
    const response = await fetch(`${API_BASE}/documents`, {
      method: 'DELETE',
    });
    
    return handleResponse(response, 'Failed to clear documents');
  },
};

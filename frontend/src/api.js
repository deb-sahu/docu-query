const API_BASE = '/api';

export const api = {
  // Upload a file
  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }
    
    return response.json();
  },

  // Process direct text input
  async processText(text, title = 'Direct Text Input') {
    const response = await fetch(`${API_BASE}/text-input`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, title }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Text processing failed');
    }
    
    return response.json();
  },

  // Ask a question
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
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Question answering failed');
    }
    
    return response.json();
  },

  // Extract passages
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
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Extraction failed');
    }
    
    return response.json();
  },

  // List documents
  async listDocuments() {
    const response = await fetch(`${API_BASE}/documents`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch documents');
    }
    
    return response.json();
  },

  // Delete a document
  async deleteDocument(docId) {
    const response = await fetch(`${API_BASE}/documents/${docId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Delete failed');
    }
    
    return response.json();
  },

  // Clear all documents
  async clearAllDocuments() {
    const response = await fetch(`${API_BASE}/documents`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error('Failed to clear documents');
    }
    
    return response.json();
  },
};


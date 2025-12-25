/**
 * API Client for DocuQuery
 */

const API_BASE = '/api';

async function handleResponse(response, fallbackMessage) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || fallbackMessage);
  }
  return response.json();
}

export const api = {
  async getConfig() {
    const response = await fetch(`${API_BASE}/config`);
    return handleResponse(response, 'Failed to get config');
  },

  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(response, 'Upload failed');
  },

  async processText(text, title = 'Direct Text Input') {
    const response = await fetch(`${API_BASE}/text-input`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, title }),
    });
    return handleResponse(response, 'Text processing failed');
  },

  async askQuestion(query, topK = 4, docIds = null) {
    const body = { query, top_k: topK };
    if (docIds?.length > 0) body.doc_ids = docIds;
    
    const response = await fetch(`${API_BASE}/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return handleResponse(response, 'Question answering failed');
  },

  async listDocuments() {
    const response = await fetch(`${API_BASE}/documents`);
    return handleResponse(response, 'Failed to fetch documents');
  },

  async deleteDocument(docId) {
    const response = await fetch(`${API_BASE}/documents/${docId}`, {
      method: 'DELETE',
    });
    return handleResponse(response, 'Delete failed');
  },

  async clearAllDocuments() {
    const response = await fetch(`${API_BASE}/documents`, {
      method: 'DELETE',
    });
    return handleResponse(response, 'Failed to clear documents');
  },
};

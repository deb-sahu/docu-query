import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileText, File, Trash2, RefreshCw, 
  AlertTriangle, X, FileType 
} from 'lucide-react';
import { api } from '../api';
import './DocumentList.css';

function DocumentList({ documents, onDelete, onRefresh }) {
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [isClearing, setIsClearing] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  const getFileIcon = (fileType) => {
    switch (fileType) {
      case 'PDF':
        return <File size={18} className="icon-pdf" />;
      case 'DOCX':
        return <FileType size={18} className="icon-docx" />;
      case 'TEXT':
        return <FileText size={18} className="icon-text" />;
      default:
        return <FileText size={18} />;
    }
  };

  const handleClearAll = async () => {
    setIsClearing(true);
    try {
      await api.clearAllDocuments();
      onRefresh();
    } catch (error) {
      console.error('Failed to clear documents:', error);
    } finally {
      setIsClearing(false);
      setShowClearConfirm(false);
    }
  };

  return (
    <div className="document-list">
      <div className="list-header">
        <h3>
          <FileText size={20} />
          Knowledge Base
        </h3>
        <div className="header-actions">
          <button 
            className="refresh-btn"
            onClick={onRefresh}
            title="Refresh"
          >
            <RefreshCw size={16} />
          </button>
          {documents.length > 0 && (
            <button 
              className="clear-btn"
              onClick={() => setShowClearConfirm(true)}
              title="Clear all"
            >
              <Trash2 size={16} />
            </button>
          )}
        </div>
      </div>

      {/* Clear Confirmation */}
      <AnimatePresence>
        {showClearConfirm && (
          <motion.div
            className="clear-confirm"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <div className="confirm-content">
              <AlertTriangle size={20} />
              <span>Clear all {documents.length} documents?</span>
            </div>
            <div className="confirm-actions">
              <button 
                className="confirm-yes"
                onClick={handleClearAll}
                disabled={isClearing}
              >
                {isClearing ? 'Clearing...' : 'Yes, clear'}
              </button>
              <button 
                className="confirm-no"
                onClick={() => setShowClearConfirm(false)}
              >
                Cancel
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {documents.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">
            <FileText size={32} />
          </div>
          <p>No documents uploaded yet</p>
          <span>Upload files or add text to get started</span>
        </div>
      ) : (
        <div className="documents">
          <AnimatePresence>
            {documents.map((doc, index) => (
              <motion.div
                key={doc.doc_id}
                className="document-item"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ delay: index * 0.05 }}
              >
                <div className="doc-icon">
                  {getFileIcon(doc.file_type)}
                </div>
                <div className="doc-info">
                  <span className="doc-name" title={doc.filename}>
                    {doc.filename}
                  </span>
                  <div className="doc-meta">
                    <span className="doc-type">{doc.file_type}</span>
                    <span className="doc-chunks">{doc.chunks} chunks</span>
                  </div>
                </div>
                
                {deleteConfirm === doc.doc_id ? (
                  <div className="delete-confirm">
                    <button 
                      className="confirm-delete"
                      onClick={() => {
                        onDelete(doc.doc_id);
                        setDeleteConfirm(null);
                      }}
                    >
                      Delete
                    </button>
                    <button 
                      className="cancel-delete"
                      onClick={() => setDeleteConfirm(null)}
                    >
                      <X size={14} />
                    </button>
                  </div>
                ) : (
                  <button 
                    className="delete-btn"
                    onClick={() => setDeleteConfirm(doc.doc_id)}
                    title="Delete document"
                  >
                    <Trash2 size={16} />
                  </button>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {documents.length > 0 && (
        <div className="list-footer">
          <span>{documents.length} document{documents.length !== 1 ? 's' : ''}</span>
          <span className="total-chunks">
            {documents.reduce((sum, doc) => sum + doc.chunks, 0)} total chunks
          </span>
        </div>
      )}
    </div>
  );
}

export default DocumentList;


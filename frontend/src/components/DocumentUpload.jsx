/**
 * DocumentUpload Component
 * ========================
 * 
 * Drag-and-drop file upload interface for adding documents to the knowledge base.
 * 
 * Features:
 * - Drag and drop file upload zone
 * - Click to browse files
 * - Multiple file upload support
 * - Upload progress queue with status indicators
 * - Automatic cleanup of successful uploads from queue
 * 
 * Supported file types: PDF, DOCX, TXT
 * 
 * Props:
 * - onUploadSuccess: Callback fired when a file is successfully uploaded
 * - isLoading: Boolean indicating if upload is in progress
 * - setIsLoading: Function to update loading state
 */

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2, X } from 'lucide-react';
import { api } from '../api';
import './DocumentUpload.css';

function DocumentUpload({ onUploadSuccess, isLoading, setIsLoading }) {
  // Queue of files being uploaded with their status
  const [uploadQueue, setUploadQueue] = useState([]);
  // Error message to display
  const [error, setError] = useState(null);

  /**
   * Handle files dropped or selected.
   * Processes each file sequentially, updating status in the queue.
   */
  const onDrop = useCallback(async (acceptedFiles) => {
    setError(null);
    
    // Add all files to the upload queue with pending status
    const newQueue = acceptedFiles.map(file => ({
      file,
      status: 'pending',  // pending -> uploading -> success/error
      progress: 0,
    }));
    
    setUploadQueue(prev => [...prev, ...newQueue]);
    setIsLoading(true);

    // Process each file sequentially
    for (let i = 0; i < acceptedFiles.length; i++) {
      const file = acceptedFiles[i];
      
      // Update status to uploading
      setUploadQueue(prev => prev.map(item => 
        item.file === file ? { ...item, status: 'uploading' } : item
      ));

      try {
        // Upload file to backend
        const result = await api.uploadFile(file);
        
        // Update status to success
        setUploadQueue(prev => prev.map(item => 
          item.file === file ? { ...item, status: 'success', result } : item
        ));
        
        // Notify parent component
        onUploadSuccess(result);
      } catch (err) {
        // Update status to error
        setUploadQueue(prev => prev.map(item => 
          item.file === file ? { ...item, status: 'error', error: err.message } : item
        ));
        setError(err.message);
      }
    }

    setIsLoading(false);
    
    // Clear successful uploads from queue after 3 seconds
    setTimeout(() => {
      setUploadQueue(prev => prev.filter(item => item.status !== 'success'));
    }, 3000);
  }, [onUploadSuccess, setIsLoading]);

  // Configure react-dropzone
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    multiple: true, // Allow multiple file selection
  });

  /**
   * Remove a file from the upload queue.
   * Used for dismissing errors or completed uploads.
   */
  const removeFromQueue = (file) => {
    setUploadQueue(prev => prev.filter(item => item.file !== file));
  };

  /**
   * Get the appropriate icon for a file based on its extension.
   * Currently returns a generic file icon for all types.
   */
  const getFileIcon = (filename) => {
    return <FileText size={20} />;
  };

  /**
   * Get the status icon based on upload status.
   */
  const getStatusIcon = (status) => {
    switch (status) {
      case 'uploading':
        return <Loader2 size={18} className="spin" />;
      case 'success':
        return <CheckCircle size={18} className="success-icon" />;
      case 'error':
        return <AlertCircle size={18} className="error-icon" />;
      default:
        return null;
    }
  };

  return (
    <div className="document-upload">
      {/* Section Header */}
      <div className="section-header">
        <h2>Upload Documents</h2>
        <p>Upload PDF, DOCX, or TXT files to build your knowledge base</p>
      </div>

      {/* Dropzone Area */}
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${isLoading ? 'disabled' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="dropzone-content">
          <motion.div 
            className="dropzone-icon"
            animate={{ scale: isDragActive ? 1.1 : 1 }}
          >
            <Upload size={48} />
          </motion.div>
          <div className="dropzone-text">
            {isDragActive ? (
              <span className="gradient-text">Drop files here...</span>
            ) : (
              <>
                <span className="primary-text">Drag & drop files here</span>
                <span className="secondary-text">or click to browse</span>
              </>
            )}
          </div>
          {/* Supported file type badges */}
          <div className="file-types">
            <span className="file-type">PDF</span>
            <span className="file-type">DOCX</span>
            <span className="file-type">TXT</span>
          </div>
        </div>
      </div>

      {/* Upload Queue - shows files being uploaded */}
      <AnimatePresence>
        {uploadQueue.length > 0 && (
          <motion.div 
            className="upload-queue"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <h4>Upload Queue</h4>
            <div className="queue-list">
              {uploadQueue.map((item, index) => (
                <motion.div
                  key={item.file.name + index}
                  className={`queue-item ${item.status}`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                >
                  <div className="queue-item-icon">
                    {getFileIcon(item.file.name)}
                  </div>
                  <div className="queue-item-info">
                    <span className="queue-item-name">{item.file.name}</span>
                    <span className="queue-item-size">
                      {(item.file.size / 1024).toFixed(1)} KB
                    </span>
                  </div>
                  <div className="queue-item-status">
                    {getStatusIcon(item.status)}
                  </div>
                  {/* Show remove button when not actively uploading */}
                  {item.status !== 'uploading' && (
                    <button 
                      className="queue-item-remove"
                      onClick={() => removeFromQueue(item.file)}
                    >
                      <X size={16} />
                    </button>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error Message Display */}
      <AnimatePresence>
        {error && (
          <motion.div
            className="error-message"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <AlertCircle size={18} />
            {error}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default DocumentUpload;

/**
 * DocumentUpload - Drag & drop file upload component
 */

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2, X } from 'lucide-react';
import { api } from '../api';
import './DocumentUpload.css';

function DocumentUpload({ onUploadSuccess, isLoading, setIsLoading }) {
  const [uploadQueue, setUploadQueue] = useState([]);
  const [error, setError] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    setError(null);
    
    const newQueue = acceptedFiles.map(file => ({
      file,
      status: 'pending',
    }));
    
    setUploadQueue(prev => [...prev, ...newQueue]);
    setIsLoading(true);

    for (const file of acceptedFiles) {
      setUploadQueue(prev => prev.map(item => 
        item.file === file ? { ...item, status: 'uploading' } : item
      ));

      try {
        const result = await api.uploadFile(file);
        setUploadQueue(prev => prev.map(item => 
          item.file === file ? { ...item, status: 'success', result } : item
        ));
        onUploadSuccess(result);
      } catch (err) {
        setUploadQueue(prev => prev.map(item => 
          item.file === file ? { ...item, status: 'error', error: err.message } : item
        ));
        setError(err.message);
      }
    }

    setIsLoading(false);
    setTimeout(() => {
      setUploadQueue(prev => prev.filter(item => item.status !== 'success'));
    }, 3000);
  }, [onUploadSuccess, setIsLoading]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    multiple: true,
  });

  const removeFromQueue = (file) => {
    setUploadQueue(prev => prev.filter(item => item.file !== file));
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'uploading': return <Loader2 size={18} className="spin" />;
      case 'success': return <CheckCircle size={18} className="success-icon" />;
      case 'error': return <AlertCircle size={18} className="error-icon" />;
      default: return null;
    }
  };

  return (
    <div className="document-upload">
      <div className="section-header">
        <h2>Upload Documents</h2>
        <p>Upload PDF, DOCX, or TXT files to build your knowledge base</p>
      </div>

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
          <div className="file-types">
            <span className="file-type">PDF</span>
            <span className="file-type">DOCX</span>
            <span className="file-type">TXT</span>
          </div>
        </div>
      </div>

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
                    <FileText size={20} />
                  </div>
                  <div className="queue-item-info">
                    <span className="queue-item-name">{item.file.name}</span>
                    <span className="queue-item-size">{(item.file.size / 1024).toFixed(1)} KB</span>
                  </div>
                  <div className="queue-item-status">
                    {getStatusIcon(item.status)}
                  </div>
                  {item.status !== 'uploading' && (
                    <button className="queue-item-remove" onClick={() => removeFromQueue(item.file)}>
                      <X size={16} />
                    </button>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

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

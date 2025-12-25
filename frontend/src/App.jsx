/**
 * DocuQuery - Main Application Component
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, MessageSquare, Database, Sparkles } from 'lucide-react';
import Header from './components/Header';
import DocumentUpload from './components/DocumentUpload';
import TextInput from './components/TextInput';
import QuestionAnswer from './components/QuestionAnswer';
import DocumentList from './components/DocumentList';
import { api } from './api';
import './styles/App.css';

function App() {
  const [documents, setDocuments] = useState([]);
  const [activeTab, setActiveTab] = useState('upload');
  const [isLoading, setIsLoading] = useState(false);
  const [notification, setNotification] = useState(null);
  const [config, setConfig] = useState(null);

  useEffect(() => {
    fetchDocuments();
    api.getConfig().then(setConfig).catch(console.error);
  }, []);

  const fetchDocuments = async () => {
    try {
      const data = await api.listDocuments();
      setDocuments(data.documents || []);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4000);
  };

  const handleUploadSuccess = (result) => {
    showNotification(`${result.filename} uploaded successfully!`);
    fetchDocuments();
  };

  const handleTextProcessed = (result) => {
    showNotification(`Text processed into ${result.chunks_count} chunks!`);
    fetchDocuments();
  };

  const handleDeleteDocument = async (docId) => {
    try {
      await api.deleteDocument(docId);
      showNotification('Document deleted');
      fetchDocuments();
    } catch (error) {
      showNotification(error.message, 'error');
    }
  };

  const tabs = [
    { id: 'upload', label: 'Upload Files', icon: FileText },
    { id: 'text', label: 'Text Input', icon: Database },
    { id: 'qa', label: 'Ask Questions', icon: MessageSquare },
  ];

  return (
    <div className="app">
      <Header />
      
      <AnimatePresence>
        {notification && (
          <motion.div
            className={`notification notification-${notification.type}`}
            initial={{ opacity: 0, y: -50, x: '-50%' }}
            animate={{ opacity: 1, y: 0, x: '-50%' }}
            exit={{ opacity: 0, y: -50, x: '-50%' }}
          >
            <Sparkles size={18} />
            {notification.message}
          </motion.div>
        )}
      </AnimatePresence>

      <main className="main-content">
        <div className="container">
          <motion.div 
            className="stats-banner glass"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="stat">
              <span className="stat-value gradient-text">{documents.length}</span>
              <span className="stat-label">Documents</span>
            </div>
            <div className="stat-divider" />
            <div className="stat">
              <span className="stat-value gradient-text">
                {documents.reduce((sum, doc) => sum + doc.chunks, 0)}
              </span>
              <span className="stat-label">Chunks</span>
            </div>
            <div className="stat-divider" />
            <div className="stat">
              <span className="stat-value gradient-text">
                {config?.llm_provider || '...'}
              </span>
              <span className="stat-label">LLM</span>
            </div>
          </motion.div>

          <nav className="tab-nav">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <tab.icon size={18} />
                {tab.label}
                {activeTab === tab.id && (
                  <motion.div className="tab-indicator" layoutId="tabIndicator" />
                )}
              </button>
            ))}
          </nav>

          <div className="content-grid">
            <motion.div className="panel main-panel" layout>
              <AnimatePresence mode="wait">
                {activeTab === 'upload' && (
                  <motion.div
                    key="upload"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                  >
                    <DocumentUpload 
                      onUploadSuccess={handleUploadSuccess}
                      isLoading={isLoading}
                      setIsLoading={setIsLoading}
                    />
                  </motion.div>
                )}
                
                {activeTab === 'text' && (
                  <motion.div
                    key="text"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                  >
                    <TextInput 
                      onTextProcessed={handleTextProcessed}
                      isLoading={isLoading}
                      setIsLoading={setIsLoading}
                    />
                  </motion.div>
                )}
                
                {activeTab === 'qa' && (
                  <motion.div
                    key="qa"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                  >
                    <QuestionAnswer 
                      documents={documents}
                      isLoading={isLoading}
                      setIsLoading={setIsLoading}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            <motion.div 
              className="panel side-panel"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <DocumentList 
                documents={documents}
                onDelete={handleDeleteDocument}
                onRefresh={fetchDocuments}
              />
            </motion.div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

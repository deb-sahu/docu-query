/**
 * QuestionAnswer Component - Q&A interface with LLM-powered answers
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, Send, Loader2, AlertCircle, BookOpen, 
  ChevronDown, ChevronUp, Sparkles, FileText, Cpu 
} from 'lucide-react';
import { api } from '../api';
import './QuestionAnswer.css';

function QuestionAnswer({ documents, isLoading, setIsLoading }) {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState(null);
  const [error, setError] = useState(null);
  const [expandedSources, setExpandedSources] = useState({});
  const [questionHistory, setQuestionHistory] = useState([]);
  const [config, setConfig] = useState(null);

  useEffect(() => {
    api.getConfig().then(setConfig).catch(console.error);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a question');
      return;
    }

    if (documents.length === 0) {
      setError('Please upload documents first');
      return;
    }

    setError(null);
    setIsLoading(true);
    setAnswer(null);

    try {
      const result = await api.askQuestion(query, 4);
      setAnswer(result);
      setQuestionHistory(prev => [
        { query, timestamp: new Date() },
        ...prev.slice(0, 9)
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSource = (index) => {
    setExpandedSources(prev => ({ ...prev, [index]: !prev[index] }));
  };

  return (
    <div className="question-answer">
      <div className="section-header">
        <h2>Ask Questions</h2>
        <p>Get answers from your documents using AI</p>
        {config && (
          <div className="llm-badge">
            <Cpu size={14} />
            <span>{config.llm_provider}: {config.llm_model}</span>
          </div>
        )}
      </div>

      {documents.length === 0 ? (
        <div className="no-documents">
          <BookOpen size={48} />
          <h3>No Documents Available</h3>
          <p>Upload documents to start asking questions</p>
        </div>
      ) : (
        <>
          <form onSubmit={handleSubmit} className="question-form">
            <div className="search-input-wrapper">
              <Search size={20} className="search-icon" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a question about your documents..."
                disabled={isLoading}
              />
              <motion.button
                type="submit"
                className="search-btn"
                disabled={isLoading || !query.trim()}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {isLoading ? <Loader2 size={20} className="spin" /> : <Send size={20} />}
              </motion.button>
            </div>
          </form>

          {error && (
            <motion.div
              className="error-message"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <AlertCircle size={18} />
              {error}
            </motion.div>
          )}

          <AnimatePresence mode="wait">
            {isLoading && (
              <motion.div
                className="loading-answer"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <div className="loading-dots">
                  <span></span><span></span><span></span>
                </div>
                <span>Generating answer with {config?.llm_provider || 'AI'}...</span>
              </motion.div>
            )}

            {answer && !isLoading && (
              <motion.div
                className="answer-container"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="query-echo">
                  <strong>Q:</strong> {answer.query}
                </div>

                <div className="answer-text">
                  <h4>
                    <Sparkles size={18} />
                    Answer
                    <span className="provider-tag">{answer.llm_provider}</span>
                  </h4>
                  <div className="answer-content">
                    {answer.answer.split('\n').map((line, i) => (
                      line.trim() ? <p key={i}>{line}</p> : null
                    ))}
                  </div>
                </div>

                {answer.sources?.length > 0 && (
                  <div className="sources-section">
                    <h4>
                      <FileText size={18} />
                      Sources ({answer.sources.length})
                    </h4>
                    <div className="sources-list">
                      {answer.sources.map((source, index) => (
                        <motion.div
                          key={index}
                          className="source-card"
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                        >
                          <button
                            className="source-header"
                            onClick={() => toggleSource(index)}
                          >
                            <div className="source-meta">
                              <span className="source-filename">{source.filename}</span>
                              <span className="source-chunk">Chunk #{source.chunk_index}</span>
                            </div>
                            <div className="source-score">
                              <span>{(source.score * 100).toFixed(1)}%</span>
                              {expandedSources[index] ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                            </div>
                          </button>
                          
                          <AnimatePresence>
                            {expandedSources[index] && (
                              <motion.div
                                className="source-content"
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                              >
                                <p>{source.text}</p>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {questionHistory.length > 0 && !answer && (
            <div className="question-history">
              <h4>Recent Questions</h4>
              <div className="history-list">
                {questionHistory.map((item, index) => (
                  <button
                    key={index}
                    className="history-item"
                    onClick={() => setQuery(item.query)}
                  >
                    <Search size={14} />
                    <span>{item.query}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default QuestionAnswer;

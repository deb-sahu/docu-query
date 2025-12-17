/**
 * QuestionAnswer Component
 * ========================
 * 
 * The main Q&A interface for asking questions about uploaded documents.
 * 
 * Features:
 * - Search input for entering questions
 * - Answer display with confidence scoring
 * - Expandable source passages with highlighting
 * - Question history for quick re-queries
 * 
 * The component calls the /api/answer endpoint and displays:
 * - The composed answer from relevant passages
 * - Overall confidence score with visual meter
 * - Source documents with individual confidence badges
 * - Highlighted query terms in source text
 * 
 * Props:
 * - documents: Array of document metadata (to check if documents exist)
 * - isLoading: Boolean indicating if query is in progress
 * - setIsLoading: Function to update loading state
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, Send, Loader2, AlertCircle, BookOpen, 
  ChevronDown, ChevronUp, Sparkles, FileText 
} from 'lucide-react';
import { api } from '../api';
import './QuestionAnswer.css';

function QuestionAnswer({ documents, isLoading, setIsLoading }) {
  // User's question input
  const [query, setQuery] = useState('');
  // Answer response from API
  const [answer, setAnswer] = useState(null);
  // Error message to display
  const [error, setError] = useState(null);
  // Track which source cards are expanded
  const [expandedSources, setExpandedSources] = useState({});
  // History of recent questions for quick re-query
  const [questionHistory, setQuestionHistory] = useState([]);

  /**
   * Submit the question to the API.
   * Validates input, calls API, and updates state with results.
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate question is not empty
    if (!query.trim()) {
      setError('Please enter a question');
      return;
    }

    // Check if documents are available
    if (documents.length === 0) {
      setError('Please upload documents or add text first');
      return;
    }

    setError(null);
    setIsLoading(true);
    setAnswer(null);

    try {
      // Call the answer API with top 5 results
      const result = await api.askQuestion(query, 5);
      setAnswer(result);
      
      // Add to question history (keep last 10)
      setQuestionHistory(prev => [
        { query, timestamp: new Date(), confidence: result.confidence_score },
        ...prev.slice(0, 9)
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Toggle expansion of a source card to show/hide full text.
   */
  const toggleSource = (index) => {
    setExpandedSources(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  /**
   * Get the CSS color variable for a confidence level.
   */
  const getConfidenceColor = (confidence) => {
    if (confidence === 'high') return 'var(--confidence-high)';
    if (confidence === 'medium') return 'var(--confidence-medium)';
    return 'var(--confidence-low)';
  };

  /**
   * Convert confidence score (0-1) to percentage.
   */
  const getConfidencePercent = (score) => Math.round(score * 100);

  /**
   * Highlight query terms in the source text.
   * Returns React elements with <mark> tags around matching terms.
   * 
   * @param {string} text - The source text
   * @param {Array} highlights - Array of {start, end} positions to highlight
   * @returns {Array} React elements with highlighted terms
   */
  const highlightText = (text, highlights) => {
    if (!highlights || highlights.length === 0) return text;
    
    let result = [];
    let lastEnd = 0;
    
    highlights.forEach((h, i) => {
      // Add text before the highlight
      if (h.start > lastEnd) {
        result.push(text.slice(lastEnd, h.start));
      }
      // Add highlighted text
      result.push(
        <mark key={i} className="highlight">
          {text.slice(h.start, h.end)}
        </mark>
      );
      lastEnd = h.end;
    });
    
    // Add remaining text after last highlight
    if (lastEnd < text.length) {
      result.push(text.slice(lastEnd));
    }
    
    return result;
  };

  return (
    <div className="question-answer">
      {/* Section Header */}
      <div className="section-header">
        <h2>Ask Questions</h2>
        <p>Query your uploaded documents and get answers with source references</p>
      </div>

      {/* Empty State - Show when no documents available */}
      {documents.length === 0 ? (
        <div className="no-documents">
          <BookOpen size={48} />
          <h3>No Documents Available</h3>
          <p>Upload documents or add text to start asking questions</p>
        </div>
      ) : (
        <>
          {/* Question Input Form */}
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
                {isLoading ? (
                  <Loader2 size={20} className="spin" />
                ) : (
                  <Send size={20} />
                )}
              </motion.button>
            </div>
          </form>

          {/* Error Message */}
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

          {/* Answer Display Area */}
          <AnimatePresence mode="wait">
            {/* Loading State */}
            {isLoading && (
              <motion.div
                className="loading-answer"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span>Searching documents...</span>
              </motion.div>
            )}

            {/* Answer Results */}
            {answer && !isLoading && (
              <motion.div
                className="answer-container"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                {/* Confidence Score Banner */}
                <div className="confidence-banner">
                  <div className="confidence-info">
                    <Sparkles size={18} />
                    <span>Confidence Score</span>
                  </div>
                  <div className="confidence-meter">
                    <div 
                      className="confidence-fill"
                      style={{ 
                        width: `${getConfidencePercent(answer.confidence_score)}%`,
                        background: answer.confidence_score >= 0.5 
                          ? 'var(--confidence-high)' 
                          : answer.confidence_score >= 0.2 
                            ? 'var(--confidence-medium)' 
                            : 'var(--confidence-low)'
                      }}
                    />
                  </div>
                  <span className="confidence-value">
                    {getConfidencePercent(answer.confidence_score)}%
                  </span>
                </div>

                {/* Echo the user's question */}
                <div className="query-echo">
                  <strong>Q:</strong> {answer.query}
                </div>

                {/* Answer Text */}
                <div className="answer-text">
                  <h4>Answer</h4>
                  <div className="answer-content">
                    {answer.answer.split('\n\n').map((paragraph, i) => (
                      <p key={i}>{paragraph}</p>
                    ))}
                  </div>
                </div>

                {/* Source Passages */}
                {answer.sources && answer.sources.length > 0 && (
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
                          {/* Source Header - clickable to expand */}
                          <button
                            className="source-header"
                            onClick={() => toggleSource(index)}
                          >
                            <div className="source-meta">
                              <span 
                                className="confidence-badge"
                                style={{ 
                                  background: getConfidenceColor(source.confidence) + '20',
                                  color: getConfidenceColor(source.confidence)
                                }}
                              >
                                {source.confidence}
                              </span>
                              <span className="source-filename">{source.filename}</span>
                              <span className="source-chunk">Chunk #{source.chunk_id}</span>
                            </div>
                            <div className="source-score">
                              <span>{(source.score * 100).toFixed(1)}%</span>
                              {expandedSources[index] ? (
                                <ChevronUp size={18} />
                              ) : (
                                <ChevronDown size={18} />
                              )}
                            </div>
                          </button>
                          
                          {/* Expandable Source Content */}
                          <AnimatePresence>
                            {expandedSources[index] && (
                              <motion.div
                                className="source-content"
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                              >
                                <p>
                                  {highlightText(source.text, source.highlight_indices)}
                                </p>
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

          {/* Question History - shown when no active answer */}
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
                    <span className="history-confidence">
                      {getConfidencePercent(item.confidence)}%
                    </span>
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

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Type, Send, Loader2, AlertCircle } from 'lucide-react';
import { api } from '../api';
import './TextInput.css';

function TextInput({ onTextProcessed, isLoading, setIsLoading }) {
  const [text, setText] = useState('');
  const [title, setTitle] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!text.trim()) {
      setError('Please enter some text');
      return;
    }

    if (text.trim().length < 50) {
      setError('Text should be at least 50 characters for meaningful processing');
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      const result = await api.processText(text, title || 'Direct Text Input');
      onTextProcessed(result);
      setText('');
      setTitle('');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="text-input">
      <div className="section-header">
        <h2>Direct Text Input</h2>
        <p>Paste or type text directly for ad-hoc queries without uploading files</p>
      </div>

      <form onSubmit={handleSubmit} className="text-form">
        <div className="input-group">
          <label htmlFor="title">Title (optional)</label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., API Documentation, User Manual..."
            className="title-input"
            disabled={isLoading}
          />
        </div>

        <div className="input-group">
          <label htmlFor="text">
            Content
            <span className="char-count">{text.length} characters</span>
          </label>
          <div className="textarea-wrapper">
            <Type size={20} className="textarea-icon" />
            <textarea
              id="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste your technical documentation, product specifications, user manual content, or any text you want to query..."
              rows={12}
              disabled={isLoading}
            />
          </div>
        </div>

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

        <motion.button
          type="submit"
          className="submit-btn"
          disabled={isLoading || !text.trim()}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {isLoading ? (
            <>
              <Loader2 size={20} className="spin" />
              Processing...
            </>
          ) : (
            <>
              <Send size={20} />
              Process Text
            </>
          )}
        </motion.button>
      </form>

      <div className="tips">
        <h4>💡 Tips for best results</h4>
        <ul>
          <li>Include complete paragraphs or sections for context</li>
          <li>Technical documentation works especially well</li>
          <li>The more text you provide, the better the answers</li>
        </ul>
      </div>
    </div>
  );
}

export default TextInput;


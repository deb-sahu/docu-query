import { motion } from 'framer-motion';
import { BookOpen, Github, Zap } from 'lucide-react';
import './Header.css';

function Header() {
  return (
    <header className="header glass">
      <div className="header-content">
        <motion.div 
          className="logo"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <div className="logo-icon">
            <BookOpen size={24} />
          </div>
          <div className="logo-text">
            <span className="logo-title">DocuQuery</span>
            <span className="logo-subtitle">Document Q&A System</span>
          </div>
        </motion.div>

        <motion.div 
          className="header-badge"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
        >
          <Zap size={14} />
          <span>TF-IDF Powered</span>
        </motion.div>

        <motion.nav 
          className="header-nav"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <a 
            href="https://github.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="nav-link"
          >
            <Github size={20} />
          </a>
        </motion.nav>
      </div>
    </header>
  );
}

export default Header;


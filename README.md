# DocuQuery - Document Q&A System

A web-based Question Answering application that allows users to upload documents and ask questions based on the document content. Built with FastAPI backend and React frontend.

![Document Q&A System](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## Features

### Frontend
- 🎨 Beautiful, modern dark-themed UI with neon accents
- 📁 Drag & drop file upload (PDF, DOCX, TXT)
- 📝 Direct text input for ad-hoc queries
- 💬 Interactive Q&A interface
- 🔍 Highlighted source passages
- 📊 Confidence scores for answers
- 📋 Question history tracking

### Backend
- ⚡ FastAPI-powered REST API
- 📄 Document parsing (PDF, DOCX, TXT)
- 🔎 TF-IDF based semantic search
- 🧩 Text chunking with overlap
- 📚 Multi-document knowledge base

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+

### Backend Setup

```bash
# Navigate to project directory
cd Qa_Backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000` and will proxy API requests to the backend at `http://localhost:8000`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload a document (PDF, DOCX, TXT) |
| POST | `/api/text-input` | Process direct text input |
| POST | `/api/answer` | Ask a question and get answers with sources |
| POST | `/api/extract` | Extract relevant passages for a query |
| GET | `/api/documents` | List all uploaded documents |
| DELETE | `/api/documents/{doc_id}` | Delete a specific document |
| DELETE | `/api/documents` | Clear all documents |
| GET | `/health` | Health check endpoint |

## API Usage Examples

### Upload a Document
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@document.pdf"
```

### Process Text Input
```bash
curl -X POST "http://localhost:8000/api/text-input" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text content here...", "title": "My Document"}'
```

### Ask a Question
```bash
curl -X POST "http://localhost:8000/api/answer" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?", "top_k": 3}'
```

## Project Structure

```
docu-query/
├── app/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── core/
│   │   └── config.py          # Configuration settings
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── services/
│   │   ├── parser.py          # Document parsing
│   │   └── vector_store.py    # TF-IDF search
│   ├── storage/
│   │   └── manager.py         # File management
│   └── main.py                # FastAPI app entry point
├── frontend/
│   ├── public/
│   │   └── favicon.svg
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── DocumentList.jsx
│   │   │   ├── DocumentUpload.jsx
│   │   │   ├── Header.jsx
│   │   │   ├── QuestionAnswer.jsx
│   │   │   └── TextInput.jsx
│   │   ├── styles/            # CSS styles
│   │   │   ├── App.css
│   │   │   └── index.css
│   │   ├── api.js             # API client
│   │   ├── App.jsx            # Main app component
│   │   └── main.jsx           # Entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── uploads/                   # Uploaded files (auto-created)
├── data/                      # Metadata storage (auto-created)
├── requirements.txt
├── run.sh                     # Startup script
├── LICENSE
└── README.md
```

## Configuration

Edit `app/core/config.py` to customize:

- `CHUNK_SIZE`: Size of text chunks (default: 1200 characters)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200 characters)

## Architecture

```
┌─────────────────┐      ┌─────────────────┐
│   React UI      │◄────►│   FastAPI       │
│   Port 3000     │      │   Port 8000     │
└─────────────────┘      └─────────────────┘
                               │
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
               PDF Parser  DOCX Parser  TXT Reader
                    │          │          │
                    └──────────┼──────────┘
                               ▼
                    TF-IDF Vector Store
                    (scikit-learn)
```

## Use Cases

- **Technical Documentation QA** - Answer questions from user manuals, API docs
- **Product Specifications** - Query product specs and datasheets
- **Research Papers** - Extract information from academic documents
- **Legal Documents** - Search through contracts and policies

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **pdfplumber** - PDF text extraction
- **python-docx** - DOCX file parsing
- **scikit-learn** - TF-IDF vectorization

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Framer Motion** - Animations
- **Lucide React** - Icons

## License

MIT License - See [LICENSE](LICENSE) for details.

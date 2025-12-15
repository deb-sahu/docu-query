# DocuQuery

A document-based Question Answering system that extracts answers from uploaded documents using TF-IDF similarity search.

## Features

- **Multi-format document parsing** — PDF, DOCX, and TXT support with text extraction
- **TF-IDF similarity search** — Find relevant passages using scikit-learn vectorization
- **Text chunking with overlap** — Configurable chunk size (1200 chars) and overlap (200 chars)
- **Multi-document knowledge base** — Query across multiple uploaded documents
- **Confidence scoring** — Relevance scores for retrieved passages
- **Source highlighting** — Shows which document and passage answered the query
- **Direct text input** — Paste text directly without file upload
- **REST API** — FastAPI backend with full OpenAPI documentation

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+

### Backend

```bash
cd docu-query
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Backend runs on `http://localhost:8000`, frontend on `http://localhost:3000`.

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

Technical documentation, product specifications, research papers, legal documents.

## Tech Stack

**Backend:** FastAPI, scikit-learn, pdfplumber, python-docx  
**Frontend:** React 18, Vite

## License

MIT License - See [LICENSE](LICENSE) for details.

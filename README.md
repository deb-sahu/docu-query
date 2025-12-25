# DocuQuery

LLM-powered document Q&A system using RAG (Retrieval-Augmented Generation). Upload documents and ask questions - get accurate answers with source references.

## Cost

This project is **100% free to run**. All components are open-source or have generous free tiers.

| Component | Cost | Notes |
|-----------|------|-------|
| ChromaDB | Free | Apache 2.0 license, runs locally |
| Sentence Transformers | Free | Open-source, runs locally on CPU |
| Gemini API | Free tier | 15 requests/min, 1M tokens/day |
| Ollama + Llama | Free | Runs 100% locally |

## Features

- **RAG-based Q&A** — Retrieves relevant context and generates answers using LLMs
- **Configurable LLM** — Supports Gemini (free) and Llama (via Ollama)
- **Semantic Search** — Uses sentence-transformers embeddings with ChromaDB
- **Multi-format Support** — PDF, DOCX, and TXT documents
- **Source Citations** — Shows which passages were used to generate answers
- **REST API** — FastAPI backend with OpenAPI docs

## Architecture

```
┌─────────────────┐      ┌─────────────────┐
│   React UI      │◄────►│   FastAPI       │
│   Port 3000     │      │   Port 8000     │
└─────────────────┘      └─────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        PDF Parser      DOCX Parser       TXT Reader
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                    ┌──────────────────┐
                    │ Text Chunking    │
                    │ (RecursiveText)  │
                    └────────┬─────────┘
                             ▼
                    ┌──────────────────┐
                    │ Embeddings       │
                    │ (MiniLM-L6-v2)   │
                    └────────┬─────────┘
                             ▼
                    ┌──────────────────┐
                    │ ChromaDB         │
                    │ (Vector Store)   │
                    └────────┬─────────┘
                             ▼
                    ┌──────────────────┐
                    │ LLM (Gemini/     │
                    │      Llama)      │
                    └──────────────────┘
```

## Steps to Run Locally

### Prerequisites

- Python 3.10+
- Node.js 18+
- (Optional) Ollama for local Llama models

### Step 1: Install Dependencies

```bash
cd docu-query
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure LLM Provider

Copy the example environment file and add your API key:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

**Option A: Gemini (Recommended - Free)**
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
```

Get a free API key at: https://aistudio.google.com/apikey

**Option B: Llama (Local via Ollama)**
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
```

Install Ollama and pull a model:
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.2
```

### Step 3: Start Backend

```bash
uvicorn app.main:app --reload --port 8000
```

API available at `http://localhost:8000/docs`

### Step 4: Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend available at `http://localhost:3000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/config` | Get current LLM configuration |
| POST | `/api/upload` | Upload a document |
| POST | `/api/text-input` | Process direct text |
| POST | `/api/answer` | Ask a question (RAG) |
| GET | `/api/documents` | List documents |
| DELETE | `/api/documents/{id}` | Delete a document |
| DELETE | `/api/documents` | Clear all documents |

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `gemini` | LLM provider: `gemini` or `ollama` |
| `GEMINI_API_KEY` | - | Google AI API key |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model name |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `CHUNK_SIZE` | `1000` | Text chunk size |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |

## Tech Stack

**Backend:** FastAPI, LangChain, ChromaDB, Sentence-Transformers  
**Frontend:** React 18, Vite  
**LLMs:** Google Gemini, Ollama (Llama)

## License

MIT License

# Semantic RAG Web Application

An open-source Retrieval-Augmented Generation (RAG) web application that enables semantic search over any document type with AI-generated answers powered by Ollama.

## Features

- **Multi-Format Document Support**: PDF, Word, Excel, PowerPoint, Text, Markdown, CSV, JSON, HTML
- **Semantic Search**: BERT-based embeddings with FAISS vector store
- **AI Answers**: Local LLM via Ollama (Mistral, Llama2, etc.) - no API costs
- **Modern UI**: Angular frontend with dark theme
- **Docker Ready**: Single `docker-compose up` deployment
- **Fully Local**: Everything runs on your machine, no data leaves your system

## Supported Document Formats

| Format | Extensions |
|--------|------------|
| PDF | `.pdf` |
| Microsoft Word | `.docx` |
| Microsoft Excel | `.xlsx` |
| Microsoft PowerPoint | `.pptx` |
| Plain Text | `.txt`, `.text` |
| Markdown | `.md`, `.markdown` |
| CSV | `.csv` |
| JSON | `.json` |
| HTML | `.html`, `.htm` |

## Tech Stack

| Component | Technology |
|-----------|------------|
| Embeddings | Sentence-Transformers (all-MiniLM-L6-v2) |
| Vector Store | FAISS |
| LLM | Ollama (Mistral by default) |
| Backend | FastAPI + Python |
| Frontend | Angular 17 |

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM (4GB minimum for Ollama)
- ~10GB disk space for models

### 1. Clone and Start

```bash
git clone https://github.com/anirudhatalmale6-alt/semantic-rag-webapp.git
cd semantic-rag-webapp
docker-compose up --build
```

### 2. Pull the Mistral Model

After containers start, pull the Mistral model (one-time setup):

```bash
docker exec -it rag-ollama ollama pull mistral
```

This downloads ~4GB. You can also use other models:
```bash
docker exec -it rag-ollama ollama pull llama2
docker exec -it rag-ollama ollama pull codellama
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **Ollama**: http://localhost:11434

## Using the Application

1. **Upload Documents**: Click "Upload Document" to add any supported file type
2. **Ask Questions**: Type a question in the search box
3. **View Results**: See the AI-generated answer and source passages with relevance scores

## API Reference

### Health Check
```bash
curl http://localhost:8000/
```

### Get Index Stats
```bash
curl http://localhost:8000/stats
```

### Get Supported Formats
```bash
curl http://localhost:8000/formats
```

### Ingest Document
```bash
# Upload a PDF
curl -X POST http://localhost:8000/ingest -F "file=@document.pdf"

# Upload a Word document
curl -X POST http://localhost:8000/ingest -F "file=@report.docx"

# Upload an Excel file
curl -X POST http://localhost:8000/ingest -F "file=@data.xlsx"

# Upload a PowerPoint
curl -X POST http://localhost:8000/ingest -F "file=@presentation.pptx"

# Upload CSV
curl -X POST http://localhost:8000/ingest -F "file=@data.csv"

# Upload JSON
curl -X POST http://localhost:8000/ingest -F "file=@config.json"
```

### Search Documents
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "top_k": 5}'
```

### Clear Index
```bash
curl -X DELETE http://localhost:8000/clear
```

## Configuration

Environment variables in `docker-compose.yml`:

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama API URL |
| `OLLAMA_MODEL` | `mistral` | LLM model for answer generation |
| `CHUNK_SIZE` | `500` | Characters per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `TOP_K` | `5` | Default search results |

### Changing the LLM Model

To use a different model (e.g., Llama2):

1. Pull the model: `docker exec -it rag-ollama ollama pull llama2`
2. Update `OLLAMA_MODEL` in docker-compose.yml to `llama2`
3. Restart: `docker-compose restart backend`

## Project Structure

```
semantic-rag-webapp/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI endpoints
│   │   ├── config.py        # Configuration
│   │   ├── chunker.py       # Text chunking
│   │   ├── document_loader.py # Multi-format document loading
│   │   ├── vector_store.py  # FAISS operations
│   │   └── generator.py     # Ollama LLM integration
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── app.component.ts
│   │   │   ├── app.component.html
│   │   │   ├── app.component.css
│   │   │   └── api.service.ts
│   │   └── environments/
│   ├── angular.json
│   ├── package.json
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Make sure Ollama is running locally
export OLLAMA_BASE_URL=http://localhost:11434
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
ng serve
```

## Performance

- **Latency**: 2-10 seconds per query depending on model and hardware
- **Accuracy**: High relevance for typical queries
- **Memory**: ~6GB RAM (2GB backend + 4GB Ollama)

## Troubleshooting

### "Cannot connect to Ollama"
- Ensure Ollama container is running: `docker ps`
- Check if model is pulled: `docker exec -it rag-ollama ollama list`

### Slow responses
- First query after startup may be slow (model loading)
- Consider using a smaller model like `tinyllama`

### Out of memory
- Reduce Ollama memory: edit `deploy.resources.reservations.memory` in docker-compose.yml
- Use a smaller model

## License

MIT License - fully open-source

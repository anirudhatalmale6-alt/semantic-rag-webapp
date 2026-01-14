"""
FastAPI application for the RAG web service.
"""
import os
import tempfile
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.config import DATA_DIR
from app.document_loader import load_document
from app.chunker import chunk_text
from app.vector_store import get_vector_store
from app.generator import get_generator


# Pydantic models for request/response
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


class SearchResult(BaseModel):
    text: str
    metadata: dict
    score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    answer: str


class IngestResponse(BaseModel):
    message: str
    filename: str
    chunks_added: int


class StatsResponse(BaseModel):
    total_documents: int
    embedding_dimension: int
    model_name: str


# Initialize FastAPI app
app = FastAPI(
    title="Semantic RAG API",
    description="Open-source RAG web application for semantic document search",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Semantic RAG API"}


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get vector store statistics."""
    store = get_vector_store()
    return store.get_stats()


@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    """
    Ingest a document (PDF, Markdown, or Text file).

    Accepts file upload, extracts text, chunks it, and adds to vector store.
    """
    # Validate file extension
    allowed_extensions = {'.pdf', '.md', '.markdown', '.txt', '.text'}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Supported: {allowed_extensions}"
        )

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Load and process document
        text, metadata = load_document(tmp_path)
        metadata["original_filename"] = file.filename

        # Chunk the document
        chunks = chunk_text(text, source=file.filename)

        # Add to vector store
        store = get_vector_store()
        chunks_added = store.add_chunks(chunks)

        return IngestResponse(
            message="Document ingested successfully",
            filename=file.filename,
            chunks_added=chunks_added
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up temp file
        os.unlink(tmp_path)


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search documents and generate an answer.

    Performs semantic search on ingested documents and generates
    an answer based on the retrieved passages.
    """
    store = get_vector_store()
    generator = get_generator()

    # Search for relevant passages
    results = store.search(request.query, top_k=request.top_k)

    # Generate answer
    answer = generator.generate(request.query, results)

    return SearchResponse(
        query=request.query,
        results=[SearchResult(**r) for r in results],
        answer=answer
    )


@app.post("/search/stream")
async def search_stream(request: SearchRequest):
    """
    Search documents and stream the generated answer.

    Returns results immediately, then streams the answer generation.
    """
    store = get_vector_store()
    generator = get_generator()

    # Search for relevant passages
    results = store.search(request.query, top_k=request.top_k)

    async def generate_stream():
        # First yield the search results as JSON
        import json
        yield json.dumps({"results": results}) + "\n---ANSWER---\n"

        # Then stream the answer
        for chunk in generator.generate_stream(request.query, results):
            yield chunk

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain"
    )


@app.delete("/clear")
async def clear_index():
    """Clear all documents from the vector store."""
    store = get_vector_store()
    store.clear()
    return {"message": "Index cleared successfully"}

"""
Configuration settings for the RAG application.
"""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", "/app/data"))
INDEX_DIR = Path(os.getenv("INDEX_DIR", "/app/index"))

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)

# Embedding model
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Chunking settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Search settings
TOP_K = int(os.getenv("TOP_K", "5"))

# Ollama settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

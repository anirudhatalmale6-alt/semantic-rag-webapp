"""
FAISS-based vector store for semantic search.
"""
import os
import json
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from app.config import INDEX_DIR, EMBEDDING_MODEL, TOP_K
from app.chunker import Chunk


class VectorStore:
    """
    FAISS vector store with sentence transformer embeddings.
    """

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """
        Initialize the vector store.

        Args:
            model_name: Name of the sentence transformer model
        """
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        self.index: Optional[faiss.IndexFlatIP] = None
        self.documents: List[Dict[str, Any]] = []
        self.index_path = INDEX_DIR / "faiss.index"
        self.docs_path = INDEX_DIR / "documents.pkl"

        # Load existing index if available
        self._load_index()

    def _load_index(self):
        """Load existing index from disk if available."""
        if self.index_path.exists() and self.docs_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            with open(self.docs_path, 'rb') as f:
                self.documents = pickle.load(f)
        else:
            # Create new index (Inner Product for cosine similarity with normalized vectors)
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self.documents = []

    def _save_index(self):
        """Save index to disk."""
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_path))
            with open(self.docs_path, 'wb') as f:
                pickle.dump(self.documents, f)

    def add_chunks(self, chunks: List[Chunk]) -> int:
        """
        Add chunks to the vector store.

        Args:
            chunks: List of Chunk objects to add

        Returns:
            Number of chunks added
        """
        if not chunks:
            return 0

        # Generate embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = self.model.encode(texts, normalize_embeddings=True)

        # Add to index
        self.index.add(np.array(embeddings).astype('float32'))

        # Store document data
        for chunk, embedding in zip(chunks, embeddings):
            self.documents.append({
                "text": chunk.text,
                "metadata": chunk.metadata,
                "chunk_index": chunk.chunk_index
            })

        # Persist to disk
        self._save_index()

        return len(chunks)

    def search(self, query: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Search query string
            top_k: Number of results to return

        Returns:
            List of matching documents with scores
        """
        if self.index is None or self.index.ntotal == 0:
            return []

        # Generate query embedding
        query_embedding = self.model.encode([query], normalize_embeddings=True)

        # Search
        scores, indices = self.index.search(
            np.array(query_embedding).astype('float32'),
            min(top_k, self.index.ntotal)
        )

        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:
                doc = self.documents[idx]
                results.append({
                    "text": doc["text"],
                    "metadata": doc["metadata"],
                    "score": float(score)
                })

        return results

    def clear(self):
        """Clear all documents from the index."""
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.documents = []
        self._save_index()

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "total_documents": len(self.documents),
            "embedding_dimension": self.embedding_dim,
            "model_name": EMBEDDING_MODEL
        }


# Global instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get or create the global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store

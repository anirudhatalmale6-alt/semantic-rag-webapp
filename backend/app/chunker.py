"""
Document chunking utilities for splitting documents into smaller passages.
"""
from typing import List, Dict, Any
from dataclasses import dataclass
from app.config import CHUNK_SIZE, CHUNK_OVERLAP


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    text: str
    metadata: Dict[str, Any]
    chunk_index: int


def chunk_text(
    text: str,
    source: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
) -> List[Chunk]:
    """
    Split text into overlapping chunks.

    Args:
        text: The full text to chunk
        source: Source identifier (filename, URL, etc.)
        chunk_size: Maximum characters per chunk
        overlap: Number of overlapping characters between chunks

    Returns:
        List of Chunk objects
    """
    if not text or not text.strip():
        return []

    # Clean the text
    text = text.strip()
    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):
        # Find the end of the chunk
        end = start + chunk_size

        # Try to break at a sentence or word boundary
        if end < len(text):
            # Look for sentence boundary (. ! ?)
            boundary = text.rfind('. ', start, end)
            if boundary == -1:
                boundary = text.rfind('! ', start, end)
            if boundary == -1:
                boundary = text.rfind('? ', start, end)
            if boundary == -1:
                # Fall back to word boundary
                boundary = text.rfind(' ', start, end)

            if boundary > start:
                end = boundary + 1

        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(Chunk(
                text=chunk_text,
                metadata={
                    "source": source,
                    "chunk_index": chunk_index,
                    "start_char": start,
                    "end_char": end
                },
                chunk_index=chunk_index
            ))
            chunk_index += 1

        # Move start position with overlap
        start = end - overlap if end < len(text) else end

        # Prevent infinite loop
        if start <= chunks[-1].metadata["start_char"] if chunks else 0:
            start = end

    return chunks

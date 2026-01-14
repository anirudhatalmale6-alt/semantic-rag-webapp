"""
Document loaders for various file formats (PDF, Markdown, Text).
"""
import os
from pathlib import Path
from typing import Tuple
import markdown
from PyPDF2 import PdfReader


def load_pdf(file_path: str) -> Tuple[str, dict]:
    """
    Extract text content from a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Tuple of (text content, metadata dict)
    """
    reader = PdfReader(file_path)
    text_parts = []

    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    return "\n\n".join(text_parts), {
        "file_type": "pdf",
        "page_count": len(reader.pages),
        "filename": os.path.basename(file_path)
    }


def load_markdown(file_path: str) -> Tuple[str, dict]:
    """
    Load and convert markdown file to plain text.

    Args:
        file_path: Path to the markdown file

    Returns:
        Tuple of (text content, metadata dict)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Convert markdown to HTML then strip tags for plain text
    html = markdown.markdown(content)
    # Simple tag stripping
    import re
    text = re.sub(r'<[^>]+>', '', html)

    return text, {
        "file_type": "markdown",
        "filename": os.path.basename(file_path)
    }


def load_text(file_path: str) -> Tuple[str, dict]:
    """
    Load plain text file.

    Args:
        file_path: Path to the text file

    Returns:
        Tuple of (text content, metadata dict)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return content, {
        "file_type": "text",
        "filename": os.path.basename(file_path)
    }


def load_document(file_path: str) -> Tuple[str, dict]:
    """
    Load document based on file extension.

    Args:
        file_path: Path to the document

    Returns:
        Tuple of (text content, metadata dict)

    Raises:
        ValueError: If file type is not supported
    """
    path = Path(file_path)
    extension = path.suffix.lower()

    loaders = {
        '.pdf': load_pdf,
        '.md': load_markdown,
        '.markdown': load_markdown,
        '.txt': load_text,
        '.text': load_text,
    }

    if extension not in loaders:
        raise ValueError(f"Unsupported file type: {extension}. Supported: {list(loaders.keys())}")

    return loaders[extension](file_path)

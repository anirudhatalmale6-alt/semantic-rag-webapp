"""
Answer generation using retrieved passages.
Uses Ollama for local LLM inference (Mistral, Llama2, etc.)
"""
import os
import httpx
from typing import List, Dict, Any, Generator, AsyncGenerator

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL


class AnswerGenerator:
    """
    Generate answers based on retrieved context using Ollama.
    """

    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        """
        Initialize the generator.

        Args:
            base_url: Ollama API base URL
            model: Model name (e.g., mistral, llama2, codellama)
        """
        self.base_url = base_url.rstrip('/')
        self.model = model

    def _build_prompt(self, query: str, passages: List[Dict[str, Any]]) -> str:
        """Build the prompt with context from retrieved passages."""
        if not passages:
            return f"Question: {query}\n\nAnswer: I don't have any documents to reference for this question."

        context_parts = []
        for i, passage in enumerate(passages[:5], 1):
            source = passage.get("metadata", {}).get("source", "Unknown")
            context_parts.append(f"[Source {i}: {source}]\n{passage['text']}")

        context = "\n\n".join(context_parts)

        return f"""You are a helpful assistant that answers questions based on the provided context.
Use only the information from the context to answer. If the answer cannot be found in the context, say so clearly.

Context:
{context}

Question: {query}

Answer:"""

    def generate(
        self,
        query: str,
        passages: List[Dict[str, Any]],
        max_tokens: int = 512
    ) -> str:
        """
        Generate an answer based on query and retrieved passages.

        Args:
            query: User's question
            passages: List of retrieved passages with text and metadata
            max_tokens: Maximum tokens in response

        Returns:
            Generated answer string
        """
        prompt = self._build_prompt(query, passages)

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": max_tokens,
                            "temperature": 0.7,
                        }
                    }
                )
                response.raise_for_status()
                return response.json().get("response", "Failed to generate response.")
        except httpx.ConnectError:
            return "Error: Cannot connect to Ollama. Please ensure Ollama is running."
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def generate_stream(
        self,
        query: str,
        passages: List[Dict[str, Any]],
        max_tokens: int = 512
    ) -> Generator[str, None, None]:
        """
        Generate answer with streaming output.

        Args:
            query: User's question
            passages: List of retrieved passages
            max_tokens: Maximum tokens in response

        Yields:
            Chunks of the generated answer
        """
        prompt = self._build_prompt(query, passages)

        try:
            with httpx.Client(timeout=120.0) as client:
                with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "num_predict": max_tokens,
                            "temperature": 0.7,
                        }
                    }
                ) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line:
                            import json
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                            if data.get("done", False):
                                break
        except httpx.ConnectError:
            yield "Error: Cannot connect to Ollama. Please ensure Ollama is running."
        except Exception as e:
            yield f"Error: {str(e)}"

    async def generate_stream_async(
        self,
        query: str,
        passages: List[Dict[str, Any]],
        max_tokens: int = 512
    ) -> AsyncGenerator[str, None]:
        """
        Async streaming generation for FastAPI StreamingResponse.

        Args:
            query: User's question
            passages: List of retrieved passages
            max_tokens: Maximum tokens in response

        Yields:
            Chunks of the generated answer
        """
        prompt = self._build_prompt(query, passages)

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "num_predict": max_tokens,
                            "temperature": 0.7,
                        }
                    }
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            import json
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                            if data.get("done", False):
                                break
        except httpx.ConnectError:
            yield "Error: Cannot connect to Ollama. Please ensure Ollama is running."
        except Exception as e:
            yield f"Error: {str(e)}"


# Global instance
_generator = None


def get_generator() -> AnswerGenerator:
    """Get or create the global generator instance."""
    global _generator
    if _generator is None:
        _generator = AnswerGenerator()
    return _generator

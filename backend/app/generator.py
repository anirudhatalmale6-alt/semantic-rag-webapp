"""
Answer generation using retrieved passages.
Uses Flan-T5 for open-source text generation.
"""
from typing import List, Dict, Any, Generator
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch

from app.config import GENERATION_MODEL


class AnswerGenerator:
    """
    Generate answers based on retrieved context using Flan-T5.
    """

    def __init__(self, model_name: str = GENERATION_MODEL):
        """
        Initialize the generator.

        Args:
            model_name: Name of the T5 model to use
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

    def generate(
        self,
        query: str,
        passages: List[Dict[str, Any]],
        max_length: int = 256
    ) -> str:
        """
        Generate an answer based on query and retrieved passages.

        Args:
            query: User's question
            passages: List of retrieved passages with text and metadata
            max_length: Maximum length of generated answer

        Returns:
            Generated answer string
        """
        if not passages:
            return "No relevant documents found to answer this question."

        # Build context from passages
        context_parts = []
        for i, passage in enumerate(passages[:5], 1):
            source = passage.get("metadata", {}).get("source", "Unknown")
            context_parts.append(f"[{i}] {passage['text']}")

        context = "\n\n".join(context_parts)

        # Create prompt for Flan-T5
        prompt = f"""Answer the question based on the following context. If the answer cannot be found in the context, say "I cannot find the answer in the provided documents."

Context:
{context}

Question: {query}

Answer:"""

        # Tokenize and generate
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=1024,
            truncation=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=3
            )

        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer

    def generate_stream(
        self,
        query: str,
        passages: List[Dict[str, Any]],
        max_length: int = 256
    ) -> Generator[str, None, None]:
        """
        Generate answer with streaming output.
        Note: True streaming requires more complex setup, this simulates it.

        Args:
            query: User's question
            passages: List of retrieved passages
            max_length: Maximum length of generated answer

        Yields:
            Chunks of the generated answer
        """
        # Generate full answer (Flan-T5 doesn't natively support streaming well)
        answer = self.generate(query, passages, max_length)

        # Simulate streaming by yielding words
        words = answer.split()
        for i, word in enumerate(words):
            if i > 0:
                yield " "
            yield word


# Global instance
_generator = None


def get_generator() -> AnswerGenerator:
    """Get or create the global generator instance."""
    global _generator
    if _generator is None:
        _generator = AnswerGenerator()
    return _generator

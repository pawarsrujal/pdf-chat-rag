"""
Embeddings service using SentenceTransformers.
"""

from typing import List
import asyncio
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Service for generating text embeddings using SentenceTransformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding service.

        Args:
            model_name: Name of the SentenceTransformer model to use.
        """
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to encode.

        Returns:
            List of embedding vectors.
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def encode_single(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to encode.

        Returns:
            Embedding vector.
        """
        embeddings = self.encode([text])
        return embeddings[0]
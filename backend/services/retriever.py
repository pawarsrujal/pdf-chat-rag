"""
Retriever service for Pinecone-based document retrieval.
"""

import logging
from typing import List, Tuple
from models.schemas import DocumentChunk
from db.pinecone_db import PineconeDatabase

logger = logging.getLogger(__name__)


class RetrieverService:
    """Service for retrieving relevant documents using Pinecone."""

    def __init__(self, pinecone_db: PineconeDatabase):
        """
        Initialize the retriever service.

        Args:
            pinecone_db: Pinecone database instance.
        """
        self.pinecone_db = pinecone_db

    def retrieve(self, query_embedding: List[float], top_k: int = 5, similarity_threshold: float = 0.5) -> Tuple[List[DocumentChunk], List[float]]:
        """
        Retrieve top-k relevant document chunks with similarity threshold filtering.

        Args:
            query_embedding: Query embedding vector.
            top_k: Number of top results to return.
            similarity_threshold: Minimum similarity score to include.

        Returns:
            Tuple of (chunks, scores) filtered and sorted.
        """
        import time
        start_time = time.time()
        
        # Retrieve more candidates for re-ranking
        candidates_k = min(top_k * 2, 50)  # Retrieve up to 50 for re-ranking
        results = self.pinecone_db.query(query_embedding, candidates_k)
        
        # Convert to DocumentChunk
        all_chunks = []
        all_scores = []
        for result in results:
            chunk = DocumentChunk(
                id=result["id"],
                document_id=result["metadata"]["document_id"],
                content=result["metadata"]["content"],
                metadata={
                    "filename": result["metadata"]["filename"],
                    "chunk_index": result["metadata"]["chunk_index"]
                },
                embedding=query_embedding  # Not needed, but schema requires
            )
            all_chunks.append(chunk)
            all_scores.append(result["score"])
        
        # Filter by threshold
        filtered_chunks = []
        filtered_scores = []
        for chunk, score in zip(all_chunks, all_scores):
            if score >= similarity_threshold:
                filtered_chunks.append(chunk)
                filtered_scores.append(score)
        
        # Re-rank: sort by score descending (already sorted by FAISS, but ensure)
        combined = sorted(zip(filtered_chunks, filtered_scores), key=lambda x: x[1], reverse=True)
        chunks, scores = zip(*combined) if combined else ([], [])
        
        # Take top_k
        chunks = list(chunks)[:top_k]
        scores = list(scores)[:top_k]
        
        latency = time.time() - start_time
        logger.info(f"Retrieval completed in {latency:.3f}s. Retrieved {len(chunks)} chunks with threshold {similarity_threshold}")
        for i, (chunk, score) in enumerate(zip(chunks, scores)):
            logger.debug(f"Chunk {i+1}: score={score:.3f}, doc={chunk.metadata.get('filename', 'unknown')}")
        
        return chunks, scores
"""
Pinecone database service.
"""

import os
from typing import List, Optional, Dict, Any
from pinecone import Pinecone
from models.schemas import DocumentChunk


class PineconeDatabase:
    def __init__(self):
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pc.Index(os.getenv("PINECONE_INDEX_NAME"))

    def upsert_chunks(self, chunks: List[DocumentChunk]):
        vectors = [
            {
                "id": chunk.id,
                "values": chunk.embedding,
                "metadata": chunk.metadata,
            }
            for chunk in chunks
        ]
        self.index.upsert(vectors=vectors)

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ):
        response = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter,
        )
        return response["matches"]

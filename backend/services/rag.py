"""
RAG (Retrieval-Augmented Generation) pipeline service.
"""

import logging
import time
from typing import List, Dict, Any, Optional
from models.schemas import DocumentChunk, ChatRequest, ChatResponse, Source
from services.embeddings import EmbeddingService
from services.retriever import RetrieverService
from services.llm import LLMService

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG pipeline combining retrieval and generation."""

    def __init__(self, embedding_service: EmbeddingService, db_service, llm_service: LLMService):
        """
        Initialize the RAG service.

        Args:
            embedding_service: Embedding service instance.
            db_service: Database service instance (Pinecone).
            llm_service: LLM service instance.
        """
        self.embedding_service = embedding_service
        self.db_service = db_service
        self.llm_service = llm_service
        self.conversation_memory: Dict[str, List[Dict[str, str]]] = {}

    def process_query(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat query using RAG with enhanced features.

        Args:
            request: Chat request with message and session info.

        Returns:
            Chat response with generated answer and sources.
        """
        start_time = time.time()
        session_id = request.session_id or self._generate_session_id()

        # Get or initialize conversation memory
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = []

        logger.info(f"Processing query for session {session_id}: {request.message[:100]}...")

        # Generate embedding for the query
        embed_start = time.time()
        query_embedding = self.embedding_service.encode_single(request.message)
        embed_time = time.time() - embed_start
        logger.debug(f"Embedding generated in {embed_time:.3f}s")

        # Retrieve relevant chunks with threshold
        retrieve_start = time.time()
        results = self.db_service.query(query_embedding, request.top_k)
        
        # Filter by threshold
        chunks = []
        scores = []
        for result in results:
            if result["score"] >= request.similarity_threshold:
                chunk = DocumentChunk(
                    id=result["id"],
                    document_id=result["metadata"]["document_id"],
                    content=result["metadata"]["content"],
                    metadata={
                        "filename": result["metadata"]["filename"],
                        "chunk_index": result["metadata"]["chunk_index"]
                    },
                    embedding=query_embedding
                )
                chunks.append(chunk)
                scores.append(result["score"])
        
        retrieve_time = time.time() - retrieve_start
        logger.info(f"Retrieved {len(chunks)} chunks in {retrieve_time:.3f}s")

        # Prepare context from retrieved chunks
        context_texts = [chunk.content for chunk in chunks]

        # Generate response using LLM
        llm_start = time.time()
        if context_texts:
            llm_result = self.llm_service.generate_response(
                request.message, 
                context_texts, 
                role=request.role
            )
            response_text = llm_result["response"]
            token_usage = llm_result["token_usage"]
        else:
            response_text = "I don't know based on the uploaded documents."
            token_usage = 0
        
        llm_time = time.time() - llm_start
        logger.info(f"LLM response generated in {llm_time:.3f}s, tokens: {token_usage}")

        # Update conversation memory
        self.conversation_memory[session_id].append({"role": "user", "content": request.message})
        self.conversation_memory[session_id].append({"role": "assistant", "content": response_text})

        # Prepare structured sources
        sources = []
        for chunk, score in zip(chunks, scores):
            source = Source(
                document_name=chunk.metadata.get("filename", "Unknown Document"),
                page_number=chunk.metadata.get("page_number"),
                content=chunk.content[:300] + "..." if len(chunk.content) > 300 else chunk.content,
                score=round(score, 3)
            )
            sources.append(source)

        total_time = time.time() - start_time
        logger.info(f"Query processed in {total_time:.3f}s total")

        return ChatResponse(
            response=response_text,
            sources=sources,
            session_id=session_id
        )

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        import uuid
        return str(uuid.uuid4())
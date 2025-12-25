"""
Pydantic models for the AI Research & Knowledge Assistant backend.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ----------------------------
# Auth / User Models
# ----------------------------

class UserCreate(BaseModel):
    """Model for user registration."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(
        ...,
        pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    )
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Model for user login."""
    username: str
    password: str


class Token(BaseModel):
    """Model for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Model for token data."""
    username: Optional[str] = None


# ----------------------------
# Document Upload Models
# ----------------------------

class DocumentUpload(BaseModel):
    """Model for document upload response."""
    id: str
    filename: str
    uploaded_at: datetime
    chunks_count: int


class DocumentChunk(BaseModel):
    """Model for document chunk with metadata."""
    id: str
    document_id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


# ----------------------------
# Chat / RAG Models
# ----------------------------

class ChatRequest(BaseModel):
    """Model for chat request."""
    message: str
    session_id: Optional[str] = None
    top_k: Optional[int] = Field(5, ge=1, le=20)
    similarity_threshold: Optional[float] = Field(0.5, ge=0.0, le=1.0)
    role: Optional[str] = Field(
        "researcher",
        description="User role: student, researcher, interview"
    )
    document_id: Optional[str] = None   # 🔒 REQUIRED FOR DOCUMENT FILTERING


class Source(BaseModel):
    """Model for source citation."""
    document_name: str
    page_number: Optional[int] = None
    content: str
    score: float


class ChatResponse(BaseModel):
    """Model for chat response."""
    response: str
    sources: List[Source] = []
    session_id: str


# ----------------------------
# Retrieval Models (Optional)
# ----------------------------

class RetrievalResult(BaseModel):
    """Model for retrieval result."""
    chunks: List[DocumentChunk]
    scores: List[float]

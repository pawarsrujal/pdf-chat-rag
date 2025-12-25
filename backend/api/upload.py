"""
Upload API – Single PDF per chat
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import asyncio, os
from datetime import datetime

from models.schemas import DocumentUpload, DocumentChunk
from utils.helpers import extract_text_from_file, chunk_text, clean_text, generate_unique_id

router = APIRouter(tags=["upload"])

_embedding_service = None
_pinecone_db = None

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# single PDF flag
pdf_uploaded = False


def get_embedding_service():
    global _embedding_service
    if _embedding_service is None:
        from services.embeddings import EmbeddingService
        _embedding_service = EmbeddingService()
    return _embedding_service


def get_pinecone_db():
    global _pinecone_db
    if _pinecone_db is None:
        from db.pinecone_db import PineconeDatabase
        _pinecone_db = PineconeDatabase()
    return _pinecone_db


@router.post("/upload", response_model=DocumentUpload)
async def upload_document(file: UploadFile = File(...)):
    global pdf_uploaded

    if pdf_uploaded:
        raise HTTPException(
            status_code=400,
            detail="A PDF is already uploaded. Please reset chat before uploading a new file."
        )

    file_path = None
    try:
        content = await file.read()
        document_id = generate_unique_id()

        file_path = UPLOAD_DIR / f"{document_id}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(content)

        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(
            None, extract_text_from_file, file.filename, content
        )

        text = clean_text(text)
        if not text.strip():
            raise HTTPException(status_code=400, detail="No readable text found")

        chunks = chunk_text(text, chunk_size=500, overlap=100)

        embeddings = await loop.run_in_executor(
            None, get_embedding_service().encode, chunks
        )

        pinecone_db = get_pinecone_db()
        vectors = []

        for chunk_text_, vector in zip(chunks, embeddings):
            vectors.append(
                DocumentChunk(
                    id=generate_unique_id(),
                    document_id=document_id,
                    content=chunk_text_,
                    metadata={
                        "content": chunk_text_
                    },
                    embedding=vector
                )
            )

        pinecone_db.upsert_chunks(vectors)

        pdf_uploaded = True

        return DocumentUpload(
            id=document_id,
            filename=file.filename,
            uploaded_at=datetime.utcnow(),
            chunks_count=len(chunks)
        )

    finally:
        if file_path and file_path.exists():
            os.remove(file_path)

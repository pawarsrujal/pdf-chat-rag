"""
Chat API – Single PDF RAG (Stable, Safe & Summary-Aware)
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os
import logging
from models.schemas import ChatRequest, ChatResponse, Source

router = APIRouter(tags=["chat"])
logger = logging.getLogger(__name__)

_embedding_service = None
_pinecone_db = None
_llm_service = None

# 🔒 Safety limit to avoid huge prompts
MAX_CONTEXT_CHARS = 2500


# -------------------------------------------------
# Lazy loaders (important for low RAM & Windows)
# -------------------------------------------------
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


def get_llm_service():
    global _llm_service
    if _llm_service is None:
        from services.llm import LLMService
        _llm_service = LLMService(api_key=os.getenv("GROQ_API_KEY", ""))
    return _llm_service


# -------------------------------------------------
# CHAT ENDPOINT
# -------------------------------------------------
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    pinecone_db = get_pinecone_db()
    llm = get_llm_service()
    embedding_service = get_embedding_service()

    # 1️⃣ Embed user query
    query_embedding = embedding_service.encode([request.message])[0]

    # 🔍 Detect summary-style queries
    summary_mode = any(
        word in request.message.lower()
        for word in ["summarize", "summary", "overview", "brief"]
    )

    top_k = 30 if summary_mode else 10

    # 2️⃣ Retrieve chunks from Pinecone
    matches = pinecone_db.query(
        query_embedding=query_embedding,
        top_k=top_k
    )

    # 🔍 DEBUG (VERY IMPORTANT)
    print("🔍 MATCH SAMPLE:", matches[:1])

    if not matches:
        return ChatResponse(
            response="No document uploaded yet.",
            sources=[],
            session_id="chat"
        )

    # 3️⃣ Build SAFE context
    context = ""
    current_len = 0
    sources = []

    max_context_chars = 8000 if summary_mode else MAX_CONTEXT_CHARS

    for match in matches:
        metadata = match.get("metadata") or {}
        text = metadata.get("content") or ""

        if not text:
            continue

        remaining_budget = max_context_chars - current_len

        if remaining_budget <= 0:
            break

        if len(text) > remaining_budget:
            text = text[:remaining_budget]

        context += text + "\n\n"
        current_len += len(text)

        sources.append(
            Source(
                document_name=metadata.get("filename", "uploaded_document"),
                content=text[:300],
                score=round(match.get("score", 0.0), 3)
            )
        )

    # 4️⃣ STRICT RAG PROMPT
    prompt = f"""
Answer the question using ONLY the information below.
If the answer is not present, say exactly:
"I don't know based on the uploaded document."

Context:
{context}

Question:
{request.message}

Instructions:
- Answer in complete sentences
- If summarizing, use bullet points
"""

    # 5️⃣ Generate answer
    answer = llm.generate(prompt)

    return ChatResponse(
        response=answer,
        sources=sources,
        session_id="chat"
    )


# -------------------------------------------------
# RESET CHAT (Single-PDF SAFETY)
# -------------------------------------------------
@router.post("/reset-chat")
def reset_chat():
    from db.pinecone_db import PineconeDatabase
    import api.upload  # reset upload flag

    db = PineconeDatabase()

    try:
        db.index.delete(delete_all=True)
    except Exception as e:
        logger.error("Pinecone reset failed", exc_info=e)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

    api.upload.pdf_uploaded = False

    return {"status": "chat reset"}

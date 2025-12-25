"""
Chat API – Single PDF RAG (Stable & Safe)
"""

from fastapi import APIRouter
import os
from models.schemas import ChatRequest, ChatResponse, Source

router = APIRouter(tags=["chat"])

_embedding_service = None
_pinecone_db = None
_llm_service = None

# 🔒 Safety limit to avoid huge prompts
MAX_CONTEXT_CHARS = 2500


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

    # 2️⃣ Retrieve chunks
    matches = pinecone_db.query(
        query_embedding=query_embedding,
        top_k=10
    )

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

    for match in matches:
        text = match.get("metadata", {}).get("content", "")
        if not text:
            continue

        if current_len + len(text) > MAX_CONTEXT_CHARS:
            break

        context += text + "\n\n"
        current_len += len(text)

        sources.append(
            Source(
                document_name="uploaded_document",
                content=text[:300],
                score=round(match.get("score", 0.0), 3)
            )
        )

    if not context.strip():
        return ChatResponse(
            response="I don't know based on the uploaded document.",
            sources=[],
            session_id="chat"
        )

    # 4️⃣ Build prompt (STRICT RAG)
    prompt = f"""
Answer the question using ONLY the information below.
If the answer is not present, say:
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
# RESET CHAT (VERY IMPORTANT)
# -------------------------------------------------
@router.post("/reset-chat")
def reset_chat():
    from db.pinecone_db import PineconeDatabase
    import api.upload  # to reset upload flag

    # Delete all vectors
    PineconeDatabase().index.delete(delete_all=True)

    # Reset upload state
    api.upload.pdf_uploaded = False

    return {"status": "chat reset"}

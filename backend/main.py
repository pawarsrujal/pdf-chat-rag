"""
Main FastAPI application for AI Research & Knowledge Assistant.
"""

print("✅ FastAPI app loading")

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.auth import router as auth_router
from api.upload import router as upload_router
from api.chat import router as chat_router

import os
import asyncio



# Configuration
PORT = int(os.getenv("PORT", 8000))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
origins = ALLOWED_ORIGINS.split(",") if ALLOWED_ORIGINS != "*" else ["*"]

app = FastAPI(
    title="AI Research & Knowledge Assistant",
    description="A RAG-based assistant for document analysis and Q&A",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

# Include routers
# app.include_router(auth_router, tags=["auth"])
app.include_router(upload_router, tags=["upload"])
app.include_router(chat_router, tags=["chat"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Research & Knowledge Assistant API"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/ping")
def ping():
    return {"ok": True}

@app.get("/cors-test")
def cors_test():
    return {"status": "cors ok"}


print("✅ FastAPI app ready")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=PORT)
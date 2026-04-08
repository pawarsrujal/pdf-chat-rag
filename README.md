
# 🧠 AI Research & Knowledge Assistant

An intelligent, hallucination-safe document Q&A system powered by **Retrieval-Augmented Generation (RAG)**.  
Upload any PDF or DOCX file and ask questions — the AI answers strictly from your document, never from guesswork.

> **"If it's not in the document, the AI won't pretend it is."**

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 Document Upload | Supports PDF and DOCX formats |
| 🔍 Semantic Search | Pinecone vector DB for context-aware retrieval |
| 🧠 LLM-Powered Answers | Groq / LLaMA for fast, intelligent responses |
| 🧪 OCR Fallback | Tesseract handles scanned or image-based PDFs |
| 📌 Source Attribution | Answers include confidence scores and source references |
| 🛡️ Hallucination-Safe | Explicitly says *"I don't know"* when info isn't in the doc |
| 🎯 Summary-Aware Retrieval | Handles long documents intelligently |
| 🔄 Session Reset | Easily clear context and upload a new document |

---

## 🏗️ Architecture


User
 │
 ▼
Frontend (Next.js + TypeScript)
 │  REST API
 ▼
Backend (FastAPI + Python)
 │  Embedding Generation
 ▼
Pinecone Vector Database
 │  Semantic Retrieval
 ▼
LLM — Groq / LLaMA
 │
 ▼
Grounded, Citation-Backed Answer



## 🧩 Tech Stack

**Frontend**
- Next.js (React) · TypeScript · Tailwind CSS

**Backend**
- FastAPI · Python 3.10+ · pdfplumber · pytesseract · pdf2image

**AI & Storage**
- Pinecone Vector DB · Groq LLM · LLaMA · Sentence Embeddings

---

## 📂 Project Structure


ai-research-assistant/
│
├── backend/
│   ├── api/
│   │   ├── chat.py            # Chat endpoint
│   │   └── upload.py          # Document ingestion endpoint
│   ├── db/
│   │   └── pinecone_db.py     # Vector DB operations
│   ├── services/
│   │   ├── embeddings.py      # Embedding generation
│   │   └── llm.py             # LLM interaction & prompt logic
│   ├── utils/
│   │   └── helpers.py         # OCR, parsing utilities
│   └── main.py                # FastAPI app entry point
│
└── frontend/
    ├── pages/
    │   ├── index.tsx           # Landing page
    │   └── chat.tsx            # Chat interface
    ├── components/
    │   ├── ChatMessage.tsx     # Message bubble component
    │   └── FileUpload.tsx      # Drag-and-drop uploader
    └── services/
        └── api.ts              # API call handlers






## 🔄 How It Works

1. **Upload** — User uploads a PDF or DOCX document
2. **Parse & Chunk** — Document is extracted (with OCR fallback) and split into semantic chunks
3. **Embed** — Chunks are converted to vector embeddings and stored in Pinecone
4. **Query** — User asks a question; the query is embedded and matched against stored vectors
5. **Retrieve & Generate** — Top-k relevant chunks are passed to the LLM with a strict grounding prompt
6. **Respond** — The LLM returns a cited, confidence-scored answer — or says *"I don't know"*

---

## 🎯 Use Cases

- Academic paper analysis
- Legal document Q&A
- Technical manual search
- Corporate report summarization
- Medical document review

---

## 🚀 Future Roadmap

- [ ] Multi-document support with cross-document reasoning
- [ ] Chat history persistence
- [ ] Fine-tuned domain-specific embeddings
- [ ] REST API public access with rate limiting
- [ ] Support for Excel, PowerPoint, and web URLs

---

## 🛠️ Requirements


Python >= 3.10
Node.js >= 18
```





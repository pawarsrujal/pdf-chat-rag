# 🧠 RAG Document Chat Assistant

**An intelligent, hallucination-safe document Q&A system powered by Retrieval-Augmented Generation (RAG).**

Upload a PDF or DOCX file and ask questions about it — the AI answers strictly from your document, never from guesswork.

> *"If it's not in the document, the AI won't pretend it is."*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-React-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Table of Contents

- [Features](#-features)
- [Architecture](#️-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Running with Docker](#-running-with-docker)
- [Deployment](#-deployment)
- [Use Cases](#-use-cases)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 Document Upload | Supports PDF and DOCX formats |
| 🔍 Semantic Search | Pinecone vector DB for context-aware retrieval |
| 🧠 LLM-Powered Answers | Groq / LLaMA for fast, intelligent responses |
| 🧪 OCR Fallback | Tesseract handles scanned or image-based PDFs |
| 📌 Source Attribution | Answers include confidence scores and source references |
| 🛡️ Hallucination-Safe | Explicitly says *"I don't know"* when info isn't in the document |
| 🎯 Summary-Aware Retrieval | Handles long documents intelligently |
| 🔄 Session Reset | Easily clear context and upload a new document |

---

## 🏗️ Architecture

```
                     ┌─────────────┐
                     │    User     │
                     └──────┬──────┘
                            │
                            ▼
           ┌─────────────────────────────────┐
           │  Frontend (Next.js + TypeScript) │
           └────────────────┬─────────────────┘
                             │ REST API
                             ▼
           ┌─────────────────────────────────┐
           │   Backend (FastAPI + Python)     │
           └────────────────┬─────────────────┘
                             │ Embedding Generation
                             ▼
           ┌─────────────────────────────────┐
           │      Pinecone Vector Database     │
           └────────────────┬─────────────────┘
                             │ Semantic Retrieval
                             ▼
           ┌─────────────────────────────────┐
           │         LLM — Groq / LLaMA       │
           └────────────────┬─────────────────┘
                             │
                             ▼
              Grounded, Citation-Backed Answer
```

---

## 🧩 Tech Stack

**Frontend**
- Next.js (React) · TypeScript · Tailwind CSS

**Backend**
- FastAPI · Python 3.10+ · pdfplumber · pytesseract · pdf2image

**AI & Storage**
- Pinecone Vector DB · Groq LLM · LLaMA · Sentence Embeddings

**Infrastructure**
- Docker · Render (backend) · Vercel (frontend)

---

## 📂 Project Structure

```
rag-document-chat-assistant/
│
├── backend/
│   ├── api/
│   │   ├── chat.py            # Chat endpoint
│   │   └── upload.py          # Document ingestion endpoint
│   │
│   ├── db/
│   │   └── pinecone_db.py     # Vector DB operations
│   │
│   ├── services/
│   │   ├── embeddings.py      # Embedding generation
│   │   └── llm.py             # LLM interaction & prompt logic
│   │
│   ├── utils/
│   │   └── helpers.py         # OCR, parsing utilities
│   │
│   └── main.py                # FastAPI app entry point
│
├── frontend/
│   ├── pages/
│   │   ├── index.tsx          # Landing page
│   │   └── chat.tsx           # Chat interface
│   │
│   ├── components/
│   │   ├── ChatMessage.tsx    # Message bubble component
│   │   └── FileUpload.tsx     # Drag-and-drop uploader
│   │
│   └── services/
│       └── api.ts             # API call handlers
│
├── docker/                    # Dockerfiles for backend/frontend
├── docker-compose.yml         # Local multi-container setup
├── render.yaml                # Render deployment config (backend)
└── vercel.json                # Vercel deployment config (frontend)
```

---

## 🔄 How It Works

1. **Upload** — User uploads a PDF or DOCX document.
2. **Parse & Chunk** — The document is extracted (with OCR fallback for scanned pages) and split into semantic chunks.
3. **Embed** — Chunks are converted into vector embeddings and stored in Pinecone.
4. **Query** — The user asks a question; the query is embedded and matched against stored vectors.
5. **Retrieve & Generate** — The top-k relevant chunks are passed to the LLM with a strict grounding prompt.
6. **Respond** — The LLM returns a cited, confidence-scored answer — or honestly says *"I don't know."*

---

## 🚀 Getting Started

### Prerequisites

- Python **3.10+**
- Node.js **18+**
- A [Pinecone](https://www.pinecone.io/) account and API key
- A [Groq](https://console.groq.com/) API key
- Tesseract OCR installed locally (for scanned-PDF support)

### 1. Clone the repository

```bash
git clone https://github.com/MrunalNikam17/rag-document-chat-assistant.git
cd rag-document-chat-assistant
```

### 2. Backend setup

```bash
cd backend
python -m venv venv

# Activate the virtual environment
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows

pip install -r requirements.txt

# Create a .env file (see Environment Variables below)
cp .env.example .env

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`.

### 3. Frontend setup

```bash
cd frontend
npm install

# Create a .env.local file pointing to your backend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

npm run dev
```

Frontend will be available at `http://localhost:3000`.

---

## 🔐 Environment Variables

Create a `.env` file inside `backend/` with the following keys:

```env
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_pinecone_index_name
PINECONE_ENVIRONMENT=your_pinecone_environment
```

And a `.env.local` file inside `frontend/`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

> ⚠️ Never commit your `.env` files. Make sure they're listed in `.gitignore`.

---

## 🐳 Running with Docker

The fastest way to spin up the full stack (backend + frontend) is with Docker Compose:

```bash
docker-compose up --build
```

This will build and start both services as defined in `docker-compose.yml`. Once running:

- Frontend → `http://localhost:3000`
- Backend API → `http://localhost:8000`

---

## ☁️ Deployment

This project ships with ready-made configs for a split deployment:

- **Backend** → deployed via [Render](https://render.com/) using `render.yaml`
- **Frontend** → deployed via [Vercel](https://vercel.com/) using `vercel.json`

Steps:
1. Push your fork to GitHub.
2. Connect the repo to Render and deploy the backend service (set the environment variables from above in the Render dashboard).
3. Connect the repo to Vercel and deploy the `frontend/` directory, setting `NEXT_PUBLIC_API_URL` to your Render backend URL.

---

## 🎯 Use Cases

- Academic paper analysis
- Legal document Q&A
- Technical manual search
- Corporate report summarization
- Medical document review

---

## 🗺️ Roadmap

- [ ] Multi-document support with cross-document reasoning
- [ ] Chat history persistence
- [ ] Fine-tuned domain-specific embeddings
- [ ] Public REST API access with rate limiting
- [ ] Support for Excel, PowerPoint, and web URLs

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---


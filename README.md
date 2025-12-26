
# AI Research & Knowledge Assistant
🧠 AI Research Assistant 
An AI-powered Research Assistant that allows users to upload documents (PDF/DOCX) and ask questions strictly based on the uploaded content using Retrieval-Augmented Generation (RAG).

The system is designed to be hallucination-safe, meaning the AI only answers if the information exists in the document, otherwise it explicitly says “I don't know based on the uploaded document.”

🚀 Features

📄 Upload PDF / DOCX documents

🔍 Semantic search using Pinecone Vector Database

🧠 Context-aware answers using LLM (Groq / LLaMA)

🧪 OCR fallback for scanned PDFs (Tesseract)

📌 Source attribution with confidence scores

🔄 Reset chat to upload a new document

🎯 Summary-aware retrieval for long documents

🛡️ Strict RAG (No hallucinations)

🏗️ System Architecture
Frontend (Next.js)
        |
        |  REST API
        v
Backend (FastAPI)
        |
        |  Embeddings
        v
Pinecone Vector DB
        |
        v
LLM (Groq / LLaMA)

🧩 Tech Stack
Frontend

Next.js (React)

TypeScript

Tailwind CSS

Backend

FastAPI

Python 3.10+

Pinecone

Groq LLM

pdfplumber

pytesseract (OCR)

pdf2image

📂 Project Structure
ai-research-assistant/
│
├── backend/
│   ├── api/
│   │   ├── chat.py
│   │   └── upload.py
│   ├── db/
│   │   └── pinecone_db.py
│   ├── services/
│   │   ├── embeddings.py
│   │   └── llm.py
│   ├── utils/
│   │   └── helpers.py
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── pages/
│   │   ├── index.tsx
│   │   └── chat.tsx
│   ├── components/
│   │   ├── ChatMessage.tsx
│   │   └── FileUpload.tsx
│   ├── services/
│   │   └── api.ts
│   └── package.json

⚙️ Environment Variables

Create a .env file inside backend/:

GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_index_name


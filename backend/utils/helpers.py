"""
Utility helper functions for document processing.
"""

import re
import uuid
from typing import List
from pdf2image import convert_from_bytes
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"



# -------------------------------------------------
# ID generator
# -------------------------------------------------
def generate_unique_id() -> str:
    return str(uuid.uuid4())


# -------------------------------------------------
# Text cleaning (CRITICAL FIX HERE)
# -------------------------------------------------
def clean_text(text: str) -> str:
    """
    Clean extracted text and fix common PDF encoding issues.
    """

    if not text:
        return ""

    # 🔒 Fix common UTF-8 / PDF encoding issues
    replacements = {
        "â¢": "•",
        "â€“": "-",
        "â€”": "-",
        "â€œ": '"',
        "â€�": '"',
        "â€™": "'",
        "â€˜": "'",
        "â€¦": "...",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Remove null chars
    text = text.replace("\x00", " ")

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# -------------------------------------------------
# Chunking
# -------------------------------------------------
def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> List[str]:
    """
    Split text into overlapping chunks.
    """

    if not text:
        return []

    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = words[start:end]
        chunks.append(" ".join(chunk))
        start = end - overlap

        if start < 0:
            start = 0

    return chunks


# -------------------------------------------------
# Text extraction dispatcher
# -------------------------------------------------
def extract_text_from_file(filename: str, content: bytes) -> str:
    """
    Extract text from supported file types.
    """

    ext = filename.lower().split(".")[-1]

    if ext == "pdf":
        return extract_text_from_pdf(content)
    elif ext in {"txt"}:
        return content.decode(errors="ignore")
    elif ext in {"docx", "doc"}:
        return extract_text_from_docx(content)
    else:
        return ""


# -------------------------------------------------
# PDF extraction
# -------------------------------------------------
def extract_text_from_pdf(content: bytes) -> str:
    """
    PDF extraction with OCR fallback for scanned / resume PDFs.
    """

    from io import BytesIO
    import pdfplumber

    # 1️⃣ Try normal PDF text extraction
    text = ""
    with pdfplumber.open(BytesIO(content)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # 2️⃣ OCR fallback if text is too small
    if len(text.strip()) < 200:
        print("⚠️ Low PDF text detected, using OCR fallback")
        images = convert_from_bytes(content)

        ocr_text = ""
        for img in images:
            ocr_text += pytesseract.image_to_string(img) + "\n"

        print("🧠 OCR extracted chars:", len(ocr_text))
        return ocr_text

    return text


# -------------------------------------------------
# DOCX extraction
# -------------------------------------------------
def extract_text_from_docx(content: bytes) -> str:
    from io import BytesIO
    from docx import Document

    doc = Document(BytesIO(content))
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs)

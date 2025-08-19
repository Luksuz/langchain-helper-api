from __future__ import annotations

import base64
import io
import os
from typing import Tuple

import docx2txt
from pypdf import PdfReader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredFileLoader


def _decode_base64_to_bytes(file_base64: str) -> bytes:
    return base64.b64decode(file_base64)


def extract_text_from_pdf_native(file_bytes: bytes) -> str:
    """Extract text from PDF without OCR using pypdf."""
    print(f"[EXTRACT_PDF] Starting PDF extraction, file size: {len(file_bytes)} bytes")
    text_parts = []
    reader = PdfReader(io.BytesIO(file_bytes))
    print(f"[EXTRACT_PDF] PDF has {len(reader.pages)} pages")
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        if page_text:
            text_parts.append(page_text)
            print(f"[EXTRACT_PDF] Page {i+1}: extracted {len(page_text)} characters")
        else:
            print(f"[EXTRACT_PDF] Page {i+1}: no text found")
    result = "\n".join(text_parts)
    print(f"[EXTRACT_PDF] Total extracted text: {len(result)} characters")
    return result


def extract_text_from_docx_native(file_bytes: bytes) -> str:
    """Extract text from DOCX using docx2txt."""
    print(f"[EXTRACT_DOCX] Starting DOCX extraction, file size: {len(file_bytes)} bytes")
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=True) as tmp:
        print(f"[EXTRACT_DOCX] Writing to temporary file: {tmp.name}")
        tmp.write(file_bytes)
        tmp.flush()
        print(f"[EXTRACT_DOCX] Processing DOCX file...")
        docx_text = docx2txt.process(tmp.name) or ""
        print(f"[EXTRACT_DOCX] Extracted {len(docx_text)} characters")
    return docx_text


def extract_text_with_langchain_pdf(file_bytes: bytes) -> str:
    """Use LangChain's PyPDFLoader for parsing; still non-OCR."""
    print(f"[EXTRACT_LANGCHAIN] Starting LangChain PDF extraction, file size: {len(file_bytes)} bytes")
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp:
        print(f"[EXTRACT_LANGCHAIN] Writing to temporary file: {tmp.name}")
        tmp.write(file_bytes)
        tmp.flush()
        print(f"[EXTRACT_LANGCHAIN] Loading PDF with PyPDFLoader...")
        docs = PyPDFLoader(tmp.name).load()
        print(f"[EXTRACT_LANGCHAIN] Loaded {len(docs)} document pages")
        for i, doc in enumerate(docs):
            print(f"[EXTRACT_LANGCHAIN] Page {i+1}: {len(doc.page_content)} characters")
    result = "\n\n".join(doc.page_content for doc in docs)
    print(f"[EXTRACT_LANGCHAIN] Total extracted text: {len(result)} characters")
    return result


def extract_text(file_base64: str, filename: str, use_langchain: bool = True) -> Tuple[str, str]:
    """Dispatch extraction based on file extension. Returns (text, method)."""
    print(f"[EXTRACT] Starting text extraction for: {filename}")
    print(f"[EXTRACT] Use LangChain: {use_langchain}")
    
    lower = filename.lower()
    print(f"[EXTRACT] File extension detected: {lower.split('.')[-1] if '.' in lower else 'none'}")
    
    file_bytes = _decode_base64_to_bytes(file_base64)
    print(f"[EXTRACT] Decoded file size: {len(file_bytes)} bytes")
    
    if lower.endswith(".pdf"):
        print(f"[EXTRACT] Processing as PDF file")
        if use_langchain:
            result, method = extract_text_with_langchain_pdf(file_bytes), "langchain_pypdf"
        else:
            result, method = extract_text_from_pdf_native(file_bytes), "pypdf"
        print(f"[EXTRACT] PDF extraction completed using {method}")
        return result, method
        
    if lower.endswith(".docx"):
        print(f"[EXTRACT] Processing as DOCX file")
        result, method = extract_text_from_docx_native(file_bytes), "docx2txt"
        print(f"[EXTRACT] DOCX extraction completed using {method}")
        return result, method
        
    print(f"[EXTRACT] Unsupported file type: {filename}")
    raise ValueError("Unsupported file type. Only .pdf and .docx are supported.")



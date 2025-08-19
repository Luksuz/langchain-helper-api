from __future__ import annotations

import base64
import io
import os
from dataclasses import dataclass
from typing import List, Tuple

from sqlalchemy import create_engine, text
from sqlalchemy import text as sql_text
from sqlalchemy.engine import Engine
from pgvector.sqlalchemy import Vector

from ..service.text_extraction_service import extract_text
from ..utils.schema_builder import build_pydantic_model
from langchain_openai import OpenAIEmbeddings


@dataclass
class Chunk:
    session_id: str
    filename: str
    chunk_id: int
    text: str


def get_engine() -> Engine:
    url = os.environ.get("PGVECTOR_URL") or "postgresql+psycopg://user:pass@pgvector-production-819e.up.railway.app:5432/db"
    return create_engine(url)


def ensure_schema(engine: Engine) -> None:
    with engine.begin() as conn:
        # Ensure pgvector extension exists (if privileges allow)
        try:
            conn.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector;"))
        except Exception:
            # Ignore if extension creation is not permitted by the role
            pass
        conn.execute(sql_text(
            """
            CREATE TABLE IF NOT EXISTS doc_chunks (
              session_id UUID NOT NULL,
              filename TEXT NOT NULL,
              chunk_id INT NOT NULL,
              content TEXT NOT NULL,
              embedding vector(1536),
              PRIMARY KEY (session_id, filename, chunk_id)
            );
            """
        ))


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    print(f"[CHUNK] Starting chunking for text of length: {len(text)}")
    words = text.split()
    print(f"[CHUNK] Split into {len(words)} words")
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i+chunk_size]
        if not chunk_words:
            break
        chunks.append(" ".join(chunk_words))
        i += chunk_size - overlap
        if i <= 0:
            break
    print(f"[CHUNK] Created {len(chunks)} chunks")
    return chunks


def embed_texts(texts: List[str]) -> List[List[float]]:
    print(f"[EMBED] Creating embeddings for {len(texts)} text chunks")
    embedder = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.environ.get("OPENAI_API_KEY"))
    print(f"[EMBED] Calling OpenAI API...")
    embeddings = embedder.embed_documents(texts)
    print(f"[EMBED] Received {len(embeddings)} embeddings, each with {len(embeddings[0]) if embeddings else 0} dimensions")
    return embeddings


def ingest_files(session_id: str, files: List[Tuple[str, str]], raw_texts: List[Tuple[str, str]] | None = None) -> int:
    """files: list of (filename, file_base64); raw_texts: list of (name, text)"""
    print(f"[INGEST] Starting ingestion for session: {session_id}")
    print(f"[INGEST] Files to process: {len(files)}")
    print(f"[INGEST] Raw texts to process: {len(raw_texts or [])}")
    
    engine = get_engine()
    print(f"[INGEST] Database engine created")
    ensure_schema(engine)
    print(f"[INGEST] Database schema ensured")

    total_chunks = 0
    with engine.begin() as conn:
        print(f"[INGEST] Database transaction started")
        
        # Process files
        for i, (filename, file_b64) in enumerate(files):
            print(f"[INGEST] Processing file {i+1}/{len(files)}: {filename}")
            print(f"[INGEST] File base64 length: {len(file_b64)}")
            
            extracted_text, method = extract_text(file_b64, filename, use_langchain=True)
            print(f"[INGEST] Text extracted using {method}, length: {len(extracted_text)}")

            chunks = chunk_text(extracted_text)
            if not chunks:
                print(f"[INGEST] No chunks created for {filename}, skipping")
                continue
                
            embeddings = embed_texts(chunks)
            print(f"[INGEST] Storing {len(embeddings)} chunks for {filename}")
            
            for idx, (chunk, vec) in enumerate(zip(chunks, embeddings)):
                conn.execute(
                    text("INSERT INTO doc_chunks(session_id, filename, chunk_id, content, embedding) VALUES (:sid, :fn, :cid, :ct, :emb) ON CONFLICT (session_id, filename, chunk_id) DO UPDATE SET content = EXCLUDED.content, embedding = EXCLUDED.embedding"),
                    {"sid": session_id, "fn": filename, "cid": idx, "ct": chunk, "emb": vec},
                )
                total_chunks += 1
            print(f"[INGEST] Stored {len(chunks)} chunks for {filename}")
            
        # Process raw texts
        print(f"[INGEST] Processing {len(raw_texts or [])} raw texts")
        for i, (name, content) in enumerate(raw_texts or []):
            print(f"[INGEST] Processing raw text {i+1}/{len(raw_texts)}: {name} (length: {len(content)})")
            
            chunks = chunk_text(content)
            if not chunks:
                print(f"[INGEST] No chunks created for raw text {name}, skipping")
                continue
                
            embeddings = embed_texts(chunks)
            print(f"[INGEST] Storing {len(embeddings)} chunks for raw text {name}")
            
            for idx, (chunk, vec) in enumerate(zip(chunks, embeddings)):
                conn.execute(
                    text("INSERT INTO doc_chunks(session_id, filename, chunk_id, content, embedding) VALUES (:sid, :fn, :cid, :ct, :emb) ON CONFLICT (session_id, filename, chunk_id) DO UPDATE SET content = EXCLUDED.content, embedding = EXCLUDED.embedding"),
                    {"sid": session_id, "fn": name, "cid": idx, "ct": chunk, "emb": vec},
                )
                total_chunks += 1
            print(f"[INGEST] Stored {len(chunks)} chunks for raw text {name}")
            
        print(f"[INGEST] Transaction committing with {total_chunks} total chunks")
    print(f"[INGEST] Ingestion completed successfully, total chunks: {total_chunks}")
    return total_chunks


def search(session_id: str, query: str, top_k: int = 15) -> List[Tuple[str, int, str, float]]:
    print(f"[SEARCH] Starting search for session: {session_id}")
    print(f"[SEARCH] Query: {query}")
    print(f"[SEARCH] Top K: {top_k}")
    
    engine = get_engine()
    ensure_schema(engine)
    
    print(f"[SEARCH] Generating embedding for query...")
    q_emb = embed_texts([query])[0]
    print(f"[SEARCH] Query embedding generated with {len(q_emb)} dimensions")
    
    with engine.begin() as conn:
        print(f"[SEARCH] Executing similarity search...")
        # Use CAST function instead of :: syntax to avoid parameter conflicts
        rows = conn.execute(
            text("SELECT filename, chunk_id, content, (embedding <#> CAST(:q AS vector)) AS distance FROM doc_chunks WHERE session_id = :sid ORDER BY embedding <#> CAST(:q AS vector) ASC LIMIT :k"),
            {"sid": session_id, "q": str(q_emb), "k": top_k},
        ).fetchall()
        print(f"[SEARCH] Found {len(rows)} results")
    
    results = [(r[0], r[1], r[2], float(r[3])) for r in rows]
    print(f"[SEARCH] Search completed successfully")
    return results



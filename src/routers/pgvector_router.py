from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..api_models.ingest_request import IngestRequest
from ..api_models.chat_request import ChatRequest
from ..service.pgvector_service import ingest_files, search
from ..ai_models.openai_model import get_openai_chat_model

router = APIRouter()


@router.post("/ingest")
def post_ingest(body: IngestRequest) -> JSONResponse:
    try:
        print(f"[ROUTER] Starting ingestion for session_id: {body.session_id}")
        files = [(f.filename, f.file_base64) for f in body.files]
        print(f"[ROUTER] Processing {len(files)} files: {[f[0] for f in files]}")
        
        # Convert raw_texts from List[dict] to List[Tuple[str, str]]
        raw_texts = None
        if body.raw_texts:
            raw_texts = [(item["name"], item["text"]) for item in body.raw_texts]
            print(f"[ROUTER] Processing {len(raw_texts)} raw texts: {[rt[0] for rt in raw_texts]}")
        else:
            print("[ROUTER] No raw texts to process")
        
        print(f"[ROUTER] Calling ingest_files with {len(files)} files and {len(raw_texts) if raw_texts else 0} raw texts")
        count = ingest_files(body.session_id, files, raw_texts)
        print(f"[ROUTER] Ingestion completed successfully, total chunks: {count}")
    except Exception as exc:
        print(f"[ROUTER] Error during ingestion: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
    return JSONResponse({"session_id": body.session_id, "chunks": count})


@router.post("/chat")
def post_chat(body: ChatRequest) -> JSONResponse:
    try:
        print(f"[CHAT] Starting chat for session: {body.session_id}")
        print(f"[CHAT] Received {len(body.messages)} messages")
        
        # Find the latest user message for similarity search
        latest_user_message = None
        for msg in reversed(body.messages):
            if msg.role == "user":
                latest_user_message = msg.content
                break
        
        if not latest_user_message:
            raise HTTPException(status_code=400, detail="No user message found")
        
        print(f"[CHAT] Latest user message: {latest_user_message[:100]}...")
        
        # Get relevant chunks using similarity search
        hits = search(body.session_id, latest_user_message, body.top_k)
        print(f"[CHAT] Found {len(hits)} relevant chunks")
        
        # Build context from retrieved chunks
        context_chunks = []
        for fn, cid, ct, dist in hits:
            context_chunks.append(f"[From {fn}, chunk {cid}]\n{ct}")
        
        context = "\n\n---\n\n".join(context_chunks)
        print(f"[CHAT] Built context with {len(context)} characters")
        
        # Build the system prompt with context
        system_prompt = f"""You are a helpful AI assistant. Answer the user's question based on the provided context from their documents.

Context from documents:
{context}

Instructions:
- Answer based primarily on the provided context
- If the context doesn't contain relevant information, say so clearly
- Be concise but comprehensive
- Reference specific documents when possible"""

        # Prepare messages for OpenAI (system + conversation history)
        openai_messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in body.messages:
            openai_messages.append({"role": msg.role, "content": msg.content})
        
        print(f"[CHAT] Calling OpenAI with {len(openai_messages)} messages")
        
        # Generate response using OpenAI
        chat_model = get_openai_chat_model("gpt-4o-mini", temperature=0.1)
        response = chat_model.invoke(openai_messages)
        
        assistant_response = response.content
        print(f"[CHAT] Generated response with {len(assistant_response)} characters")
        
        # Return both chunks and generated response
        return JSONResponse({
            "session_id": body.session_id,
            "response": assistant_response,
            "chunks": [
                {"filename": fn, "chunk_id": cid, "content": ct, "distance": dist}
                for fn, cid, ct, dist in hits
            ],
            "context_used": len(hits) > 0
        })
        
    except Exception as exc:
        print(f"[CHAT] Error during chat: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))



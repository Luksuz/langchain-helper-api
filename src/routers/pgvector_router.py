from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..api_models.ingest_request import IngestRequest
from ..api_models.chat_request import ChatRequest
from ..service.pgvector_service import ingest_files, search

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
        hits = search(body.session_id, body.query, body.top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return JSONResponse({
        "session_id": body.session_id,
        "query": body.query,
        "results": [
            {"filename": fn, "chunk_id": cid, "content": ct, "distance": dist}
            for fn, cid, ct, dist in hits
        ]
    })



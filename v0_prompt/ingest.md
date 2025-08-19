### /ingest — Create a session and store text chunks (pgvector)

Use this to create a logical folder by `session_id` and ingest files. The service extracts text (PDF/DOCX/TXT/XLSX), chunks it, embeds with OpenAI embeddings, and stores vectors in Postgres+pgvector.

Sample request
```http
POST /ingest
Content-Type: application/json

{
  "session_id": "c0b9f9a8-9a9a-4e9a-8a5f-4a2f2b5e0001",
  "files": [
    {"filename": "sample.pdf", "file_base64": "<base64>"}
  ]
}
```

Sample response
```json
{ "session_id": "c0b9f9a8-9a9a-4e9a-8a5f-4a2f2b5e0001", "chunks": 42 }
```



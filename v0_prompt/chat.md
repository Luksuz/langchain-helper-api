### /chat — Query a session using vector similarity (pgvector)

Use this to answer user questions over the ingested session. The service embeds the query, retrieves the top-k similar chunks (default 15), and returns them so your app can compose an answer.

Sample request
```http
POST /chat
Content-Type: application/json

{
  "session_id": "c0b9f9a8-9a9a-4e9a-8a5f-4a2f2b5e0001",
  "query": "Summarize the account details",
  "top_k": 15
}
```

Sample response
```json
{
  "session_id": "c0b9f9a8-9a9a-4e9a-8a5f-4a2f2b5e0001",
  "query": "Summarize the account details",
  "results": [
    {"filename": "sample.pdf", "chunk_id": 0, "content": "...", "distance": 0.12},
    {"filename": "sample.pdf", "chunk_id": 1, "content": "...", "distance": 0.14}
  ]
}
```



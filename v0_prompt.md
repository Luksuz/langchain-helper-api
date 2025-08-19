
[main app builder prompt]

USE THIS CONTEXT FOR STRUCUTRED RESPONSES USING LLMS

### For app builder agents. consume this api for structured api where needed

- Base URL (local): `https://langchain-helper-api-production.up.railway.app`
- Endpoints:
  - `POST /generate` (text-only structured output)
  - `POST /generate-vision` (structured output with images)
  - `POST /extract` (structured web extraction via Firecrawl)
  - `POST /render-pdf` (HTML → PDF rendering)
  - `POST /ocr` (Google Document AI OCR)
  - `POST /extract-text` (native PDF/DOCX text extraction)
  - `POST /ingest` (document ingestion into pgvector)
  - `POST /chat` (conversational AI with document context)
  - `POST /setup-db` (database schema setup from SQL)
  - `POST /query-db` (full database querying)
  - `POST /generate-schema` (AI-powered database schema generation)
  - `GET /db-health` (database connection health check)
  
  - `POST /generate-vision` Body fields:
    - `system_prompt` (string, optional)
    - `user_prompt` (string, required)
    - `structure` (object, required) — either an example object or a JSON Schema with `{type:"object", properties:{...}}`
    - `images` (array, optional) — elements:
      - `source_type`: `"url" | "base64"`
      - `url?`: string (if `source_type=url`)
      - `data?`: base64 string (if `source_type=base64`)
      - `mime_type?`: string (default `image/jpeg`)
    - `model` (string, optional; default `gpt-4o-mini`)
    - `temperature` (number, optional; default `0`)

  - `POST /extract` Body fields:
    - `urls` (array, required): list of URLs or patterns (e.g., `https://docs.firecrawl.dev/*`)
    - `prompt` (string, required): instruction describing what to extract
    - `structure` (object, required): example object or JSON Schema; backend converts to JSON Schema dynamically
    - `api_key` (string, optional): Firecrawl API key (if not using environment configuration)
- Response shape:
  - `{ "data": <object>, "model_name": <string> }`

Prompt postfix template (copy/paste below to append to your main prompt in V0):

```
You can call my backend to return validated structured JSON using LangChain structured outputs.

Text-only endpoint:
POST https://langchain-helper-api-production.up.railway.app/generate
Content-Type: application/json
Body fields:
- system_prompt (string, optional)
- user_prompt (string, required)
- structure (object, required) — either an example object or a JSON Schema with {type:"object", properties:{...}}
- model (string, optional; default gpt-4o-mini)
- temperature (number, optional; default 0)

Vision endpoint (supports images):
POST https://langchain-helper-api-production.up.railway.app/generate-vision
Content-Type: application/json
Body fields:
- system_prompt (string, optional)
- user_prompt (string, required)
- structure (object, required)
- images (array, optional) — elements:
  { source_type: "url" | "base64", url?: string, data?: string, mime_type?: string }
- model (string, optional; default gpt-4o-mini)
- temperature (number, optional; default 0)

Extraction endpoint (structured web extraction via Firecrawl):
POST https://langchain-helper-api-production.up.railway.app/extract
Content-Type: application/json
Body fields:
- urls (array, required)
- prompt (string, required)
- structure (object, required)
- api_key (string, optional)

OCR endpoint (Google Document AI):
POST https://langchain-helper-api-production.up.railway.app/ocr
Content-Type: application/json
Body fields:
- image_base64 (string, required)
- mime_type (string, required)

Render PDF endpoint (HTML → PDF):
POST https://langchain-helper-api-production.up.railway.app/render-pdf
Content-Type: application/json
Body fields:
- html (string, required)

Text extraction endpoint (PDF/DOCX → text):
POST https://langchain-helper-api-production.up.railway.app/extract-text
Content-Type: application/json
Body fields:
- file_base64 (string, required)
- filename (string, required) — with .pdf or .docx extension

Document ingestion endpoint (pgvector storage):
POST https://langchain-helper-api-production.up.railway.app/ingest
Content-Type: application/json
Body fields:
- session_id (string, required) — UUID for document session
- files (array, required) — objects with filename and file_base64
- raw_texts (array, optional) — objects with name and text

Conversational AI endpoint (chat with documents):
POST https://langchain-helper-api-production.up.railway.app/chat
Content-Type: application/json
Body fields:
- session_id (string, required) — UUID from previous ingest
- messages (array, required) — conversation history with role ("user"/"assistant"/"system") and content
- top_k (number, optional) — max chunks to retrieve (default 15)

Database setup endpoint (create schema from SQL):
POST https://langchain-helper-api-production.up.railway.app/setup-db
Content-Type: application/json
Body fields:
- sql_content (string, required) — SQL statements to execute (CREATE TABLE, INSERT, etc.)
- connection_string (string, optional) — PostgreSQL connection string

Database query endpoint (full SQL capabilities):
POST https://langchain-helper-api-production.up.railway.app/query-db
Content-Type: application/json
Body fields:
- sql_query (string, required) — Any SQL statement to execute (SELECT, INSERT, UPDATE, DELETE, etc.)
- connection_string (string, optional) — PostgreSQL connection string

Database schema generation endpoint (AI-powered):
POST https://langchain-helper-api-production.up.railway.app/generate-schema
Content-Type: application/json
Body fields:
- project_description (string, required) — Description of project and data requirements
- additional_requirements (string, optional) — Specific technical requirements
- model (string, optional) — OpenAI model name (default: "gpt-4o-mini")
- temperature (number, optional) — Creativity level 0.0-1.0 (default: 0.1)

Database health endpoint (connection check):
GET https://langchain-helper-api-production.up.railway.app/db-health

Response shape for structured endpoints:
{ "data": <structured_object>, "model_name": "<model>" }

Response shape for document AI endpoints:
- /ingest: { "session_id": "<uuid>", "chunks": <number> }
- /chat: { "session_id": "<uuid>", "response": "<ai_response>", "chunks": [<chunk_objects>], "context_used": <boolean> }

Response shape for database endpoints:
- /setup-db: { "success": <boolean>, "message": "<string>", "executed_statements": <number> }
- /query-db: { "success": <boolean>, "columns": [<strings>], "rows": [<objects>], "row_count": <number>, "message?": "<string>" }
- /generate-schema: { "success": <boolean>, "sql_schema": "<string>", "app_uuid": "<string>", "tables_created": [<strings>], "explanation": "<string>", "message?": "<string>" }
- /db-health: { "status": "<healthy|unhealthy>", "message": "<string>" }

Notes:
- The backend enforces the schema via LangChain's with_structured_output.
- For JSON Schema, use { type: "object", properties: { ... }, required?: [ ... ] }.
- For base64 images, provide only the raw base64; the backend will build a data URL.
 - For extraction, send { urls, prompt, structure } to `/extract`. The backend converts `structure` to a JSON Schema and calls Firecrawl.
 - Do not reference or require SDKs outside of this context for LLMs, scraping, or PDF generation. Always call the provided endpoints.

- For document AI (/ingest, /chat), the backend requires PGVECTOR_URL and OPENAI_API_KEY environment variables.
- /chat supports full conversation history - include previous assistant/user messages to maintain context.
- /ingest creates document sessions that can be queried later via /chat with the same session_id.
- For database endpoints (/setup-db, /query-db), the backend requires DATABASE_URL or PGVECTOR_URL for PostgreSQL connection.
- For /generate-schema, the backend requires OPENAI_API_KEY for AI-powered schema generation.
- /setup-db executes SQL statements in transactions - all succeed or all fail for data integrity.
- /query-db supports all SQL operations - SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, etc.
- /generate-schema creates database schemas with UUID-postfixed table names for app isolation.
- Use /generate-schema to create schemas, /setup-db to implement them, then /query-db for data operations.
- Each app gets unique table names (e.g., users_a1b2c3d4) to prevent conflicts between different v0 projects.

```

Minimal fetch example (text-only):

```bash
curl -X POST http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "system_prompt": "You are a helpful assistant.",
    "user_prompt": "Return a person object matching the schema.",
    "structure": {"type":"object","properties":{"name":{"type":"string"},"age":{"type":"integer"}},"required":["name","age"]}
  }'
```

Minimal fetch example (vision):

```bash
curl -X POST http://localhost:8000/generate-vision \
  -H 'Content-Type: application/json' \
  -d '{
    "system_prompt": "You are a helpful assistant that uses the image(s) to produce structured outputs.",
    "user_prompt": "Describe the scene and extract key attributes in the requested structure.",
    "structure": {"type":"object","properties":{"summary":{"type":"string"},"objects":{"type":"array","items":{"type":"string"}}},"required":["summary","objects"]},
    "images": [{"source_type": "url", "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"}],
    "model": "gpt-4o-mini",
    "temperature": 0
  }'
```



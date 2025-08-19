## Handy AI API

Comprehensive FastAPI service providing:
- **Structured Output Generation**: Convert prompts to structured JSON using LangChain + OpenAI
- **Document AI**: Ingest, process, and chat with PDF/DOCX documents using pgvector + embeddings
- **Conversational AI**: Context-aware chat with document knowledge and conversation history
- **Database Operations**: Setup PostgreSQL schemas and query databases securely for v0 apps
- **AI Schema Generation**: Automatically generate database schemas from project descriptions
- **Text Extraction**: Native PDF/DOCX text extraction and Google Document AI OCR
- **Web Scraping**: Extract structured data from websites using Firecrawl
- **PDF Generation**: Convert HTML to professional PDFs

Reference: [LangChain Structured outputs](https://python.langchain.com/docs/concepts/structured_outputs/)

### Requirements

- Python 3.9+
- An OpenAI API key in env var `OPENAI_API_KEY`
- Optional: PostgreSQL with pgvector extension (`PGVECTOR_URL`) for document AI features
- Optional: Google Cloud credentials for OCR (`GOOGLE_APPLICATION_CREDENTIALS`)
- Optional: Firecrawl API key for web scraping (`FIRECRAWL_API_KEY`)

### Install and run (local)

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

export OPENAI_API_KEY=YOUR_KEY_HERE
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Run with Docker

Build image:

```bash
docker build -t handy-api .
```

Run on port 8000:

```bash
docker run -e OPENAI_API_KEY=YOUR_KEY_HERE -p 8000:8000 handy-api
```

### API

- POST `/generate`
  - Body:
    - `system_prompt` (optional): string
    - `user_prompt`: string
    - `structure`: object (either an example dict or a JSON Schema `{type:"object", properties:{...}}`)
    - `model` (optional): OpenAI chat model (default `gpt-4o-mini`)
    - `temperature` (optional): float (default `0.0`)

- POST `/generate-vision`
  - Body:
    - `system_prompt` (optional): string
    - `user_prompt`: string
    - `structure`: object (example dict or JSON Schema)
    - `images`: array of objects, each with:
      - `source_type`: `base64` or `url`
      - `data`: base64 string (if `source_type=base64`)
      - `url`: string (if `source_type=url`)
      - `mime_type`: optional, default `image/jpeg`
    - `model` (optional): OpenAI chat model with vision support (default `gpt-4o-mini`)
    - `temperature` (optional): float (default `0.0`)

- POST `/extract` (Firecrawl integration)
  - Body:
    - `urls`: array of strings (supports wildcards like `https://docs.firecrawl.dev/*`)
    - `prompt`: string describing what to extract
    - `structure`: object (example dict or JSON Schema; backend converts to JSON Schema dynamically)
    - `api_key` (optional): Firecrawl API key; otherwise use `FIRECRAWL_API_KEY` if configured by the SDK
  - Returns: Firecrawl response payload

- POST `/render-pdf` (HTML → PDF)
  - Body:
    - `html`: string (the AI-generated HTML to render into a PDF)
  - Returns: `application/pdf` stream (use `--output` to save)

- POST `/ocr` (Google Document AI OCR)
  - Auth: requires `GOOGLE_APPLICATION_CREDENTIALS` pointing to a GCP service account JSON key file; uses `GOOGLE_CLOUD_PROJECT_ID` and `GOOGLE_DOCUMENT_AI_PROCESSOR_ID`. Optional `GOOGLE_CLOUD_LOCATION` (default `us`).
  - Body:
    - `image_base64`: base64-encoded image
    - `mime_type`: image MIME type (e.g., `image/png`)
    - `location` (optional): GCP location (default `us`)
  - Returns: `{ text, paragraphs?, entities? }`

- POST `/extract-text` (native text extraction for PDF/DOCX; no OCR)
  - Body:
    - `file_base64`: base64-encoded file
    - `filename`: original filename with extension (`.pdf` or `.docx`)
  - Returns: `{ text, method }`, where `method` indicates `langchain_pypdf`, `pypdf`, or `docx2txt`

- POST `/ingest` (pgvector document ingestion)
  - Auth: requires `PGVECTOR_URL` for database connection and `OPENAI_API_KEY` for embeddings
  - Body:
    - `session_id`: UUID for document session/folder
    - `files`: array of objects with `filename` and `file_base64` (supports PDF/DOCX)
    - `raw_texts` (optional): array of objects with `name` and `text` for direct text ingestion
  - Returns: `{ session_id, chunks }` where `chunks` is total count of text chunks stored

- POST `/chat` (conversational AI with document context)
  - Auth: requires `PGVECTOR_URL` for database access and `OPENAI_API_KEY` for chat model
  - Body:
    - `session_id`: UUID of previously ingested document session
    - `messages`: array of conversation messages with `role` (`user`/`assistant`/`system`) and `content`
    - `top_k` (optional): number of similar chunks to retrieve (default 15, max 50)
  - Returns: `{ session_id, response, chunks, context_used }` with AI response and source chunks

- POST `/setup-db` (database schema setup)
  - Auth: requires `DATABASE_URL` or `PGVECTOR_URL` for PostgreSQL connection
  - Body:
    - `sql_content`: SQL statements to execute (CREATE TABLE, INSERT, etc.)
    - `connection_string` (optional): PostgreSQL connection string
  - Returns: `{ success, message, executed_statements }` with execution results

- POST `/query-db` (full database querying)
  - Auth: requires `DATABASE_URL` or `PGVECTOR_URL` for PostgreSQL connection
  - Body:
    - `sql_query`: Any SQL statement to execute (SELECT, INSERT, UPDATE, DELETE, CREATE, etc.)
    - `connection_string` (optional): PostgreSQL connection string
  - Returns: `{ success, columns, rows, row_count, message? }` with query results in JSON format

- POST `/generate-schema` (AI-powered database schema generation)
  - Auth: requires `OPENAI_API_KEY` for AI model access
  - Body:
    - `project_description`: Description of project and data requirements
    - `additional_requirements` (optional): Specific technical requirements
    - `model` (optional): OpenAI model name (default: "gpt-4o-mini")
    - `temperature` (optional): Creativity level 0.0-1.0 (default: 0.1)
  - Returns: `{ success, sql_schema, app_uuid, tables_created, explanation, message? }` with generated SQL

- GET `/db-health` (database connection health check)
  - Auth: requires `DATABASE_URL` or `PGVECTOR_URL` for PostgreSQL connection
  - Returns: `{ status, message }` with database connectivity status

### Example (example dict as structure)

```bash
curl -X POST http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "system_prompt": "You are a helpful assistant that strictly follows the requested structure.",
    "user_prompt": "Fill out this user object plausibly based on the fields.",
    "structure": {
      "id": 1,
      "name": "Luka",
      "email": "luka@example.com",
      "address": {
        "street": "Main Street",
        "city": "Zagreb",
        "zip_code": "10000"
      },
      "tags": ["developer", "ai", "multi-agent"]
    },
    "model": "gpt-4o-mini",
    "temperature": 0
  }'
```

### Example (JSON Schema as structure)

```bash
curl -X POST http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "system_prompt": "You are a helpful assistant that returns only JSON matching the schema.",
    "user_prompt": "Return a user object matching this schema.",
    "structure": {
      "type": "object",
      "required": ["id", "name", "email", "address"],
      "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string"},
        "address": {
          "type": "object",
          "required": ["street", "city", "zip_code"],
          "properties": {
            "street": {"type": "string"},
            "city": {"type": "string"},
            "zip_code": {"type": "string"}
          }
        },
        "tags": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    }
  }'

### Example (Vision with image URL)

```bash
curl -X POST http://localhost:8000/generate-vision \
  -H 'Content-Type: application/json' \
  -d '{
    "system_prompt": "You are a helpful assistant that uses the image(s) to produce structured outputs.",
    "user_prompt": "Describe the scene and extract key attributes in the requested structure.",
    "structure": {
      "type": "object",
      "required": ["summary", "objects"],
      "properties": {
        "summary": {"type": "string"},
        "objects": {"type": "array", "items": {"type": "string"}}
      }
    },
    "images": [
      {"source_type": "url", "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"}
    ],
    "model": "gpt-4o-mini",
    "temperature": 0
  }'
```

### Example (`/extract` with Firecrawl)

```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://docs.firecrawl.dev/*",
      "https://firecrawl.dev/",
      "https://www.ycombinator.com/companies/"
    ],
    "prompt": "Extract the company mission, whether it supports SSO, whether it is open source, and whether it is in Y Combinator from the page.",
    "structure": {
      "company_mission": "string",
      "supports_sso": false,
      "is_open_source": true,
      "is_in_yc": true
    }
  }'
```

### Example (`/render-pdf`)

```bash
curl -X POST http://localhost:8000/render-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><head><meta charset=\"utf-8\"><title>AI Report</title><script src=\"https://cdn.tailwindcss.com\"></script></head><body class=\"bg-gray-50 text-gray-800 p-10 font-sans\"><div class=\"max-w-3xl mx-auto bg-white shadow-lg rounded-2xl p-8\"><h1 class=\"text-4xl font-bold text-gray-900 border-b pb-4 mb-6\">AI Report</h1><p class=\"text-lg mb-6\">This was generated by an LLM.</p><div class=\"text-sm text-gray-500 border-t pt-4\">&copy; 2025 AI System – All rights reserved.</div></div></body></html>"
  }' \
  --output report.pdf
```

Notes for Tailwind CDN in PDFs:
- Tailwind Play CDN is JavaScript-based; wkhtmltopdf supports JS with a delay. The service enables JS and waits ~2 seconds. If styles are missing, increase delay or inline a precompiled CSS. For most static reports, consider using a precompiled Tailwind CSS instead of CDN for deterministic rendering.

### Example (`/ocr` with Google Document AI)

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json
export GOOGLE_CLOUD_PROJECT_ID=your-gcp-project
export GOOGLE_DOCUMENT_AI_PROCESSOR_ID=your-processor-id

IMG_B64=$(base64 -w0 sample.png) # macOS: base64 sample.png | tr -d '\n'
curl -X POST http://localhost:8000/ocr \
  -H "Content-Type: application/json" \
  -d "{\
    \"image_base64\": \"$IMG_B64\",\
    \"mime_type\": \"image/png\",\
    \"location\": \"us\"\
  }"
```

### Example (`/extract-text` PDF)

```bash
FILE_B64=$(base64 -w0 sample.pdf) # macOS: base64 sample.pdf | tr -d '\n'
curl -X POST http://localhost:8000/extract-text \
  -H "Content-Type: application/json" \
  -d "{\
    \"file_base64\": \"$FILE_B64\",\
    \"filename\": \"sample.pdf\"\
  }"
```

### Example (`/ingest`)

```bash
SESSION_ID=$(python - <<'PY'
import uuid; print(uuid.uuid4())
PY
)
FILE_B64=$(base64 -w0 account_details_proof_eur.pdf) # macOS: base64 account_details_proof_eur.pdf | tr -d '\n'
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d "{\
    \"session_id\": \"$SESSION_ID\",\
    \"files\": [{\"filename\": \"account_details_proof_eur.pdf\", \"file_base64\": \"$FILE_B64\"}]\
  }"
```

### Example (`/chat`)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "'$SESSION_ID'",
    "messages": [
      {
        "role": "user",
        "content": "What are the main points in this document? Please provide a summary."
      }
    ],
    "top_k": 15
  }'
```

**Response:**
```json
{
  "session_id": "c0b9f9a8-9a9a-4e9a-8a5f-4a2f2b5e0001",
  "response": "Based on your document, here are the main points: ...",
  "chunks": [
    {
      "filename": "account_details_proof_eur.pdf",
      "chunk_id": 0,
      "content": "Account holder: John Doe...",
      "distance": 0.089
    }
  ],
  "context_used": true
}
```

### Example (`/setup-db`)

```bash
curl -X POST http://localhost:8000/setup-db \
  -H "Content-Type: application/json" \
  -d '{
    "sql_content": "CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR(100) UNIQUE NOT NULL, email VARCHAR(255) UNIQUE NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP); INSERT INTO users (username, email) VALUES ('"'"'admin'"'"', '"'"'admin@example.com'"'"');"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully executed 2 SQL statements", 
  "executed_statements": 2
}
```

### Example (`/query-db`)

**Select Query:**
```bash
curl -X POST http://localhost:8000/query-db \
  -H "Content-Type: application/json" \
  -d '{
    "sql_query": "SELECT id, username, email, created_at FROM users ORDER BY created_at DESC LIMIT 10"
  }'
```

**Insert/Update Query:**
```bash
curl -X POST http://localhost:8000/query-db \
  -H "Content-Type: application/json" \
  -d '{
    "sql_query": "INSERT INTO users (username, email) VALUES ('"'"'new_user'"'"', '"'"'user@example.com'"'"') RETURNING id, username"
  }'
```

**Response:**
```json
{
  "success": true,
  "columns": ["id", "username", "email", "created_at"],
  "rows": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com", 
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "row_count": 1
}
```

### Example (`/generate-schema`)

```bash
curl -X POST http://localhost:8000/generate-schema \
  -H "Content-Type: application/json" \
  -d '{
    "project_description": "A weather tracking application that stores daily weather data including temperature, humidity, pressure, wind speed, and weather conditions for different cities",
    "additional_requirements": "Include historical data storage and multiple weather stations per city"
  }'
```

**Response:**
```json
{
  "success": true,
  "sql_schema": "CREATE TABLE cities_a1b2c3d4 (\n  id SERIAL PRIMARY KEY,\n  name VARCHAR(255) NOT NULL,\n  country VARCHAR(100) NOT NULL,\n  latitude DECIMAL(10,8),\n  longitude DECIMAL(11,8),\n  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n);",
  "app_uuid": "a1b2c3d4",
  "tables_created": ["cities_a1b2c3d4", "weather_data_a1b2c3d4", "weather_stations_a1b2c3d4"],
  "explanation": "Generated database schema for weather tracking application with UUID a1b2c3d4..."
}
```

Notes:
- For `/extract`, install and configure Firecrawl. You can pass `api_key` in the request or configure `FIRECRAWL_API_KEY` if supported.
- For `/render-pdf`, ensure your HTML is self-contained (inline/base64 images, embedded styles) for best fidelity.
- For `/ingest` and `/chat`, set `PGVECTOR_URL` to your Postgres+pgvector connection string and `OPENAI_API_KEY` for both embeddings and chat responses.
- For `/setup-db` and `/query-db`, set `DATABASE_URL` or `PGVECTOR_URL` for PostgreSQL connection.
- For `/generate-schema`, set `OPENAI_API_KEY` for AI-powered schema generation.
- `/chat` supports full conversation history - include previous messages to maintain context across interactions.
- `/query-db` supports all SQL operations - SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, etc.
- `/generate-schema` creates UUID-postfixed table names to isolate different v0 app databases.


## Handy Structured Output API

FastAPI service that takes a system prompt + user prompt and either an example JSON object or a JSON Schema, and returns structured output using LangChain structured outputs with OpenAI.

Reference: [LangChain Structured outputs](https://python.langchain.com/docs/concepts/structured_outputs/)

### Requirements

- Python 3.9+
- An OpenAI API key in env var `OPENAI_API_KEY`

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
    "query": "Summarize the account details",
    "top_k": 15
  }'
```

Notes:
- For `/extract`, install and configure Firecrawl. You can pass `api_key` in the request or configure `FIRECRAWL_API_KEY` if supported.
- For `/render-pdf`, ensure your HTML is self-contained (inline/base64 images, embedded styles) for best fidelity.
- For `/ingest` and `/chat`, set `PGVECTOR_URL` to your Postgres+pgvector connection string and `OPENAI_API_KEY` for embeddings.



[main app builder prompt]

USE THIS CONTEXT FOR STRUCUTRED RESPONSES USING LLMS

### For app builder agents. consume this api for structured api where needed

- Base URL (local): `https://langchain-helper-api-production.up.railway.app`
- Endpoints:
  - `POST /generate` (text-only structured output)
  - `POST /generate-vision` (structured output with images)
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

Response shape for both endpoints:
{ "data": <structured_object>, "model_name": "<model>" }

Notes:
- The backend enforces the schema via LangChain's with_structured_output.
- For JSON Schema, use { type: "object", properties: { ... }, required?: [ ... ] }.
- For base64 images, provide only the raw base64; the backend will build a data URL.
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



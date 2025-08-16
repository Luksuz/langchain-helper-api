
[main app builder prompt]

USE THIS CONTEXT FOR STRUCUTRED RESPONSES USING LLMS

### For app builder agents. consume this api for structured api where needed

- Base URL (local): `https://langchain-helper-api-production.up.railway.app`
- Endpoints:
  - `POST /generate` (text-only structured output)
  - `POST /generate-vision` (structured output with images)
  - `POST /extract` (structured web extraction via Firecrawl)
  
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
 - For extraction, send { urls, prompt, structure } to `/extract`. The backend converts `structure` to a JSON Schema and calls Firecrawl.
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



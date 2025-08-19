### /generate-vision — Structured output with images

Use this when your prompt includes one or more images and you need structured JSON output.

Sample request
```http
POST https://langchain-helper-api-production.up.railway.app/generate-vision
Content-Type: application/json

{
  "system_prompt": "Use provided images to answer.",
  "user_prompt": "Describe and list prominent objects.",
  "structure": {"type":"object","properties":{"summary":{"type":"string"},"objects":{"type":"array","items":{"type":"string"}}},"required":["summary","objects"]},
  "images": [{"source_type": "url", "url": "https://example.com/image.jpg"}],
  "model": "gpt-4o-mini",
  "temperature": 0
}
```

Sample response
```json
{
  "data": {"summary": "A wooden boardwalk in a nature reserve.", "objects": ["boardwalk", "trees", "sky"]},
  "model_name": "gpt-4o-mini"
}
```



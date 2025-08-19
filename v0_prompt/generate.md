### /generate — Text-only structured output

Use this when you need a structured JSON response from text-only prompts.

Sample request
```http
POST https://langchain-helper-api-production.up.railway.app/generate
Content-Type: application/json

{
  "system_prompt": "You are a helpful assistant.",
  "user_prompt": "Return a person matching the schema.",
  "structure": {"type":"object","properties":{"name":{"type":"string"},"age":{"type":"integer"}},"required":["name","age"]},
  "model": "gpt-4o-mini",
  "temperature": 0
}
```

Sample response
```json
{
  "data": {"name": "Luka", "age": 28},
  "model_name": "gpt-4o-mini"
}
```



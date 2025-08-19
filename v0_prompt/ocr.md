### /ocr — OCR with Google Document AI

Use this to extract text (and basic structure) from images using a configured Document AI processor.

Sample request
```http
POST /ocr
Content-Type: application/json

{
  "image_base64": "<base64>",
  "mime_type": "image/png",
}
```

Sample response
```json
{
  "text": "Acme Corp Invoice...",
  "paragraphs": ["Acme Corp", "Invoice #1234"],
  "entities": [
    {"type": "invoice_number", "mentionText": "1234", "confidence": 0.98}
  ]
}
```



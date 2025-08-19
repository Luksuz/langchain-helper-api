### /extract-text — Native text extraction for PDF/DOCX (no OCR)

Use this when you need quick text extraction from digital PDFs or DOCX files. This does not perform OCR on scanned images.

Sample request
```http
POST https://langchain-helper-api-production.up.railway.app/extract-text
Content-Type: application/json

{
  "file_base64": "<base64>",
  "filename": "sample.pdf"
}
```

Sample response
```json
{
  "text": "This is the document text...",
  "method": "langchain_pypdf"
}
```



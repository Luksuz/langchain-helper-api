### /render-pdf — HTML to PDF rendering

Use this to convert AI-generated HTML into a PDF. Prefer linking a static Tailwind CSS file or inline CSS for reliability.

Sample request
```http
POST https://langchain-helper-api-production.up.railway.app/render-pdf
Content-Type: application/json

{
  "html": "<html><head><meta charset=\"utf-8\"><title>AI Report</title><link rel=\"stylesheet\" href=\"/assets/tailwind.min.css\"></head><body class=\"p-10\"><h1 class=\"text-3xl font-bold\">AI Report</h1></body></html>"
}
```

Sample response
```
application/pdf (binary stream)
```



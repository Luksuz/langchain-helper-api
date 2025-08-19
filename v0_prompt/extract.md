### /extract — Structured web extraction (Firecrawl)

Use this to extract structured data from one or more URLs using a schema.

Sample request
```http
POST /extract
Content-Type: application/json

{
  "urls": ["https://docs.firecrawl.dev/*", "https://firecrawl.dev/"],
  "prompt": "Extract mission and whether it supports SSO.",
  "structure": {
    "company_mission": "string",
    "supports_sso": false
  }
}
```

Sample response
```json
{
  "success": true,
  "data": {
    "company_mission": "Firecrawl is the easiest way...",
    "supports_sso": false
  }
}
```



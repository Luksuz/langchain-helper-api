### /extract — Structured web extraction (Firecrawl)

Use this to extract structured data from one or more URLs using a schema. Create a Next.js API route that proxies to the backend.

**Next.js API Route** (`/api/extract/route.ts`):
```typescript
export async function POST(request: Request) {
  const body = await request.json();
  const response = await fetch('https://langchain-helper-api-production.up.railway.app/extract', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return Response.json(await response.json());
}
```

**Frontend usage**:
```javascript
const response = await fetch('/api/extract', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    urls: ["https://docs.firecrawl.dev/*", "https://firecrawl.dev/"],
    prompt: "Extract mission and whether it supports SSO.",
    structure: {
      company_mission: "string",
      supports_sso: false
    }
  })
});
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



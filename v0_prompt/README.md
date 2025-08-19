## V0 Prompt API Reference (Split by Endpoint)

Use these per-endpoint guides when instructing an app builder. Each file includes a short description, when to use it, a sample request, and a sample response.

### 🚨 CRITICAL: Next.js Integration Pattern

**ALL endpoints must be accessed via Next.js API routes that proxy to the backend. DO NOT make direct calls from frontend to external APIs.**

**Standard Next.js API Route Pattern:**
```typescript
// /api/[endpoint]/route.ts
export async function POST(request: Request) {
  const body = await request.json();
  const response = await fetch('https://langchain-helper-api-production.up.railway.app/[endpoint]', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return Response.json(await response.json());
}
```

**Frontend Usage:**
```javascript
// ✅ CORRECT: Call local API route
const response = await fetch('/api/extract', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(requestData)
});

// ❌ WRONG: Direct external API call
const response = await fetch('https://langchain-helper-api-production.up.railway.app/extract', ...);
```

### 📚 Available Endpoints

- [Text generation: /generate](./generate.md)
- [Vision generation: /generate-vision](./generate-vision.md)
- [Web extraction (Firecrawl): /extract](./extract.md)
- [HTML → PDF rendering: /render-pdf](./render-pdf.md)
- [OCR (Google Document AI): /ocr](./ocr.md)
- [Native text extraction (PDF/DOCX): /extract-text](./extract-text.md)
- [Ingest vectors (PGVector): /ingest](./ingest.md)
- [Chat over vectors (PGVector): /chat](./chat.md)
- [Query the database (SQLALCHEMY): /query-db](./query-db.md)
- [Generate database schema: /generate-schema](./generate-schema.md)

Base URL (production): `https://langchain-helper-api-production.up.railway.app`

### 🔄 Complete Next.js Example

For a news scraper app, create these API routes:

```typescript
// /api/extract/route.ts - Web scraping
export async function POST(request: Request) {
  const body = await request.json();
  const response = await fetch('https://langchain-helper-api-production.up.railway.app/extract', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return Response.json(await response.json());
}

// /api/ingest/route.ts - Store scraped articles
export async function POST(request: Request) {
  const body = await request.json();
  const response = await fetch('https://langchain-helper-api-production.up.railway.app/ingest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return Response.json(await response.json());
}

// /api/chat/route.ts - Search articles
export async function POST(request: Request) {
  const body = await request.json();
  const response = await fetch('https://langchain-helper-api-production.up.railway.app/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return Response.json(await response.json());
}

// /api/setup-db/route.ts - Database setup
export async function POST(request: Request) {
  const body = await request.json();
  const response = await fetch('https://langchain-helper-api-production.up.railway.app/setup-db', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return Response.json(await response.json());
}
```


### /chat — Conversational AI with document context (pgvector + OpenAI)

Use this to have conversations with an AI assistant that has access to your ingested documents. The service accepts a list of messages (conversation history), performs similarity search using the latest user message, and generates contextual responses using OpenAI with the retrieved document chunks.

**Features:**
- Supports full conversation history with message roles (user, assistant, system)
- Retrieves relevant document chunks using vector similarity search
- Generates AI responses with document context using OpenAI GPT models
- Returns both the generated response and the source chunks used

**Next.js API Route** (`/api/chat/route.ts`):
```typescript
export async function POST(request: Request) {
  const body = await request.json();
  const response = await fetch('https://langchain-helper-api-production.up.railway.app/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return Response.json(await response.json());
}
```

**Frontend usage**:
```javascript
const response = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: "c0b9f9a8-9a9a-4e9a-8a5f-4a2f2b5e0001",
    messages: [
      {
        role: "user", 
        content: "What are the main points in this document?"
      },
      {
        role: "assistant", 
        content: "Based on the document, the main points are..."
      },
      {
        role: "user", 
        content: "Can you elaborate on the financial section?"
      }
    ],
    top_k: 15
  })
});
```

Sample response
```json
{
  "session_id": "c0b9f9a8-9a9a-4e9a-8a5f-4a2f2b5e0001",
  "response": "Based on the financial section of your documents, here are the key details...",
  "chunks": [
    {
      "filename": "financial_report.pdf", 
      "chunk_id": 2, 
      "content": "Revenue for Q3 was $1.2M, representing a 15% increase...", 
      "distance": 0.08
    },
    {
      "filename": "budget.docx", 
      "chunk_id": 0, 
      "content": "Operating expenses include marketing $200K, salaries $800K...", 
      "distance": 0.12
    }
  ],
  "context_used": true
}
```

**Message Roles:**
- `user`: User messages/questions
- `assistant`: AI assistant responses  
- `system`: System instructions (optional)

**Parameters:**
- `session_id`: UUID of the ingested document session
- `messages`: Array of conversation messages with role and content
- `top_k`: Number of similar chunks to retrieve (default: 15, max: 50)



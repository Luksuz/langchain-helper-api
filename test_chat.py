import os
import requests


BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def main():
    session_id = "3d063ac8-486b-4aea-a28a-0f0133dbbbba"
    if not session_id:
        print("Set SESSION_ID to a previously ingested session.")
        return

    # Example conversation with message history
    payload = {
        "session_id": session_id,
        "messages": [
            {
                "role": "user",
                "content": os.environ.get("CHAT_QUERY", "What does this document contain? Please summarize the main points.")
            }
        ],
        "top_k": int(os.environ.get("TOP_K", "15")),
    }
    
    url = f"{BASE_URL}/chat"
    resp = requests.post(url, json=payload)
    print("POST /chat status:", resp.status_code)
    print()
    
    try:
        result = resp.json()
        print("=== CHAT RESPONSE ===")
        print(f"Session ID: {result.get('session_id', 'N/A')}")
        print(f"Context Used: {result.get('context_used', 'N/A')}")
        print(f"Found {len(result.get('chunks', []))} relevant chunks")
        print()
        print("=== AI RESPONSE ===")
        print(result.get('response', 'No response'))
        print()
        print("=== RELEVANT CHUNKS ===")
        for i, chunk in enumerate(result.get('chunks', [])[:3]):  # Show top 3 chunks
            print(f"Chunk {i+1} (from {chunk['filename']}, chunk {chunk['chunk_id']}, distance: {chunk['distance']:.4f}):")
            print(chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content'])
            print("---")
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(resp.text)


if __name__ == "__main__":
    main()



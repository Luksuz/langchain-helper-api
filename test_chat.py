import os
import requests


BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def main():
    session_id = "3d063ac8-486b-4aea-a28a-0f0133dbbbba"
    if not session_id:
        print("Set SESSION_ID to a previously ingested session.")
        return

    payload = {
        "session_id": session_id,
        "query": os.environ.get("CHAT_QUERY", "Summarize the account details"),
        "top_k": int(os.environ.get("TOP_K", "15")),
    }
    url = f"{BASE_URL}/chat"
    resp = requests.post(url, json=payload)
    print("POST /chat status:", resp.status_code)
    try:
        print(resp.json())
    except Exception:
        print(resp.text)


if __name__ == "__main__":
    main()



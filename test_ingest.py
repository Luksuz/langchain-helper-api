import base64
import os
import sys
import uuid
import requests


BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def b64_file(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def main():
    session_id = os.environ.get("SESSION_ID") or str(uuid.uuid4())
    paths = []
    # Collect sample files if they exist; adjust as needed
    for candidate in [
        "document.docx",
    ]:
        if os.path.exists(candidate):
            paths.append(candidate)

    if not paths:
        print("No sample files found (looked for PDF/DOCX/TXT/XLSX). Pass file paths as args.")
        if len(sys.argv) > 1:
            paths = sys.argv[1:]
        else:
            sys.exit(1)

    files = []
    for p in paths:
        try:
            files.append({"filename": os.path.basename(p), "file_base64": b64_file(p)})
        except Exception as e:
            print(f"Skipping {p}: {e}")

    payload = {"session_id": session_id, "files": files}
    url = f"{BASE_URL}/ingest"
    resp = requests.post(url, json=payload)
    print("POST /ingest status:", resp.status_code)
    try:
        print(resp.json())
    except Exception:
        print(resp.text)
    print("SESSION_ID:", session_id)


if __name__ == "__main__":
    main()



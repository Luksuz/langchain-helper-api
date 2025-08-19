import base64
import os
import requests


BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def test_extract_text_docx(file_path: str) -> None:
    with open(file_path, "rb") as f:
        file_b64 = base64.b64encode(f.read()).decode("utf-8")
    payload = {
        "file_base64": file_b64,
        "filename": os.path.basename(file_path),
    }
    url = f"{BASE_URL}/extract-text"
    resp = requests.post(url, json=payload)
    print("/extract-text DOCX status:", resp.status_code)
    print(resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text)


if __name__ == "__main__":
    path = "document.pdf"
    if os.path.exists(path):
        test_extract_text_docx(path)
    else:
        print(f"Skipping DOCX test: {path} not found")



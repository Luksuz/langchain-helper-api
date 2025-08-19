import base64
import requests
import os


BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def test_ocr(image_path: str, mime_type: str = "image/png") -> None:
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "image_base64": image_base64,
        "mime_type": mime_type,
    }
    url = f"{BASE_URL}/ocr"
    resp = requests.post(url, json=payload)
    print("/ocr status:", resp.status_code)
    print(resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text)


def test_extract_text(file_path: str) -> None:
    with open(file_path, "rb") as f:
        file_b64 = base64.b64encode(f.read()).decode("utf-8")
    payload = {
        "file_base64": file_b64,
        "filename": os.path.basename(file_path),
    }
    url = f"{BASE_URL}/extract-text"
    resp = requests.post(url, json=payload)
    print("/extract-text status:", resp.status_code)
    print(resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text)


if __name__ == "__main__":
    # Test OCR (update path/mime if needed)
    if os.path.exists("document.png"):
        test_ocr("document.png", "image/png")
    else:
        print("Skipping OCR test: document.png not found")

    # Test native text extraction for PDF
    if os.path.exists("account_details_proof_eur.pdf"):
        test_extract_text("account_details_proof_eur.pdf")
    else:
        print("Skipping extract-text PDF test: account_details_proof_eur.pdf not found")

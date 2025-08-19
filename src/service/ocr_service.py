from __future__ import annotations

import os
from typing import Any, Dict, List
import base64
from dotenv import load_dotenv
from google.cloud.documentai_v1 import DocumentProcessorServiceClient, ProcessRequest
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

load_dotenv()


def _get_processor_name(project_id: str, location: str, processor_id: str) -> str:
    return f"projects/{project_id}/locations/{location}/processors/{processor_id}"


def extract_text_rich(image_base64: str, mime_type: str) -> Dict[str, Any]:
    """Enhanced OCR returning text, paragraphs and entities if present."""
    print(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    service_account_b64 = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not service_account_b64:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS must be set to a base64-encoded service account key")
    service_account_json = base64.b64decode(service_account_b64).decode("utf-8")

    import json
    try:
        service_account_info = json.loads(service_account_json)
    except Exception as exc:
        raise RuntimeError(f"Failed to parse service account JSON: {exc}")

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT_ID")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION")
    processor_id = os.environ.get("GOOGLE_DOCUMENT_AI_PROCESSOR_ID")
    if not all([project_id, location, processor_id]):
        raise RuntimeError("GOOGLE_CLOUD_PROJECT_ID, GOOGLE_CLOUD_LOCATION, and GOOGLE_DOCUMENT_AI_PROCESSOR_ID must be set in the environment")

    client = DocumentProcessorServiceClient(
        credentials=ServiceAccountCredentials.from_service_account_info(
            service_account_info
        )
    )
    name = _get_processor_name(project_id, location, processor_id)
    request = ProcessRequest(
        name=name,
        raw_document={"content": image_base64, "mime_type": mime_type},
    )
    result = client.process_document(request)
    document = result.document

    text = document.text or ""

    def get_text_segment(text_anchor) -> str:
        if not getattr(text_anchor, "text_segments", None):
            return ""
        text_segments = text_anchor.text_segments
        if not text_segments:
            return ""
        start_index = getattr(text_segments[0], "start_index", 0)
        end_index = getattr(text_segments[0], "end_index", 0)
        return text[start_index:end_index]

    paragraphs: List[str] = []
    if getattr(document, "pages", None):
        page = document.pages[0]
        for p in getattr(page, "paragraphs", []) or []:
            t = get_text_segment(p.layout.text_anchor)
            if t.strip():
                paragraphs.append(t.strip())

    entities = []
    for e in getattr(document, "entities", []) or []:
        entities.append(
            {
                "type": getattr(e, "type_", getattr(e, "type", "unknown")),
                "mentionText": getattr(e, "mention_text", ""),
                "confidence": getattr(e, "confidence", 0.0),
            }
        )

    return {
        "text": text,
        "paragraphs": paragraphs or None,
        "entities": entities or None,
    }

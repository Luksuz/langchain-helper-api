from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ExtractRequest(BaseModel):
    urls: List[str] = Field(
        ..., description="List of URLs or URL patterns (e.g., https://site.com/*) to extract from"
    )
    prompt: str = Field(
        ..., description="Instruction describing what to extract from the pages"
    )
    structure: Dict[str, Any] = Field(
        ..., description="Example object or JSON Schema describing the desired extracted output"
    )
    api_key: Optional[str] = Field(
        default=None, description="Optional Firecrawl API key; otherwise uses FIRECRAWL_API_KEY env var"
    )



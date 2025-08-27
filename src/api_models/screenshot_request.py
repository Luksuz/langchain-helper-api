from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


DEFAULT_SCREENSHOT_OPTIONS: Dict[str, Any] = {
    "onlyMainContent": True,
    "maxAge": 172800000,
    "parsers": ["pdf"],
    "formats": [
        {
            "type": "screenshot",
            "fullPage": True,
        }
    ],
}


class ScreenshotRequest(BaseModel):
    url: str = Field(..., description="Target URL to screenshot")
    options: Dict[str, Any] = Field(default_factory=lambda: DEFAULT_SCREENSHOT_OPTIONS.copy())






from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, Field


class ImageInput(BaseModel):
    source_type: Literal["base64", "url"] = Field(..., description="Image source type")
    data: Optional[str] = Field(
        default=None, description="Base64-encoded image data (if source_type=base64)"
    )
    url: Optional[str] = Field(
        default=None, description="Publicly accessible URL (if source_type=url)"
    )
    mime_type: Optional[str] = Field(
        default="image/jpeg", description="MIME type for base64 payloads"
    )


class StructuredGenVisionRequest(BaseModel):
    system_prompt: Optional[str] = Field(
        default=None, description="Optional system instruction for the model"
    )
    user_prompt: str = Field(..., description="User message for the model")
    structure: Dict[str, Any] = Field(
        ..., description="JSON Schema or example dictionary describing desired output"
    )
    images: List[ImageInput] = Field(
        default_factory=list, description="List of images to include in the prompt"
    )
    model: str = Field(
        default="gpt-5-mini",
        description="OpenAI chat model name supporting vision, e.g. gpt-4o, gpt-4o-mini",
    )
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)



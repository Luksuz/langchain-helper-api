from pydantic import BaseModel, Field


class OCRRequest(BaseModel):
    image_base64: str = Field(..., description="Base64-encoded image data")
    mime_type: str = Field(..., description="Image MIME type, e.g. image/png")
    location: str = Field(default="us", description="GCP location, e.g. us or eu")


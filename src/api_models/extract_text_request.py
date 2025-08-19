from pydantic import BaseModel, Field


class ExtractTextRequest(BaseModel):
    file_base64: str = Field(..., description="Base64-encoded file bytes")
    filename: str = Field(..., description="Original filename including extension")


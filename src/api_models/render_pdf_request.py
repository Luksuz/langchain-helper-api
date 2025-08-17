from pydantic import BaseModel, Field


class RenderPdfRequest(BaseModel):
    html: str = Field(..., description="AI-generated HTML to render into PDF")



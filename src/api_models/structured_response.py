from typing import Any, Dict

from pydantic import BaseModel, Field


class StructuredGenResponse(BaseModel):
    data: Dict[str, Any] = Field(..., description="Structured output from the model")
    model_name: str = Field(..., description="Model used for generation")


from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class StructuredGenRequest(BaseModel):
    """Request body for generating structured output.

    - system_prompt: optional system instruction to steer model behavior
    - user_prompt: the main user message
    - structure: either a JSON Schema (object with type/properties) or an example dict
    - model: OpenAI chat model name
    - temperature: sampling temperature
    """

    system_prompt: Optional[str] = Field(
        default=None, description="Optional system instruction for the model"
    )
    user_prompt: str = Field(..., description="User message for the model")
    structure: Dict[str, Any] = Field(
        ..., description="JSON Schema or example dictionary describing desired output"
    )
    model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI chat model name, e.g. gpt-4o, gpt-4o-mini, o4-mini",
    )
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)


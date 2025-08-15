from typing import Optional

from pydantic import BaseModel, Field


class EnhancePromptRequest(BaseModel):
    user_description: str = Field(
        ..., description="Natural language description of the desired app"
    )
    model: str = Field(
        default="gpt-5-mini",
        description="OpenAI chat model name (for enhancement)",
    )
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)



from typing import Optional

from pydantic import BaseModel, Field


class ClientMessageRequest(BaseModel):
    user_description: str = Field(
        ..., description="App idea to tailor the outreach message to"
    )
    website: Optional[str] = Field(
        default="https://www.lukamindek.com",
        description="Website to include in signature",
    )
    github: Optional[str] = Field(
        default="https://www.github.com/luksuz",
        description="GitHub profile to include in signature",
    )
    linkedin: Optional[str] = Field(
        default="https://www.linkedin.com/in/lukamindek/",
        description="LinkedIn profile to include in signature",
    )
    model: str = Field(
        default="gpt-4o-mini", description="OpenAI chat model name (for message)"
    )
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)



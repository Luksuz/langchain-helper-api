from pydantic import BaseModel, Field


class BuilderPromptRequest(BaseModel):
    user_description: str = Field(
        ..., description="Natural language description of the desired app"
    )



from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(...)
    query: str = Field(...)
    top_k: int = Field(default=15, ge=1, le=50)


from typing import List, Literal
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(...)
    content: str = Field(...)


class ChatRequest(BaseModel):
    session_id: str = Field(...)
    messages: List[ChatMessage] = Field(...)
    top_k: int = Field(default=15, ge=1, le=50)


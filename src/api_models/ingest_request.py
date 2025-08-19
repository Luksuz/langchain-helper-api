from typing import List
from pydantic import BaseModel, Field


class IngestFile(BaseModel):
    filename: str = Field(...)
    file_base64: str = Field(...)


class IngestRequest(BaseModel):
    session_id: str = Field(..., description="UUID tying all chunks to a folder/session")
    files: List[IngestFile] = Field(default_factory=list, description="List of files to ingest")
    raw_texts: List[dict] = Field(
        default_factory=list,
        description="Optional list of {name, text} items for direct text ingestion",
    )


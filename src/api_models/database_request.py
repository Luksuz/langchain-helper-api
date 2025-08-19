from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DatabaseSetupRequest(BaseModel):
    sql_content: str = Field(..., description="SQL file contents to execute for database setup")
    connection_string: Optional[str] = Field(None, description="PostgreSQL connection string (uses env var if not provided)")


class DatabaseQueryRequest(BaseModel):
    sql_query: str = Field(..., description="SQL query to execute (SELECT, INSERT, UPDATE, DELETE, etc.)")
    connection_string: Optional[str] = Field(None, description="PostgreSQL connection string (uses env var if not provided)")


class DatabaseSetupResponse(BaseModel):
    success: bool = Field(...)
    message: str = Field(...)
    executed_statements: int = Field(...)


class DatabaseQueryResponse(BaseModel):
    success: bool = Field(...)
    columns: List[str] = Field(default_factory=list)
    rows: List[Dict[str, Any]] = Field(default_factory=list)
    row_count: int = Field(...)
    message: Optional[str] = Field(None)

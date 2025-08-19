from typing import Optional, List
from pydantic import BaseModel, Field


class SchemaGenerationRequest(BaseModel):
    project_description: str = Field(..., description="Description of the project and its data requirements")
    additional_requirements: Optional[str] = Field(None, description="Additional specific requirements for the database schema")
    model: Optional[str] = Field("gpt-4o-mini", description="OpenAI model to use for schema generation")
    temperature: Optional[float] = Field(0.1, description="Temperature for LLM generation")


class SchemaGenerationResponse(BaseModel):
    success: bool = Field(...)
    sql_schema: str = Field(..., description="Generated SQL schema with UUID-postfixed table names")
    app_uuid: str = Field(..., description="UUID used for table name postfixes")
    tables_created: List[str] = Field(..., description="List of table names that will be created")
    explanation: str = Field(..., description="Explanation of the generated schema")
    message: Optional[str] = Field(None, description="Error message if success is false")

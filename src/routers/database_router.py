from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..api_models.database_request import (
    DatabaseSetupRequest,
    DatabaseQueryRequest,
    DatabaseSetupResponse,
    DatabaseQueryResponse
)
from ..api_models.schema_generation_request import (
    SchemaGenerationRequest,
    SchemaGenerationResponse
)
from ..service.database_service import setup_database, query_database, validate_connection_string
from ..service.schema_generation_service import generate_database_schema

router = APIRouter()


@router.post("/setup-db", response_model=DatabaseSetupResponse)
def post_setup_database(body: DatabaseSetupRequest) -> DatabaseSetupResponse:
    """
    Execute SQL setup statements to create database schema and tables.
    
    Accepts a .sql file content and executes it against a PostgreSQL database.
    Useful for setting up database schemas for v0 applications.
    """
    try:
        print(f"[SETUP_DB] Database setup request received")
        print(f"[SETUP_DB] SQL content length: {len(body.sql_content)}")
        
        # Validate connection string if provided
        if body.connection_string and not validate_connection_string(body.connection_string):
            raise HTTPException(status_code=400, detail="Invalid PostgreSQL connection string format")
        
        # Execute database setup
        success, message, executed_count = setup_database(body.sql_content, body.connection_string)
        
        if success:
            print(f"[SETUP_DB] Setup completed successfully: {executed_count} statements")
        else:
            print(f"[SETUP_DB] Setup failed: {message}")
            
        return DatabaseSetupResponse(
            success=success,
            message=message,
            executed_statements=executed_count
        )
        
    except Exception as exc:
        error_msg = f"Failed to setup database: {str(exc)}"
        print(f"[SETUP_DB] Error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/query-db", response_model=DatabaseQueryResponse)
def post_query_database(body: DatabaseQueryRequest) -> DatabaseQueryResponse:
    """
    Execute SQL queries against the database and return results in JSON format.
    
    Supports all SQL statements: SELECT, INSERT, UPDATE, DELETE, etc.
    Returns results with columns and rows in a standardized format.
    """
    try:
        print(f"[QUERY_DB] Database query request received")
        print(f"[QUERY_DB] Query: {body.sql_query[:100]}...")
        
        # Validate connection string if provided
        if body.connection_string and not validate_connection_string(body.connection_string):
            raise HTTPException(status_code=400, detail="Invalid PostgreSQL connection string format")
        
        # Execute database query
        success, columns, rows, row_count, message = query_database(body.sql_query, body.connection_string)
        
        if success:
            print(f"[QUERY_DB] Query completed successfully: {row_count} rows returned")
        else:
            print(f"[QUERY_DB] Query failed: {message}")
            
        return DatabaseQueryResponse(
            success=success,
            columns=columns,
            rows=rows,
            row_count=row_count,
            message=message if not success else None
        )
        
    except Exception as exc:
        error_msg = f"Failed to query database: {str(exc)}"
        print(f"[QUERY_DB] Error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/generate-schema", response_model=SchemaGenerationResponse)
def post_generate_schema(body: SchemaGenerationRequest) -> SchemaGenerationResponse:
    """
    Generate a database schema based on project description using AI.
    
    Analyzes the project requirements and creates appropriate PostgreSQL tables
    with UUID-postfixed names to avoid conflicts between different applications.
    """
    try:
        print(f"[GENERATE_SCHEMA] Schema generation request received")
        print(f"[GENERATE_SCHEMA] Project: {body.project_description[:100]}...")
        
        # Generate database schema using AI
        success, sql_schema, app_uuid, tables, explanation, error_message = generate_database_schema(
            body.project_description,
            body.additional_requirements,
            body.model,
            body.temperature
        )
        
        if success:
            print(f"[GENERATE_SCHEMA] Schema generated successfully: {len(tables)} tables")
        else:
            print(f"[GENERATE_SCHEMA] Schema generation failed: {error_message}")
            
        return SchemaGenerationResponse(
            success=success,
            sql_schema=sql_schema,
            app_uuid=app_uuid,
            tables_created=tables,
            explanation=explanation,
            message=error_message if not success else None
        )
        
    except Exception as exc:
        error_msg = f"Failed to generate schema: {str(exc)}"
        print(f"[GENERATE_SCHEMA] Error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/db-health")
def get_database_health() -> JSONResponse:
    """Check if database connection is working."""
    try:
        success, columns, rows, row_count, message = query_database("SELECT 1 as health_check")
        
        if success and row_count > 0:
            return JSONResponse({
                "status": "healthy",
                "message": "Database connection successful"
            })
        else:
            return JSONResponse({
                "status": "unhealthy",
                "message": message
            }, status_code=503)
            
    except Exception as exc:
        return JSONResponse({
            "status": "unhealthy",
            "message": f"Database health check failed: {str(exc)}"
        }, status_code=503)

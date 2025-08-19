from __future__ import annotations

import re
import uuid
from typing import Tuple, List

from ..ai_models.openai_model import get_openai_chat_model


def generate_database_schema(project_description: str, additional_requirements: str = None, model: str = "gpt-4o-mini", temperature: float = 0.1) -> Tuple[bool, str, str, List[str], str, str]:
    """
    Generate a database schema based on project description.
    
    Returns:
        Tuple of (success: bool, sql_schema: str, app_uuid: str, tables: List[str], explanation: str, error_message: str)
    """
    print(f"[SCHEMA_GEN] Starting schema generation")
    print(f"[SCHEMA_GEN] Project: {project_description[:100]}...")
    
    try:
        # Generate unique UUID for this app
        app_uuid = str(uuid.uuid4()).replace('-', '')[:8]  # Use first 8 chars for readability
        print(f"[SCHEMA_GEN] Generated app UUID: {app_uuid}")
        
        # Build the system prompt for schema generation
        system_prompt = f"""You are a database architect that creates SIMPLE and RELIABLE PostgreSQL schemas for web applications.

CRITICAL REQUIREMENTS:
1. All table names MUST be postfixed with "_{app_uuid}" (e.g., "users_{app_uuid}", "products_{app_uuid}")
2. Always include an 'id' column as SERIAL PRIMARY KEY for each table
3. Use ONLY basic PostgreSQL data types: VARCHAR, TEXT, INTEGER, DECIMAL, BOOLEAN, TIMESTAMP
4. Include created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP for each table
5. Add foreign key relationships using REFERENCES
6. Include sample INSERT statements with realistic data

FORBIDDEN - DO NOT USE:
- Triggers or functions
- Dollar-quoted strings ($$)
- Array types (TEXT[], VARCHAR[], etc.) - use TEXT or VARCHAR instead
- JSON or JSONB types - use TEXT instead
- Complex constraints beyond NOT NULL, UNIQUE, and REFERENCES
- Advanced PostgreSQL features
- Stored procedures or custom functions
- Complex UPDATE triggers
- ARRAY constructors in INSERT statements
- Complex sample data with quotes, apostrophes, or special characters
- Long text strings in sample data
- Names with apostrophes or quotes (use simple names like "John Doe")

Keep it SIMPLE and RELIABLE. Focus on basic table structure that works.

Example output format:
CREATE TABLE users_{app_uuid} (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE articles_{app_uuid} (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_{app_uuid}_email ON users_{app_uuid}(email);
CREATE INDEX idx_articles_{app_uuid}_title ON articles_{app_uuid}(title);

Return ONLY the SQL schema - no explanations, no markdown, no complex features."""
        
        # Build user prompt
        user_prompt = f"Project Description: {project_description}"
        if additional_requirements:
            user_prompt += f"\n\nAdditional Requirements: {additional_requirements}"
        
        print(f"[SCHEMA_GEN] Calling OpenAI with model: {model}")
        print(f"[SCHEMA_GEN] User prompt: {user_prompt}")
        
        # Generate schema using OpenAI
        chat_model = get_openai_chat_model(model, temperature)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = chat_model.invoke(messages)
        sql_schema = response.content.strip()
        
        print(f"[SCHEMA_GEN] Generated schema length: {len(sql_schema)} characters")
        
        # Extract table names from the generated schema
        tables = _extract_table_names(sql_schema, app_uuid)
        print(f"[SCHEMA_GEN] Extracted {len(tables)} tables: {tables}")
        
        # Generate explanation
        explanation = _generate_explanation(project_description, tables, app_uuid)
        
        print(f"[SCHEMA_GEN] Schema generation completed successfully")
        return True, sql_schema, app_uuid, tables, explanation, ""
        
    except Exception as e:
        error_msg = f"Error generating database schema: {str(e)}"
        print(f"[SCHEMA_GEN] Error: {error_msg}")
        return False, "", "", [], "", error_msg


def _extract_table_names(sql_schema: str, app_uuid: str) -> List[str]:
    """Extract table names from the generated SQL schema."""
    # Pattern to match CREATE TABLE statements
    pattern = r'CREATE TABLE\s+(\w+_' + re.escape(app_uuid) + r')\s*\('
    matches = re.findall(pattern, sql_schema, re.IGNORECASE)
    return matches


def _generate_explanation(project_description: str, tables: List[str], app_uuid: str) -> str:
    """Generate a human-readable explanation of the schema."""
    explanation = f"Generated database schema for: {project_description}\n\n"
    explanation += f"App UUID: {app_uuid}\n\n"
    explanation += f"Created {len(tables)} tables:\n"
    
    for table in tables:
        # Remove UUID suffix for display
        clean_name = table.replace(f"_{app_uuid}", "")
        explanation += f"- {table} (stores {clean_name} data)\n"
    
    explanation += f"\nAll tables are isolated with UUID suffix '_{app_uuid}' to prevent conflicts with other applications."
    explanation += f"\nYou can now use /setup-db to create these tables and /query-db to interact with them."
    
    return explanation

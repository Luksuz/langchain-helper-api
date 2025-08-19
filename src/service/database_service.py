from __future__ import annotations

import os
import re
from typing import List, Dict, Any, Tuple

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


def get_database_engine(connection_string: str = None) -> Engine:
    """Get database engine using provided connection string or environment variable."""
    conn_str = connection_string or os.environ.get("DATABASE_URL") or os.environ.get("PGVECTOR_URL")
    if not conn_str:
        raise ValueError("No database connection string provided. Set DATABASE_URL environment variable or pass connection_string.")
    
    return create_engine(conn_str)


def setup_database(sql_content: str, connection_string: str = None) -> Tuple[bool, str, int]:
    """
    Execute SQL setup statements against the database.
    
    Returns:
        Tuple of (success: bool, message: str, executed_statements: int)
    """
    print(f"[DB_SETUP] Starting database setup")
    print(f"[DB_SETUP] SQL content length: {len(sql_content)} characters")
    
    try:
        engine = get_database_engine(connection_string)
        print(f"[DB_SETUP] Database connection established")
        
        # Parse SQL content into individual statements
        statements = _parse_sql_statements(sql_content)
        print(f"[DB_SETUP] Parsed {len(statements)} SQL statements")
        
        executed_count = 0
        
        with engine.begin() as conn:
            print(f"[DB_SETUP] Executing {len(statements)} SQL statements")
            
            for i, statement in enumerate(statements):
                if statement.strip():
                    print(f"[DB_SETUP] Executing statement {i+1}/{len(statements)}: {statement[:100]}...")
                    conn.execute(text(statement))
                    executed_count += 1
                    print(f"[DB_SETUP] Statement {i+1} completed successfully")
            
            print(f"[DB_SETUP] Transaction committed successfully")
        
        message = f"Successfully executed {executed_count} SQL statements"
        print(f"[DB_SETUP] {message}")
        return True, message, executed_count
        
    except SQLAlchemyError as e:
        error_msg = f"Database error during setup: {str(e)}"
        print(f"[DB_SETUP] Error: {error_msg}")
        return False, error_msg, 0
    except Exception as e:
        error_msg = f"Unexpected error during database setup: {str(e)}"
        print(f"[DB_SETUP] Error: {error_msg}")
        return False, error_msg, 0


def query_database(sql_query: str, connection_string: str = None) -> Tuple[bool, List[str], List[Dict[str, Any]], int, str]:
    """
    Execute a SELECT query against the database and return results.
    
    Returns:
        Tuple of (success: bool, columns: List[str], rows: List[Dict], row_count: int, message: str)
    """
    print(f"[DB_QUERY] Starting database query")
    print(f"[DB_QUERY] Query: {sql_query[:100]}...")
    
    try:    
        engine = get_database_engine(connection_string)
        print(f"[DB_QUERY] Database connection established")
        
        with engine.begin() as conn:
            print(f"[DB_QUERY] Executing query...")
            result = conn.execute(text(sql_query))
            
            # Get column names
            columns = list(result.keys()) if result.keys() else []
            print(f"[DB_QUERY] Found {len(columns)} columns: {columns}")
            
            # Get all rows as dictionaries
            rows = []
            for row in result:
                row_dict = {col: _serialize_value(row[i]) for i, col in enumerate(columns)}
                rows.append(row_dict)
            
            row_count = len(rows)
            print(f"[DB_QUERY] Retrieved {row_count} rows")
            
            message = f"Successfully executed query, returned {row_count} rows"
            return True, columns, rows, row_count, message
            
    except SQLAlchemyError as e:
        error_msg = f"Database error during query: {str(e)}"
        print(f"[DB_QUERY] Error: {error_msg}")
        return False, [], [], 0, error_msg
    except Exception as e:
        error_msg = f"Unexpected error during query: {str(e)}"
        print(f"[DB_QUERY] Error: {error_msg}")
        return False, [], [], 0, error_msg


def _parse_sql_statements(sql_content: str) -> List[str]:
    """
    Parse SQL content into individual executable statements.
    
    Handles:
    - Multi-line statements
    - Line comments (-- comment)
    - Block comments (/* comment */)
    - Empty lines and whitespace
    - Proper semicolon splitting
    """
    print(f"[SQL_PARSE] Processing SQL content ({len(sql_content)} chars)")
    
    # Remove block comments /* ... */
    sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)
    
    # Split into lines and process line comments
    lines = []
    for line in sql_content.split('\n'):
        # Remove line comments (-- comment)
        if '--' in line:
            line = line[:line.index('--')]
        # Keep non-empty lines
        line = line.strip()
        if line:
            lines.append(line)
    
    # Join lines back and split by semicolons
    clean_sql = ' '.join(lines)
    print(f"[SQL_PARSE] Cleaned SQL: {clean_sql[:200]}...")
    
    # Split on semicolons and clean up
    raw_statements = clean_sql.split(';')
    statements = []
    
    for statement in raw_statements:
        statement = statement.strip()
        if statement:
            statements.append(statement)
            print(f"[SQL_PARSE] Found statement: {statement[:100]}...")
    
    print(f"[SQL_PARSE] Extracted {len(statements)} statements")
    return statements


def _serialize_value(value: Any) -> Any:
    """Serialize database values to JSON-compatible types."""
    if value is None:
        return None
    elif hasattr(value, 'isoformat'):  # datetime objects
        return value.isoformat()
    elif hasattr(value, '__str__') and not isinstance(value, (str, int, float, bool)):
        return str(value)
    else:
        return value


def validate_connection_string(connection_string: str) -> bool:
    """Validate that connection string looks like a valid PostgreSQL URL."""
    pattern = r'^postgresql://.*'
    return bool(re.match(pattern, connection_string))

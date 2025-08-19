### /setup-db — Execute SQL setup scripts to create database schema

Use this to create database tables, indexes, and insert initial data from SQL files. Perfect for setting up database schemas for v0 applications that need persistent data storage.

**Features:**
- Execute multiple SQL statements from .sql file content
- Transaction safety - all statements succeed or all fail
- Supports CREATE TABLE, CREATE INDEX, INSERT, and other DDL/DML statements
- Returns count of successfully executed statements

Sample request
```http
POST /setup-db
Content-Type: application/json

{
  "sql_content": "CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR(100) UNIQUE NOT NULL, email VARCHAR(255) UNIQUE NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP); INSERT INTO users (username, email) VALUES ('admin', 'admin@example.com');"
}
```

Sample response
```json
{
  "success": true,
  "message": "Successfully executed 2 SQL statements",
  "executed_statements": 2
}
```

**Use Cases:**
- Setting up database schema for new v0 projects
- Creating sample data for development/testing
- Database migrations and updates
- Initializing application-specific tables and indexes

**Parameters:**
- `sql_content`: String containing SQL statements separated by semicolons
- `connection_string` (optional): PostgreSQL connection string (uses environment variable if not provided)

**Environment Variables:**
- `DATABASE_URL` or `PGVECTOR_URL`: Default PostgreSQL connection string

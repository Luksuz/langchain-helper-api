### /query-db — Execute SQL queries and return structured results

Use this to execute any SQL query against your database and get results in a standardized JSON format. Perfect for building dynamic applications that need full database interaction with PostgreSQL.

**Features:**
- Execute any SQL statements: SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, etc.
- Returns results with column names and typed data for SELECT queries
- Handles various PostgreSQL data types (timestamps, JSON, arrays, etc.)
- Standardized response format for easy frontend integration

Sample request
```http
POST /query-db
Content-Type: application/json

{
  "sql_query": "SELECT id, username, email, created_at FROM users WHERE created_at > NOW() - INTERVAL '7 days' ORDER BY created_at DESC"
}
```

Sample response
```json
{
  "success": true,
  "columns": ["id", "username", "email", "created_at"],
  "rows": [
    {
      "id": 1,
      "username": "john_doe", 
      "email": "john@example.com",
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "id": 2,
      "username": "jane_smith",
      "email": "jane@example.com", 
      "created_at": "2024-01-14T15:45:00"
    }
  ],
  "row_count": 2
}
```

**Use Cases:**
- Fetching user data for profiles and dashboards (SELECT)
- Creating, updating, and deleting records (INSERT, UPDATE, DELETE)
- Managing database structure (CREATE TABLE, ALTER TABLE, DROP TABLE)
- Loading dynamic content and generating reports
- Building fully interactive v0 applications with database persistence
- Real-time data operations and transactions

**Parameters:**
- `sql_query`: Any SQL statement to execute (SELECT, INSERT, UPDATE, DELETE, CREATE, etc.)
- `connection_string` (optional): PostgreSQL connection string (uses environment variable if not provided)

**Response Format:**
- `success`: Boolean indicating query success
- `columns`: Array of column names in order
- `rows`: Array of objects with column_name: value pairs
- `row_count`: Total number of rows returned
- `message`: Error message if success is false

**Environment Variables:**
- `DATABASE_URL` or `PGVECTOR_URL`: Default PostgreSQL connection string

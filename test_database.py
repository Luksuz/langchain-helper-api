import os
import requests


BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def test_database_setup():
    """Test database setup with a sample SQL schema."""
    
    # Sample SQL for a simple task management system
    sample_sql = """
    -- Create tasks table
    CREATE TABLE IF NOT EXISTS tasks (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        completed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create users table
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Insert some sample data
    INSERT INTO users (username, email) VALUES 
        ('john_doe', 'john@example.com'),
        ('jane_smith', 'jane@example.com')
    ON CONFLICT (email) DO NOTHING;

    INSERT INTO tasks (title, description, completed) VALUES 
        ('Setup database', 'Create initial database schema', true),
        ('Test API endpoints', 'Verify all endpoints work correctly', false),
        ('Write documentation', 'Document the new database features', false)
    ON CONFLICT DO NOTHING;
    """
    
    payload = {
        "sql_content": sample_sql
    }
    
    url = f"{BASE_URL}/setup-db"
    resp = requests.post(url, json=payload)
    print("POST /setup-db status:", resp.status_code)
    
    try:
        result = resp.json()
        print("=== DATABASE SETUP RESULT ===")
        print(f"Success: {result.get('success', 'N/A')}")
        print(f"Message: {result.get('message', 'N/A')}")
        print(f"Executed Statements: {result.get('executed_statements', 'N/A')}")
        print()
        return result.get('success', False)
    except Exception as e:
        print(f"Error parsing setup response: {e}")
        print(resp.text)
        return False


def test_database_query():
    """Test database queries with sample SELECT statements."""
    
    test_queries = [
        "SELECT * FROM users ORDER BY created_at DESC",
        "SELECT COUNT(*) as total_tasks, SUM(CASE WHEN completed THEN 1 ELSE 0 END) as completed_tasks FROM tasks",
        "SELECT title, completed, created_at FROM tasks WHERE completed = false"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"=== QUERY TEST {i} ===")
        print(f"Query: {query}")
        
        payload = {
            "sql_query": query
        }
        
        url = f"{BASE_URL}/query-db"
        resp = requests.post(url, json=payload)
        print(f"Status: {resp.status_code}")
        
        try:
            result = resp.json()
            if result.get('success'):
                print(f"Columns: {result.get('columns', [])}")
                print(f"Row Count: {result.get('row_count', 0)}")
                print("Sample Rows:")
                for j, row in enumerate(result.get('rows', [])[:3]):  # Show first 3 rows
                    print(f"  Row {j+1}: {row}")
                if result.get('row_count', 0) > 3:
                    print(f"  ... and {result.get('row_count', 0) - 3} more rows")
            else:
                print(f"Query failed: {result.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"Error parsing query response: {e}")
            print(resp.text)
        print()


def test_database_health():
    """Test database health check."""
    url = f"{BASE_URL}/db-health"
    resp = requests.get(url)
    print("GET /db-health status:", resp.status_code)
    
    try:
        result = resp.json()
        print("=== DATABASE HEALTH ===")
        print(f"Status: {result.get('status', 'N/A')}")
        print(f"Message: {result.get('message', 'N/A')}")
        print()
    except Exception as e:
        print(f"Error parsing health response: {e}")
        print(resp.text)


def test_full_sql_operations():
    """Test that all SQL operations work correctly."""
    print("=== FULL SQL OPERATIONS TEST ===")
    
    operations = [
        ("CREATE temporary table", "CREATE TEMPORARY TABLE temp_test (id SERIAL, name VARCHAR(50))"),
        ("INSERT into temp table", "INSERT INTO temp_test (name) VALUES ('test_record') RETURNING id, name"),
        ("SELECT from temp table", "SELECT * FROM temp_test"),
        ("UPDATE temp table", "UPDATE temp_test SET name = 'updated_record' WHERE id = 1 RETURNING *"),
        ("DELETE from temp table", "DELETE FROM temp_test WHERE id = 1 RETURNING *")
    ]
    
    for description, query in operations:
        print(f"Testing {description}: {query}")
        
        payload = {
            "sql_query": query
        }
        
        url = f"{BASE_URL}/query-db"
        resp = requests.post(url, json=payload)
        
        try:
            result = resp.json()
            if result.get('success'):
                print(f"✅ {description} successful")
                if result.get('rows'):
                    print(f"   Returned {result.get('row_count', 0)} rows")
            else:
                print(f"❌ {description} failed: {result.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"Error parsing response: {e}")
    print()


def main():
    """Run all database tests."""
    print("🚀 Testing Database API Endpoints\n")
    
    # Test health check first
    test_database_health()
    
    # Test database setup
    setup_success = test_database_setup()
    
    if setup_success:
        # Test queries if setup succeeded
        test_database_query()
        
        # Test full SQL operations
        test_full_sql_operations()
    else:
        print("⚠️  Skipping query tests due to setup failure")
    
    print("✅ Database API tests completed!")


if __name__ == "__main__":
    main()

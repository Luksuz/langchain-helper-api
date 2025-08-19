import os
import requests


BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def test_safe_schema_generation():
    """Test that generated schemas have safe SQL without syntax errors."""
    print("=== SAFE SCHEMA GENERATION TEST ===")
    
    # Test with a description that might tempt the AI to use complex data
    payload = {
        "project_description": "Create a news article management system with authors, articles with quotes and complex content, user comments with apostrophes in names like O'Connor, and metadata extraction"
    }
    
    url = f"{BASE_URL}/generate-schema"
    resp = requests.post(url, json=payload)
    print(f"POST /generate-schema status: {resp.status_code}")
    
    try:
        result = resp.json()
        
        if not result.get('success'):
            print(f"❌ Schema generation failed: {result.get('message', 'Unknown error')}")
            return False
            
        sql_schema = result.get('sql_schema', '')
        app_uuid = result.get('app_uuid', '')
        
        print("✅ Schema generated successfully")
        print(f"App UUID: {app_uuid}")
        print(f"Tables: {result.get('tables_created', [])}")
        print(f"SQL length: {len(sql_schema)} characters")
        
        # Check for dangerous patterns in the SQL
        dangerous_patterns = [
            "$$",  # Dollar quoted strings
            "ARRAY[",  # Array constructors
            "'s ",  # Apostrophes in names
            ''"'',  # Nested quotes
            "O'",  # Names with apostrophes
            "can't",  # Contractions
            "it's",  # More contractions
        ]
        
        print("\n--- SAFETY CHECKS ---")
        found_issues = []
        for pattern in dangerous_patterns:
            if pattern in sql_schema:
                found_issues.append(pattern)
                print(f"⚠️  Found dangerous pattern: {pattern}")
                
        if not found_issues:
            print("✅ No dangerous patterns found in SQL")
        
        # Show a preview of the SQL
        print("\n--- SQL PREVIEW ---")
        lines = sql_schema.split('\n')
        for i, line in enumerate(lines[:20]):  # Show first 20 lines
            print(f"{i+1:2d}: {line}")
        if len(lines) > 20:
            print(f"... and {len(lines) - 20} more lines")
            
        # Test the actual database setup
        return test_database_setup_safe(sql_schema, app_uuid)
        
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(resp.text)
        return False


def test_database_setup_safe(sql_schema: str, app_uuid: str):
    """Test that the generated schema can be setup without SQL errors."""
    print(f"\n=== DATABASE SETUP SAFETY TEST (UUID: {app_uuid}) ===")
    
    payload = {
        "sql_content": sql_schema
    }
    
    url = f"{BASE_URL}/setup-db"
    resp = requests.post(url, json=payload)
    print(f"POST /setup-db status: {resp.status_code}")
    
    try:
        result = resp.json()
        if result.get('success'):
            print(f"✅ Database setup successful: {result.get('executed_statements', 0)} statements")
            
            # Test basic query to verify tables exist
            test_basic_query(app_uuid)
            return True
            
        else:
            print(f"❌ Database setup failed: {result.get('message', 'Unknown error')}")
            # Show the problematic SQL for debugging
            print("\n--- PROBLEMATIC SQL ---")
            print(sql_schema)
            return False
            
    except Exception as e:
        print(f"Error during database setup: {e}")
        return False


def test_basic_query(app_uuid: str):
    """Test basic querying of the created tables."""
    print(f"\n=== BASIC QUERY TEST (UUID: {app_uuid}) ===")
    
    # Query to see what tables were created
    payload = {
        "sql_query": f"SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%_{app_uuid}' AND table_schema = 'public'"
    }
    
    url = f"{BASE_URL}/query-db"
    resp = requests.post(url, json=payload)
    
    try:
        result = resp.json()
        if result.get('success'):
            tables_found = [row['table_name'] for row in result.get('rows', [])]
            print(f"✅ Found {len(tables_found)} tables:")
            for table in tables_found:
                print(f"  - {table}")
                
            # Try to query one of the tables to see if sample data was inserted safely
            if tables_found:
                test_table = tables_found[0]
                payload = {"sql_query": f"SELECT * FROM {test_table} LIMIT 3"}
                resp = requests.post(url, json=payload)
                result = resp.json()
                
                if result.get('success'):
                    print(f"✅ Sample data query successful for {test_table}")
                    print(f"   Columns: {result.get('columns', [])}")
                    print(f"   Rows: {len(result.get('rows', []))}")
                else:
                    print(f"⚠️  Sample data query failed: {result.get('message', 'Unknown')}")
                    
        else:
            print(f"❌ Table lookup failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"Error during basic query: {e}")


def main():
    """Run the safe schema generation test."""
    print("🚀 Testing Safe Schema Generation\n")
    
    success = test_safe_schema_generation()
    
    if success:
        print("\n✅ Safe schema generation test PASSED!")
        print("The schema generator now creates SQL without syntax errors!")
    else:
        print("\n❌ Safe schema generation test FAILED!")
        print("The schema generator still has issues that need fixing.")


if __name__ == "__main__":
    main()

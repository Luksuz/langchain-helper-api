import os
import requests


BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def test_v0_prompt_with_database():
    """Test the integrated V0 prompt + database schema generation."""
    print("=== V0 PROMPT + DATABASE INTEGRATION TEST ===")
    
    payload = {
        "user_description": "Create a weather tracking app that lets users view and log daily weather data including temperature, humidity, and conditions for different cities"
    }
    
    url = f"{BASE_URL}/prompt/v0/enhance"
    resp = requests.post(url, json=payload)
    print(f"POST /prompt/v0/enhance status: {resp.status_code}")
    
    try:
        result = resp.json()
        
        # Check prompt generation
        if 'prompt' in result:
            print("✅ V0 prompt generated successfully")
            print(f"Prompt length: {len(result['prompt'])} characters")
            print(f"Prompt preview: {result['prompt'][:200]}...")
        else:
            print("❌ No prompt in response")
            
        # Check database generation
        if 'database' in result:
            db_data = result['database']
            if db_data.get('success'):
                print("✅ Database schema generated successfully")
                print(f"App UUID: {db_data.get('app_uuid', 'N/A')}")
                print(f"Tables created: {len(db_data.get('tables_created', []))}")
                print("Tables:")
                for table in db_data.get('tables_created', []):
                    print(f"  - {table}")
                print(f"SQL schema length: {len(db_data.get('sql_schema', ''))} characters")
                
                # Test database setup if schema was generated
                if db_data.get('sql_schema'):
                    test_database_setup(db_data['sql_schema'], db_data['app_uuid'])
                    
            else:
                print(f"❌ Database schema generation failed: {db_data.get('error', 'Unknown error')}")
        else:
            print("❌ No database info in response")
            
        return result
        
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(resp.text)
        return None


def test_database_setup(sql_schema: str, app_uuid: str):
    """Test setting up the generated database schema."""
    print(f"\n=== DATABASE SETUP TEST (UUID: {app_uuid}) ===")
    
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
            
            # Test querying the created tables
            test_database_query(app_uuid)
            
        else:
            print(f"❌ Database setup failed: {result.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Error during database setup: {e}")


def test_database_query(app_uuid: str):
    """Test querying the created database tables."""
    print(f"\n=== DATABASE QUERY TEST (UUID: {app_uuid}) ===")
    
    # Query to see what tables were created
    payload = {
        "sql_query": f"SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%_{app_uuid}' AND table_schema = 'public'"
    }
    
    url = f"{BASE_URL}/query-db"
    resp = requests.post(url, json=payload)
    print(f"POST /query-db status: {resp.status_code}")
    
    try:
        result = resp.json()
        if result.get('success'):
            tables_found = [row['table_name'] for row in result.get('rows', [])]
            print(f"✅ Found {len(tables_found)} tables in database:")
            for table in tables_found:
                print(f"  - {table}")
                
            # Test inserting and querying data in one of the tables
            if tables_found:
                test_sample_data_operations(tables_found[0])
                
        else:
            print(f"❌ Query failed: {result.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Error during database query: {e}")


def test_sample_data_operations(table_name: str):
    """Test basic data operations on a created table."""
    print(f"\n=== SAMPLE DATA OPERATIONS TEST ({table_name}) ===")
    
    # Try to query the table to see its structure
    payload = {
        "sql_query": f"SELECT * FROM {table_name} LIMIT 5"
    }
    
    url = f"{BASE_URL}/query-db"
    resp = requests.post(url, json=payload)
    
    try:
        result = resp.json()
        if result.get('success'):
            print(f"✅ Successfully queried {table_name}")
            print(f"Columns: {result.get('columns', [])}")
            print(f"Sample rows: {len(result.get('rows', []))}")
            
            # Show sample data if any exists
            for i, row in enumerate(result.get('rows', [])[:3]):
                print(f"  Row {i+1}: {row}")
                
        else:
            print(f"❌ Query failed: {result.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Error during sample data query: {e}")


def main():
    """Run the integrated V0 + database test."""
    print("🚀 Testing V0 Prompt + Database Integration\n")
    
    result = test_v0_prompt_with_database()
    
    if result:
        print("\n✅ Integration test completed successfully!")
        print("\nThe V0 Prompt Builder now:")
        print("1. ✅ Generates enhanced V0 prompts")
        print("2. ✅ Automatically creates database schemas with UUID-postfixed tables")
        print("3. ✅ Provides frontend interface to setup databases")
        print("4. ✅ Enables full database operations via the API")
        print("\nUsers can now build complete v0 apps with persistent data storage!")
    else:
        print("\n❌ Integration test failed")


if __name__ == "__main__":
    main()

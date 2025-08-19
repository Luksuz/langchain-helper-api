import os
import requests


BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def test_insert_statement():
    """Test that INSERT statements work without the 'does not return rows' error."""
    print("=== INSERT STATEMENT FIX TEST ===")
    
    # First create a simple test table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS test_insert_fix (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    print("1. Creating test table...")
    payload = {"sql_content": create_table_sql}
    resp = requests.post(f"{BASE_URL}/setup-db", json=payload)
    
    try:
        result = resp.json()
        if result.get('success'):
            print("✅ Test table created successfully")
        else:
            print(f"❌ Failed to create test table: {result.get('message')}")
            return
    except Exception as e:
        print(f"❌ Error creating test table: {e}")
        return

    # Now test INSERT statement
    print("\n2. Testing INSERT statement...")
    insert_sql = """
    INSERT INTO test_insert_fix (name, description) 
    VALUES ('Test Item', 'This is a test description')
    """
    
    payload = {"sql_query": insert_sql}
    resp = requests.post(f"{BASE_URL}/query-db", json=payload)
    
    try:
        result = resp.json()
        if result.get('success'):
            print("✅ INSERT statement executed successfully")
            print(f"Affected rows: {result.get('row_count', 0)}")
            print(f"Message: {result.get('message', 'N/A')}")
        else:
            print(f"❌ INSERT failed: {result.get('message')}")
            return
    except Exception as e:
        print(f"❌ Error executing INSERT: {e}")
        return

    # Test UPDATE statement  
    print("\n3. Testing UPDATE statement...")
    update_sql = """
    UPDATE test_insert_fix 
    SET description = 'Updated description' 
    WHERE name = 'Test Item'
    """
    
    payload = {"sql_query": update_sql}
    resp = requests.post(f"{BASE_URL}/query-db", json=payload)
    
    try:
        result = resp.json()
        if result.get('success'):
            print("✅ UPDATE statement executed successfully")
            print(f"Affected rows: {result.get('row_count', 0)}")
        else:
            print(f"❌ UPDATE failed: {result.get('message')}")
    except Exception as e:
        print(f"❌ Error executing UPDATE: {e}")

    # Test SELECT to verify data
    print("\n4. Testing SELECT to verify data...")
    select_sql = "SELECT * FROM test_insert_fix"
    
    payload = {"sql_query": select_sql}
    resp = requests.post(f"{BASE_URL}/query-db", json=payload)
    
    try:
        result = resp.json()
        if result.get('success'):
            print("✅ SELECT statement executed successfully")
            print(f"Columns: {result.get('columns', [])}")
            print(f"Rows: {len(result.get('rows', []))}")
            for i, row in enumerate(result.get('rows', [])):
                print(f"  Row {i+1}: {row}")
        else:
            print(f"❌ SELECT failed: {result.get('message')}")
    except Exception as e:
        print(f"❌ Error executing SELECT: {e}")

    # Cleanup
    print("\n5. Cleaning up...")
    cleanup_sql = "DROP TABLE IF EXISTS test_insert_fix"
    payload = {"sql_query": cleanup_sql}
    resp = requests.post(f"{BASE_URL}/query-db", json=payload)
    
    try:
        result = resp.json()
        if result.get('success'):
            print("✅ Cleanup completed")
        else:
            print(f"⚠️  Cleanup warning: {result.get('message')}")
    except Exception as e:
        print(f"⚠️  Cleanup error: {e}")


def main():
    """Run the INSERT fix test."""
    print("🚀 Testing INSERT Statement Fix\n")
    test_insert_statement()
    print("\n✅ INSERT statement fix test completed!")


if __name__ == "__main__":
    main()

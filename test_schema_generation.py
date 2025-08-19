import os
import requests


BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def test_weather_app_schema():
    """Test schema generation for a weather tracking application."""
    print("=== WEATHER APP SCHEMA GENERATION ===")
    
    payload = {
        "project_description": "A weather tracking application that stores daily weather data including temperature, humidity, pressure, wind speed, and weather conditions for different cities",
        "additional_requirements": "Include historical data storage and ability to track multiple weather stations per city"
    }
    
    url = f"{BASE_URL}/generate-schema"
    resp = requests.post(url, json=payload)
    print(f"POST /generate-schema status: {resp.status_code}")
    
    try:
        result = resp.json()
        if result.get('success'):
            print("✅ Schema generation successful")
            print(f"App UUID: {result.get('app_uuid', 'N/A')}")
            print(f"Tables created: {len(result.get('tables_created', []))}")
            print("Tables:")
            for table in result.get('tables_created', []):
                print(f"  - {table}")
            print("\nGenerated SQL Schema:")
            print("=" * 50)
            print(result.get('sql_schema', 'No schema'))
            print("=" * 50)
            print(f"\nExplanation:\n{result.get('explanation', 'No explanation')}")
            return result.get('sql_schema', ''), result.get('app_uuid', '')
        else:
            print(f"❌ Schema generation failed: {result.get('message', 'Unknown error')}")
            return '', ''
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(resp.text)
        return '', ''


def test_ecommerce_schema():
    """Test schema generation for an e-commerce application."""
    print("\n=== E-COMMERCE SCHEMA GENERATION ===")
    
    payload = {
        "project_description": "An e-commerce platform with users, products, shopping cart, orders, payments, and inventory management",
        "additional_requirements": "Include product categories, reviews, discounts, and order tracking"
    }
    
    url = f"{BASE_URL}/generate-schema"
    resp = requests.post(url, json=payload)
    print(f"POST /generate-schema status: {resp.status_code}")
    
    try:
        result = resp.json()
        if result.get('success'):
            print("✅ Schema generation successful")
            print(f"App UUID: {result.get('app_uuid', 'N/A')}")
            print(f"Tables created: {len(result.get('tables_created', []))}")
            print("Tables:")
            for table in result.get('tables_created', []):
                print(f"  - {table}")
            return result.get('sql_schema', ''), result.get('app_uuid', '')
        else:
            print(f"❌ Schema generation failed: {result.get('message', 'Unknown error')}")
            return '', ''
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(resp.text)
        return '', ''


def test_schema_setup_and_query(sql_schema: str, app_uuid: str):
    """Test setting up the generated schema and querying it."""
    if not sql_schema or not app_uuid:
        print("⚠️  Skipping setup test - no schema generated")
        return
    
    print(f"\n=== TESTING SCHEMA SETUP (UUID: {app_uuid}) ===")
    
    # Setup the database schema
    setup_payload = {
        "sql_content": sql_schema
    }
    
    setup_url = f"{BASE_URL}/setup-db"
    setup_resp = requests.post(setup_url, json=setup_payload)
    print(f"POST /setup-db status: {setup_resp.status_code}")
    
    try:
        setup_result = setup_resp.json()
        if setup_result.get('success'):
            print(f"✅ Schema setup successful: {setup_result.get('executed_statements', 0)} statements")
            
            # Test a simple query to verify tables exist
            print("\n=== TESTING QUERY WITH UUID TABLES ===")
            
            # Try to query information_schema to see our tables
            query_payload = {
                "sql_query": f"SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%_{app_uuid}' AND table_schema = 'public'"
            }
            
            query_url = f"{BASE_URL}/query-db"
            query_resp = requests.post(query_url, json=query_payload)
            
            if query_resp.status_code == 200:
                query_result = query_resp.json()
                if query_result.get('success'):
                    tables_found = [row['table_name'] for row in query_result.get('rows', [])]
                    print(f"✅ Found {len(tables_found)} tables in database:")
                    for table in tables_found:
                        print(f"  - {table}")
                else:
                    print(f"❌ Query failed: {query_result.get('message', 'Unknown error')}")
            else:
                print(f"❌ Query request failed with status: {query_resp.status_code}")
                
        else:
            print(f"❌ Schema setup failed: {setup_result.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Error during setup/query test: {e}")


def test_blog_schema():
    """Test schema generation for a simple blog application."""
    print("\n=== BLOG SCHEMA GENERATION ===")
    
    payload = {
        "project_description": "A simple blog application with posts, authors, comments, and categories",
        "model": "gpt-4o-mini",
        "temperature": 0.0
    }
    
    url = f"{BASE_URL}/generate-schema"
    resp = requests.post(url, json=payload)
    print(f"POST /generate-schema status: {resp.status_code}")
    
    try:
        result = resp.json()
        if result.get('success'):
            print("✅ Schema generation successful")
            print(f"Tables: {', '.join(result.get('tables_created', []))}")
            return result.get('sql_schema', ''), result.get('app_uuid', '')
        else:
            print(f"❌ Schema generation failed: {result.get('message', 'Unknown error')}")
            return '', ''
    except Exception as e:
        print(f"Error parsing response: {e}")
        return '', ''


def main():
    """Run all schema generation tests."""
    print("🚀 Testing Schema Generation API\n")
    
    # Test weather app schema
    weather_sql, weather_uuid = test_weather_app_schema()
    test_schema_setup_and_query(weather_sql, weather_uuid)
    
    # Test e-commerce schema
    ecommerce_sql, ecommerce_uuid = test_ecommerce_schema()
    
    # Test blog schema  
    blog_sql, blog_uuid = test_blog_schema()
    
    print("\n✅ Schema generation tests completed!")
    print("\nNext steps:")
    print("1. Use the generated SQL with /setup-db to create tables")
    print("2. Use /query-db with the UUID-postfixed table names to interact with data")
    print("3. Each app has isolated tables thanks to UUID postfixes")


if __name__ == "__main__":
    main()

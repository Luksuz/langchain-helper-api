import os
import requests


BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def test_nextjs_api_routes_generation():
    """Test that the V0 prompt builder now generates Next.js API routes."""
    print("=== NEXT.JS API ROUTES GENERATION TEST ===")
    
    # Test with a news scraper that would need multiple endpoints
    payload = {
        "user_description": "I want a news scraper that can extract articles from URLs and store them for later searching and querying"
    }
    
    url = f"{BASE_URL}/prompt/v0/enhance"
    resp = requests.post(url, json=payload)
    print(f"POST /prompt/v0/enhance status: {resp.status_code}")
    
    try:
        result = resp.json()
        enhanced_prompt = result.get('prompt', '')
        
        print("✅ Enhanced prompt generated successfully")
        print(f"Prompt length: {len(enhanced_prompt)} characters")
        
        # Check for Next.js API route patterns
        nextjs_patterns = [
            "/api/",  # API routes
            "route.ts",  # Next.js app router file naming
            "export async function POST",  # Next.js API route pattern
            "https://langchain-helper-api-production.up.railway.app",  # Backend URL
            "fetch('/api/",  # Frontend calling local API routes
            "proxy",  # Should mention proxying
        ]
        
        print("\n--- NEXT.JS PATTERN CHECKS ---")
        found_patterns = []
        for pattern in nextjs_patterns:
            if pattern in enhanced_prompt:
                found_patterns.append(pattern)
                print(f"✅ Found Next.js pattern: {pattern}")
            else:
                print(f"❌ Missing pattern: {pattern}")
                
        # Check for anti-patterns (direct external calls)
        antipatterns = [
            "fetch('https://langchain-helper-api-production.up.railway.app",  # Direct external calls
            "axios.post('https://langchain-helper-api-production.up.railway.app",  # Direct external calls
        ]
        
        print("\n--- ANTI-PATTERN CHECKS ---")
        found_antipatterns = []
        for antipattern in antipatterns:
            if antipattern in enhanced_prompt:
                found_antipatterns.append(antipattern)
                print(f"⚠️  Found anti-pattern: {antipattern}")
        
        if not found_antipatterns:
            print("✅ No anti-patterns found (good!)")
        
        # Show a preview of the enhanced prompt
        print("\n--- ENHANCED PROMPT PREVIEW ---")
        lines = enhanced_prompt.split('\n')
        for i, line in enumerate(lines[:30]):  # Show first 30 lines
            print(f"{i+1:2d}: {line}")
        if len(lines) > 30:
            print(f"... and {len(lines) - 30} more lines")
            
        # Check success criteria
        success_criteria = len(found_patterns) >= 4 and len(found_antipatterns) == 0
        
        if success_criteria:
            print("\n✅ SUCCESS: V0 prompt correctly uses Next.js API routes pattern!")
            print("The generated prompt will instruct builders to:")
            print("  - Create API routes in /api folder")
            print("  - Proxy requests to the backend")
            print("  - Make frontend calls to local API routes")
            print("  - Avoid direct external API calls")
        else:
            print("\n❌ ISSUE: V0 prompt may not follow Next.js API routes pattern correctly")
            print(f"Found {len(found_patterns)}/{len(nextjs_patterns)} expected patterns")
            print(f"Found {len(found_antipatterns)} anti-patterns")
            
        return success_criteria
        
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(resp.text)
        return False


def test_database_integration():
    """Test that database generation also follows the API routes pattern."""
    print("\n=== DATABASE INTEGRATION WITH NEXT.JS TEST ===")
    
    payload = {
        "user_description": "A task management app where users can create, update, and delete tasks with due dates and categories"
    }
    
    url = f"{BASE_URL}/prompt/v0/enhance"
    resp = requests.post(url, json=payload)
    
    try:
        result = resp.json()
        enhanced_prompt = result.get('prompt', '')
        database_info = result.get('database', {})
        
        print(f"✅ Combined prompt and database generated")
        print(f"Database success: {database_info.get('success', False)}")
        print(f"Tables created: {len(database_info.get('tables_created', []))}")
        
        # Check that database API routes are mentioned
        db_api_patterns = [
            "/api/setup-db",
            "/api/query-db", 
            "/api/generate-schema",
            "database setup",
        ]
        
        found_db_patterns = []
        for pattern in db_api_patterns:
            if pattern in enhanced_prompt:
                found_db_patterns.append(pattern)
                print(f"✅ Found database API pattern: {pattern}")
                
        if len(found_db_patterns) >= 2:
            print("✅ Database integration includes API routes")
        else:
            print("⚠️  Database integration may not include API routes")
            
        return len(found_db_patterns) >= 2
        
    except Exception as e:
        print(f"Error testing database integration: {e}")
        return False


def main():
    """Run the Next.js API routes generation tests."""
    print("🚀 Testing Next.js API Routes Pattern in V0 Prompts\n")
    
    test1_success = test_nextjs_api_routes_generation()
    test2_success = test_database_integration()
    
    if test1_success and test2_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("The V0 prompt builder now correctly generates Next.js API routes!")
        print("✅ API routes proxy to langchain-helper-api-production.up.railway.app")
        print("✅ Frontend calls local API routes instead of external APIs")
        print("✅ Database integration follows the same pattern")
    else:
        print("\n❌ Some tests failed!")
        print("The V0 prompt builder may need further adjustments")


if __name__ == "__main__":
    main()

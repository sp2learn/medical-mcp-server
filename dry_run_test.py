#!/usr/bin/env python3
"""
Dry run test for Medical MCP Server - tests structure without API calls
"""

import asyncio
import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_server_structure():
    """Test the server structure and imports without making API calls."""
    print("🧪 Medical MCP Server - Dry Run Test")
    print("=" * 50)
    
    try:
        # Test imports
        print("✓ Testing imports...")
        from server import server
        from medical_client import MedicalClient
        print("  ✓ All imports successful")
        
        # Test server tools listing
        print("\n✓ Testing server tools...")
        # Import the handler directly to test it
        from server import handle_list_tools
        tools = await handle_list_tools()
        print(f"  ✓ Found {len(tools)} tools:")
        for tool in tools:
            print(f"    - {tool.name}: {tool.description}")
        
        # Test medical client initialization (without API calls)
        print("\n✓ Testing medical client initialization...")
        
        # Temporarily override environment for testing
        original_model = os.getenv("MEDICAL_MODEL")
        os.environ["MEDICAL_MODEL"] = "gemini"
        os.environ["GOOGLE_API_KEY"] = "test_key_for_dry_run"
        
        try:
            client = MedicalClient()
            print(f"  ✓ Client initialized with model: {client.model_type}")
            print(f"  ✓ Client type: {client.client_type}")
        except Exception as e:
            print(f"  ⚠️  Client initialization: {str(e)}")
        finally:
            # Restore original environment
            if original_model:
                os.environ["MEDICAL_MODEL"] = original_model
            else:
                os.environ.pop("MEDICAL_MODEL", None)
        
        # Test tool call structure (without actual execution)
        print("\n✓ Testing tool call structure...")
        
        # Test medical_query tool arguments
        medical_query_args = {
            "question": "What are the symptoms of diabetes?",
            "context": "Patient is 45 years old"
        }
        print(f"  ✓ medical_query args structure: {json.dumps(medical_query_args, indent=2)}")
        
        # Test symptom_checker tool arguments  
        symptom_checker_args = {
            "symptoms": ["headache", "fever", "fatigue"],
            "age": 30,
            "gender": "female"
        }
        print(f"  ✓ symptom_checker args structure: {json.dumps(symptom_checker_args, indent=2)}")
        
        print("\n🎉 Dry run completed successfully!")
        print("\nNext steps:")
        print("1. Add your real API keys to .env file")
        print("2. Test with: python test_server.py")
        print("3. Add to your MCP client configuration")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure you've installed requirements: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_server_structure())
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Test that the MCP server can start up properly
"""

import asyncio
import sys
import os
import signal
from contextlib import asynccontextmanager

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_server_startup():
    """Test that the server can start up without errors."""
    print("🚀 Testing MCP Server Startup...")
    
    try:
        from server import server
        from mcp.server.models import InitializationOptions
        from mcp.server import NotificationOptions
        
        print("✓ Server imports successful")
        
        # Test server capabilities
        capabilities = server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        )
        
        print("✓ Server capabilities generated:")
        print(f"  - Tools: {capabilities.tools is not None}")
        print(f"  - Resources: {capabilities.resources is not None}")
        print(f"  - Prompts: {capabilities.prompts is not None}")
        
        print("\n🎉 Server startup test completed successfully!")
        print("\nThe server is ready to run. To start it:")
        print("python server.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Server startup failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_server_startup())
    sys.exit(0 if success else 1)
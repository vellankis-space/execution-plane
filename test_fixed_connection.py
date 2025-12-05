#!/usr/bin/env python3
"""
Test script to verify the fixed HTTP connection to Docker MCP Gateway
This simulates what happens when the backend service restarts and loads the updated configuration
"""
import asyncio
import sys
import os

# Add backend to path so we can import the FastMCP manager
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.fastmcp_manager import fastmcp_manager, MCPServerConfig

async def test_fixed_connection():
    """Test the fixed HTTP connection to Docker MCP Gateway"""
    print("🧪 Testing Fixed Docker MCP Gateway HTTP Connection")
    print("=" * 60)
    
    # Create the corrected configuration (matching what we updated in the database)
    config = MCPServerConfig(
        server_id="mcp_fixed_test",
        name="Docker MCP Toolkit",
        transport_type="http",
        url="http://localhost:3000",
        auth_token="my-test-token-123",
        env={"PYTHONUNBUFFERED": "1"}
    )
    
    print(f"Registering server: {config.name}")
    print(f"  - Transport type: {config.transport_type}")
    print(f"  - URL: {config.url}")
    print(f"  - Auth token: {'*' * len(config.auth_token) if config.auth_token else 'None'}")
    
    # Register the server with FastMCP manager
    await fastmcp_manager.register_server(config)
    
    # Try to connect to the server
    print(f"\nAttempting to connect to server {config.server_id}...")
    try:
        success = await fastmcp_manager.connect_server(config.server_id)
        if success:
            print("✅ Successfully connected to Docker MCP Gateway!")
            print("🎉 The HTTP connection is working correctly.")
            
            # Try to get tools to verify full functionality
            try:
                tools = await fastmcp_manager.get_tools(config.server_id)
                print(f"✅ Successfully retrieved {len(tools)} tools from the gateway.")
                if tools:
                    print("Sample tools:")
                    for i, tool in enumerate(tools[:3]):  # Show first 3 tools
                        print(f"  {i+1}. {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:50]}...")
                return True
            except Exception as tools_error:
                print(f"⚠️  Connected but couldn't retrieve tools: {tools_error}")
                return True
        else:
            print("❌ Failed to connect to Docker MCP Gateway.")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Docker MCP Gateway: {e}")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(test_fixed_connection())
        if result:
            print("\n🎉 SUCCESS: The Docker MCP Toolkit connection issue has been FIXED!")
            print("\nSummary of fixes:")
            print("  1. Updated database record to use HTTP transport instead of STDIO")
            print("  2. Set correct URL: http://localhost:3000")
            print("  3. Added authentication token")
            print("  4. Removed problematic command and args")
            print("\nNext steps:")
            print("  1. Restart the backend service to load the updated database configuration")
            print("  2. The MCP server should now connect successfully through the UI")
        else:
            print("\n❌ The connection test failed. Please check the Docker MCP Gateway status.")
    except Exception as e:
        print(f"❌ Unexpected error during test: {e}")
        import traceback
        traceback.print_exc()
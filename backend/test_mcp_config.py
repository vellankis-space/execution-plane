import asyncio
import os
import sys
import traceback

# Add the current directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from services.fastmcp_manager import fastmcp_manager
    print("Successfully imported fastmcp_manager")
except Exception as e:
    print(f"Error importing fastmcp_manager: {e}")
    traceback.print_exc()
    sys.exit(1)

async def test_mcp_config_loading():
    """Test loading MCP configuration from file"""
    # Get the path to the mcp.json file
    config_file_path = os.path.join(os.path.dirname(__file__), "..", "mcp.json")
    print(f"Looking for MCP config file at: {config_file_path}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if file exists
    if not os.path.exists(config_file_path):
        print("MCP config file not found")
        # List files in the parent directory to see what's there
        parent_dir = os.path.join(os.path.dirname(__file__), "..")
        print(f"Files in parent directory: {os.listdir(parent_dir)}")
        return False
    
    print("MCP config file found")
    
    # Try to load the configuration
    try:
        print("Attempting to load MCP config...")
        success = await fastmcp_manager.load_config_from_file(config_file_path)
        print(f"MCP config loading result: {success}")
        
        # Print loaded servers
        print(f"Loaded servers: {list(fastmcp_manager.servers.keys())}")
        
        return success
    except Exception as e:
        print(f"Error loading MCP config: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting MCP config test...")
    try:
        result = asyncio.run(test_mcp_config_loading())
        print(f"Test result: {result}")
    except Exception as e:
        print(f"Error running test: {e}")
        traceback.print_exc()
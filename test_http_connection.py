#!/usr/bin/env python3
"""
Test script to verify HTTP connection to Docker MCP Gateway
"""
import requests
import time

def test_http_connection():
    """Test HTTP connection to Docker MCP Gateway"""
    url = "http://localhost:3000"
    
    print(f"Testing connection to Docker MCP Gateway at {url}")
    
    try:
        # Send a simple GET request to test if the server is responding
        response = requests.get(url, timeout=10)
        print(f"✅ Server responded with status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server may not be running")
        print("\nTo start the Docker MCP Gateway, you can:")
        print("1. Run start_docker_mcp_gateway.bat (foreground, keeps window open)")
        print("2. Run start_docker_mcp_background.ps1 (background PowerShell job)")
        print("\nAfter starting the gateway, wait 10-15 seconds for initialization, then run this test again.")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out - server may be busy or not responding")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Docker MCP Gateway HTTP Connection")
    print("=" * 50)
    
    success = test_http_connection()
    
    if success:
        print("\n🎉 HTTP connection test passed!")
        print("The Docker MCP Gateway is ready to accept connections.")
        print("\nNext steps:")
        print("1. Restart your backend service to reload the MCP configuration")
        print("2. Connect to the MCP server through the UI")
    else:
        print("\n❌ HTTP connection test failed.")
        print("\nPlease follow the instructions above and try again.")
#!/usr/bin/env python3
"""
Test script to verify authenticated HTTP connection to Docker MCP Gateway
"""
import requests
import time

def test_authenticated_http_connection():
    """Test authenticated HTTP connection to Docker MCP Gateway"""
    url = "http://localhost:3000/mcp"  # Note the /mcp path
    token = "my-test-token-123"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print(f"Testing authenticated connection to Docker MCP Gateway at {url}")
    print(f"Using token: {token}")
    
    try:
        # Send a simple GET request with authentication
        response = requests.get(url, headers=headers, timeout=10)
        print(f"✅ Server responded with status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        if response.text:
            print(f"Response body: {response.text[:200]}{'...' if len(response.text) > 200 else ''}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server may not be running")
        print("\nTo start the Docker MCP Gateway, you can:")
        print("1. Run start_docker_mcp_gateway.bat (foreground, keeps window open)")
        print("2. Make sure to set the MCP_GATEWAY_AUTH_TOKEN environment variable")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out - server may be busy or not responding")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Authenticated Docker MCP Gateway HTTP Connection")
    print("=" * 60)
    
    success = test_authenticated_http_connection()
    
    if success:
        print("\n🎉 Authenticated HTTP connection test passed!")
        print("The Docker MCP Gateway is ready to accept authenticated connections.")
        print("\nNext steps:")
        print("1. Restart your backend service to reload the MCP configuration")
        print("2. Connect to the MCP server through the UI")
    else:
        print("\n❌ Authenticated HTTP connection test failed.")
        print("\nPlease follow the instructions above and try again.")
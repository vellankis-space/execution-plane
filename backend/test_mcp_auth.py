#!/usr/bin/env python3
"""
MCP Server Authentication Diagnostic Tool

This script helps diagnose authentication issues with MCP servers configured via HTTP/API key.
It tests the complete flow from database retrieval to FastMCP client creation.
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from core.database import engine, get_db
from models.mcp_server import MCPServer
from services.fastmcp_manager import MCPServerConfig, fastmcp_manager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_mcp_server_auth(server_name: str = None):
    """
    Test MCP server authentication configuration.
    
    Args:
        server_name: Optional server name to test. If None, tests all servers.
    """
    print("=" * 80)
    print("MCP Server Authentication Diagnostic Tool")
    print("=" * 80)
    print()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Query servers
        if server_name:
            servers = db.query(MCPServer).filter(MCPServer.name.ilike(f"%{server_name}%")).all()
            if not servers:
                print(f"❌ No server found matching '{server_name}'")
                return
        else:
            servers = db.query(MCPServer).all()
            
        if not servers:
            print("❌ No MCP servers found in database")
            return
            
        print(f"Found {len(servers)} server(s) to test:\n")
        
        for server in servers:
            print("-" * 80)
            print(f"Server: {server.name}")
            print(f"ID: {server.server_id}")
            print(f"Transport: {server.transport_type}")
            print(f"Status: {server.status}")
            print()
            
            # Check authentication configuration
            print("Authentication Configuration:")
            print(f"  • URL: {server.url}")
            print(f"  • Auth Type: {server.auth_type or '(not set)'}")
            print(f"  • Auth Token Present: {'✓ Yes' if server.auth_token else '✗ No'}")
            
            if server.auth_token:
                token_preview = server.auth_token[:10] + "..." + server.auth_token[-4:] if len(server.auth_token) > 14 else server.auth_token
                print(f"  • Auth Token Length: {len(server.auth_token)} characters")
                print(f"  • Auth Token Preview: {token_preview}")
            else:
                print(f"  • ⚠️  WARNING: No auth token configured!")
                
            print(f"  • Headers: {server.headers or '(none)'}")
            print()
            
            # Validate auth configuration
            if server.transport_type in ("http", "sse"):
                has_auth_token = bool(server.auth_token and server.auth_token.strip())
                has_auth_header = False
                
                if server.headers and isinstance(server.headers, dict):
                    has_auth_header = any(k.lower() == 'authorization' for k in server.headers.keys())
                
                if not has_auth_token and not has_auth_header:
                    print("  ❌ ISSUE: HTTP/SSE server has NO authentication configured")
                    print("     → Connection to authenticated APIs will fail")
                    print()
                elif has_auth_token and len(server.auth_token.strip()) < 10:
                    print(f"  ⚠️  WARNING: API key seems too short ({len(server.auth_token.strip())} chars)")
                    print("     → Verify this is the correct API key")
                    print()
                else:
                    print("  ✅ Authentication is configured")
                    print()
                    
                # Test creating MCPServerConfig
                try:
                    print("Creating MCPServerConfig...")
                    config = MCPServerConfig(
                        server_id=server.server_id,
                        name=server.name,
                        description=server.description or "",
                        transport_type=server.transport_type,
                        url=server.url,
                        headers=server.headers or {},
                        auth_type=server.auth_type,
                        auth_token=server.auth_token,
                        command=server.command,
                        args=server.args or [],
                        env=server.env or {},
                        cwd=server.cwd
                    )
                    
                    print("  ✅ MCPServerConfig created successfully")
                    print(f"     → Config auth_token present: {bool(config.auth_token)}")
                    print(f"     → Config auth_type: {config.auth_type}")
                    print()
                    
                    # Test registration
                    print("Testing server registration...")
                    await fastmcp_manager.register_server(config)
                    print("  ✅ Server registered with FastMCP manager")
                    print()
                    
                    # Test connection (optional - may fail if server is down)
                    print("Testing connection (this may fail if server is unavailable)...")
                    try:
                        success = await fastmcp_manager.connect_server(server.server_id)
                        if success:
                            print("  ✅ Successfully connected to server!")
                            status = await fastmcp_manager.get_server_status(server.server_id)
                            print(f"     → Tools: {status.get('tools_count', 0)}")
                            print(f"     → Resources: {status.get('resources_count', 0)}")
                            print(f"     → Prompts: {status.get('prompts_count', 0)}")
                        else:
                            print("  ❌ Connection failed")
                            status = await fastmcp_manager.get_server_status(server.server_id)
                            if status.get('last_error'):
                                print(f"     → Error: {status['last_error']}")
                    except Exception as conn_err:
                        print(f"  ⚠️  Connection test failed: {conn_err}")
                    print()
                    
                except Exception as e:
                    print(f"  ❌ Failed to create config: {e}")
                    import traceback
                    traceback.print_exc()
                    print()
            
            print("-" * 80)
            print()
            
    finally:
        db.close()
        
    print("=" * 80)
    print("Diagnostic complete!")
    print("=" * 80)


if __name__ == "__main__":
    server_name = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(test_mcp_server_auth(server_name))

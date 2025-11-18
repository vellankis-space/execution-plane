"""
FastMCP Manager Service
Using FastMCP framework for robust MCP server/client management
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from fastmcp import Client
from fastmcp.exceptions import McpError
import json
import traceback

logger = logging.getLogger(__name__)

# Connection timeout settings
CONNECTION_TIMEOUT = 30  # seconds
PING_TIMEOUT = 10  # seconds


@dataclass
class MCPServerConfig:
    """MCP Server Configuration"""
    server_id: str
    name: str
    description: str = ""
    transport_type: str = "http"  # http, sse, stdio
    
    # HTTP/SSE config
    url: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    auth_type: Optional[str] = None  # bearer, oauth, etc.
    auth_token: Optional[str] = None
    
    # STDIO config
    command: Optional[str] = None
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    cwd: Optional[str] = None
    
    # Status tracking
    status: str = "inactive"  # inactive, active, error, connecting
    last_error: Optional[str] = None
    last_connected: Optional[datetime] = None
    
    # Tool discovery
    tools_count: int = 0
    resources_count: int = 0
    prompts_count: int = 0


class FastMCPManager:
    """
    FastMCP Manager for handling multiple MCP servers as a client (host).
    
    This manager:
    - Connects to external MCP servers (HTTP, SSE, STDIO)
    - Discovers tools, resources, and prompts
    - Manages connections and health monitoring
    - Provides unified interface for agent tool integration
    """
    
    def __init__(self):
        self.servers: Dict[str, MCPServerConfig] = {}
        self.clients: Dict[str, Client] = {}
        self.cached_tools: Dict[str, List[Dict[str, Any]]] = {}
        self.cached_resources: Dict[str, List[Dict[str, Any]]] = {}
        self.cached_prompts: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = asyncio.Lock()
    
    async def register_server(self, config: MCPServerConfig) -> bool:
        """
        Register an MCP server configuration.
        
        Args:
            config: MCP server configuration
            
        Returns:
            True if successfully registered
        """
        async with self._lock:
            self.servers[config.server_id] = config
            logger.info(f"Registered MCP server: {config.server_id} ({config.name})")
            return True
    
    async def connect_server(self, server_id: str) -> bool:
        """
        Connect to an MCP server using FastMCP client.
        
        CRITICAL: FastMCP Client MUST be used with 'async with' to establish connection!
        
        Args:
            server_id: ID of the server to connect to
            
        Returns:
            True if connection successful
        """
        if server_id not in self.servers:
            logger.error(f"Server {server_id} not registered")
            return False
        
        config = self.servers[server_id]
        
        try:
            config.status = "connecting"
            logger.info(f"Connecting to MCP server: {server_id} ({config.name}) via {config.transport_type}")
            logger.info(f"URL/Command: {config.url or config.command}")
            
            # Create FastMCP client based on transport type
            client = self._create_client_instance(config)
            
            # Store client instance (but connection happens in async with)
            async with self._lock:
                self.clients[server_id] = client
            
            # ✅ CRITICAL: Use async with to establish connection!
            # Without this, transport never connects and operations fail
            logger.info(f"Establishing connection to {server_id}...")
            async with asyncio.timeout(CONNECTION_TIMEOUT):
                async with client:
                    # Connection established! Now test it
                    logger.info(f"Testing connection to {server_id} with ping...")
                    try:
                        await asyncio.wait_for(client.ping(), timeout=PING_TIMEOUT)
                        logger.info(f"✓ Ping successful for {server_id}")
                    except asyncio.TimeoutError:
                        logger.warning(f"Ping timeout for {server_id}, trying list_tools as fallback...")
                        # Some servers don't support ping, try list_tools
                        await asyncio.wait_for(client.list_tools(), timeout=PING_TIMEOUT)
                        logger.info(f"✓ Fallback connection test (list_tools) successful for {server_id}")
                    except Exception as ping_error:
                        logger.warning(f"Ping failed for {server_id}: {ping_error}. Trying to list tools as fallback...")
                        try:
                            tools = await asyncio.wait_for(client.list_tools(), timeout=PING_TIMEOUT)
                            logger.info(f"✓ Fallback connection test (list_tools) successful for {server_id}, found {len(tools)} tools")
                        except Exception as list_error:
                            raise Exception(f"Both ping and list_tools failed. Ping error: {ping_error}. List tools error: {list_error}")
                    
                    # Discover capabilities while connection is active
                    logger.info(f"Discovering capabilities for {server_id}...")
                    await self._discover_capabilities_in_context(server_id, client)
            
            # Connection test successful
            config.status = "active"
            config.last_connected = datetime.now()
            config.last_error = None
            
            logger.info(f"✓ Successfully connected to MCP server: {server_id} (Tools: {config.tools_count}, Resources: {config.resources_count}, Prompts: {config.prompts_count})")
            return True
            
        except asyncio.TimeoutError as e:
            error_msg = f"Connection timeout after {CONNECTION_TIMEOUT}s - server may be unreachable"
            logger.error(f"Timeout connecting to MCP server {server_id}: {error_msg}")
            config.status = "error"
            config.last_error = error_msg
            
            # Clean up
            async with self._lock:
                if server_id in self.clients:
                    del self.clients[server_id]
            return False
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Error connecting to MCP server {server_id}: {error_msg}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            config.status = "error"
            config.last_error = error_msg
            
            # Clean up client if it was partially created
            async with self._lock:
                if server_id in self.clients:
                    del self.clients[server_id]
            
            return False
    
    def _create_client_instance(self, config: MCPServerConfig) -> Client:
        """
        Create FastMCP Client instance.
        
        IMPORTANT: This only creates the instance. Connection is established
        when the client is used within 'async with' context!
        
        Args:
            config: Server configuration
            
        Returns:
            FastMCP Client instance (not yet connected)
        """
        if config.transport_type in ["http", "sse"]:
            # HTTP/SSE transport
            if not config.url:
                raise ValueError("URL required for HTTP/SSE transport")
            
            logger.info(f"Creating {config.transport_type.upper()} client for: {config.url}")
            
            # Use URL as-is - FastMCP will handle endpoint detection
            url = config.url.rstrip('/')  # Remove trailing slash
            
            # For SSE, append /sse if not present
            if config.transport_type == "sse":
                # Check if URL already has a known MCP endpoint
                has_endpoint = any(endpoint in url.lower() for endpoint in ["/sse", "/mcp", "/sse/", "/mcp/"])
                if not has_endpoint:
                    url = url + "/sse"
                    logger.info(f"Adjusted SSE URL to: {url}")
            
            # Create client - connection happens in async with!
            # FastMCP Client constructor parameters:
            # Client(transport, name=None, timeout=None, auth=None, ...)
            return Client(url, timeout=PING_TIMEOUT)
            
        elif config.transport_type == "stdio":
            # STDIO transport (local script/process)
            if not config.command:
                raise ValueError("Command required for STDIO transport")
            
            logger.info(f"Creating STDIO client for command: {config.command}")
            
            # FastMCP supports passing a Python script path directly
            if config.command.endswith(".py"):
                return Client(config.command, timeout=PING_TIMEOUT)
            
            # For command strings, FastMCP will auto-detect if it's a script
            return Client(config.command, timeout=PING_TIMEOUT)
        
        else:
            raise ValueError(f"Unsupported transport type: {config.transport_type}")
    
    async def _discover_capabilities_in_context(self, server_id: str, client: Client):
        """
        Discover tools, resources, and prompts from server within an active connection context.
        
        MUST be called within 'async with client:' block!
        
        Args:
            server_id: Server ID to discover from
            client: Connected FastMCP Client instance
        """
        config = self.servers[server_id]
        
        try:
            # Discover tools with timeout
            logger.info(f"Listing tools from {server_id}...")
            tools = await asyncio.wait_for(client.list_tools(), timeout=PING_TIMEOUT)
            self.cached_tools[server_id] = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema.model_dump() if hasattr(tool.inputSchema, 'model_dump') else tool.inputSchema
                }
                for tool in tools
            ]
            config.tools_count = len(tools)
            logger.info(f"✓ Discovered {len(tools)} tools from {server_id}")
            
            # Discover resources with timeout
            try:
                logger.info(f"Listing resources from {server_id}...")
                resources = await asyncio.wait_for(client.list_resources(), timeout=PING_TIMEOUT)
                self.cached_resources[server_id] = [
                    {
                        "uri": resource.uri,
                        "name": resource.name,
                        "description": resource.description,
                        "mimeType": resource.mimeType
                    }
                    for resource in resources
                ]
                config.resources_count = len(resources)
                logger.info(f"✓ Discovered {len(resources)} resources from {server_id}")
            except Exception as res_error:
                logger.warning(f"Could not list resources from {server_id}: {res_error}")
                config.resources_count = 0
            
            # Discover prompts with timeout
            try:
                logger.info(f"Listing prompts from {server_id}...")
                prompts = await asyncio.wait_for(client.list_prompts(), timeout=PING_TIMEOUT)
                self.cached_prompts[server_id] = [
                    {
                        "name": prompt.name,
                        "description": prompt.description,
                        "arguments": prompt.arguments
                    }
                    for prompt in prompts
                ]
                config.prompts_count = len(prompts)
                logger.info(f"✓ Discovered {len(prompts)} prompts from {server_id}")
            except Exception as prompt_error:
                logger.warning(f"Could not list prompts from {server_id}: {prompt_error}")
                config.prompts_count = 0
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout discovering capabilities from {server_id}")
            config.tools_count = 0
            config.resources_count = 0
            config.prompts_count = 0
        except Exception as e:
            logger.error(f"Error discovering capabilities from {server_id}: {e}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            config.tools_count = 0
            config.resources_count = 0
            config.prompts_count = 0
    
    async def disconnect_server(self, server_id: str) -> bool:
        """
        Disconnect from an MCP server.
        
        Args:
            server_id: Server ID to disconnect
            
        Returns:
            True if successfully disconnected
        """
        if server_id in self.clients:
            try:
                # FastMCP Client handles cleanup automatically when going out of scope
                # but we can explicitly remove it
                async with self._lock:
                    del self.clients[server_id]
                
                if server_id in self.servers:
                    self.servers[server_id].status = "inactive"
                
                logger.info(f"Disconnected from MCP server: {server_id}")
                return True
            except Exception as e:
                logger.error(f"Error disconnecting from server {server_id}: {e}")
                return False
        return True
    
    async def get_tools(self, server_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get available tools from specified server or all servers.
        
        Args:
            server_id: Optional server ID. If None, returns tools from all servers.
            
        Returns:
            List of tool definitions
        """
        if server_id:
            # Return tools from specific server
            if server_id in self.cached_tools:
                return self.cached_tools[server_id]
            
            # If not cached, try to discover
            if server_id in self.clients:
                await self._discover_capabilities(server_id)
                return self.cached_tools.get(server_id, [])
            
            return []
        
        # Return tools from all servers
        all_tools = []
        for sid, tools in self.cached_tools.items():
            # Prefix tool names with server ID to avoid conflicts
            prefixed_tools = [
                {
                    **tool,
                    "name": f"{sid}_{tool['name']}",
                    "server_id": sid,
                    "original_name": tool["name"]
                }
                for tool in tools
            ]
            all_tools.extend(prefixed_tools)
        
        return all_tools
    
    async def call_tool(self, server_id: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on an MCP server.
        
        CRITICAL: Uses async with to establish connection for each call.
        
        Args:
            server_id: Server ID
            tool_name: Tool name (unprefixed)
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if server_id not in self.clients:
            # Try to connect if not connected
            if not await self.connect_server(server_id):
                raise Exception(f"Server {server_id} not connected")
        
        client = self.clients[server_id]
        
        try:
            # ✅ CRITICAL: Use async with to establish connection!
            async with client:
                result = await client.call_tool(tool_name, arguments)
                return result.data if hasattr(result, 'data') else result
        except McpError as e:
            logger.error(f"MCP error calling tool {tool_name} on {server_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling tool {tool_name} on {server_id}: {e}")
            raise
    
    async def get_resources(self, server_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available resources from server(s)"""
        if server_id:
            return self.cached_resources.get(server_id, [])
        
        # Return resources from all servers
        all_resources = []
        for sid, resources in self.cached_resources.items():
            prefixed_resources = [
                {**resource, "server_id": sid}
                for resource in resources
            ]
            all_resources.extend(prefixed_resources)
        
        return all_resources
    
    async def read_resource(self, server_id: str, uri: str) -> Any:
        """Read a resource from an MCP server"""
        if server_id not in self.clients:
            if not await self.connect_server(server_id):
                raise Exception(f"Server {server_id} not connected")
        
        client = self.clients[server_id]
        
        try:
            # ✅ Use async with to establish connection
            async with client:
                result = await client.read_resource(uri)
                return result
        except Exception as e:
            logger.error(f"Error reading resource {uri} from {server_id}: {e}")
            raise
    
    async def get_prompts(self, server_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available prompts from server(s)"""
        if server_id:
            return self.cached_prompts.get(server_id, [])
        
        # Return prompts from all servers
        all_prompts = []
        for sid, prompts in self.cached_prompts.items():
            prefixed_prompts = [
                {
                    **prompt,
                    "name": f"{sid}_{prompt['name']}",
                    "server_id": sid,
                    "original_name": prompt["name"]
                }
                for prompt in prompts
            ]
            all_prompts.extend(prefixed_prompts)
        
        return all_prompts
    
    async def get_prompt(self, server_id: str, prompt_name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
        """Get a rendered prompt from an MCP server"""
        if server_id not in self.clients:
            if not await self.connect_server(server_id):
                raise Exception(f"Server {server_id} not connected")
        
        client = self.clients[server_id]
        
        try:
            # ✅ Use async with to establish connection
            async with client:
                result = await client.get_prompt(prompt_name, arguments or {})
                return result.messages if hasattr(result, 'messages') else result
        except Exception as e:
            logger.error(f"Error getting prompt {prompt_name} from {server_id}: {e}")
            raise
    
    async def health_check(self, server_id: str) -> bool:
        """
        Check health of an MCP server.
        
        Args:
            server_id: Server ID to check
            
        Returns:
            True if server is healthy
        """
        if server_id not in self.clients:
            return False
        
        client = self.clients[server_id]
        config = self.servers[server_id]
        
        try:
            # ✅ Use async with to establish connection
            async with client:
                await client.ping()
                config.status = "active"
                config.last_error = None
                return True
        except Exception as e:
            logger.warning(f"Health check failed for {server_id}: {e}")
            config.status = "error"
            config.last_error = str(e)
            return False
    
    async def get_server_status(self, server_id: str) -> Dict[str, Any]:
        """Get detailed status of an MCP server"""
        if server_id not in self.servers:
            return {"error": "Server not found"}
        
        config = self.servers[server_id]
        
        return {
            "server_id": server_id,
            "name": config.name,
            "description": config.description,
            "transport_type": config.transport_type,
            "status": config.status,
            "last_connected": config.last_connected.isoformat() if config.last_connected else None,
            "last_error": config.last_error,
            "tools_count": config.tools_count,
            "resources_count": config.resources_count,
            "prompts_count": config.prompts_count,
            "is_connected": server_id in self.clients
        }
    
    async def get_all_servers(self) -> List[Dict[str, Any]]:
        """Get status of all registered servers"""
        return [
            await self.get_server_status(server_id)
            for server_id in self.servers.keys()
        ]


# Global FastMCP manager instance
fastmcp_manager = FastMCPManager()

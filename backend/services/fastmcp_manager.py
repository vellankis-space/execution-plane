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

logger = logging.getLogger(__name__)


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
            logger.info(f"Connecting to MCP server: {server_id} ({config.name})")
            
            # Create FastMCP client based on transport type
            client = await self._create_client(config)
            
            # Store client
            async with self._lock:
                self.clients[server_id] = client
            
            # Test connection with ping
            await client.ping()
            
            # Update status
            config.status = "active"
            config.last_connected = datetime.now()
            config.last_error = None
            
            # Discover capabilities
            await self._discover_capabilities(server_id)
            
            logger.info(f"Successfully connected to MCP server: {server_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to MCP server {server_id}: {e}")
            config.status = "error"
            config.last_error = str(e)
            return False
    
    async def _create_client(self, config: MCPServerConfig) -> Client:
        """
        Create FastMCP client based on configuration.
        
        Args:
            config: Server configuration
            
        Returns:
            FastMCP Client instance
        """
        if config.transport_type == "http" or config.transport_type == "sse":
            # HTTP/SSE transport
            if not config.url:
                raise ValueError("URL required for HTTP/SSE transport")
            
            # Build client configuration
            client_config = config.url
            
            # Add headers if needed
            if config.headers or config.auth_token:
                # For authenticated connections, we'll use the config parameter
                client_config = {
                    "url": config.url,
                    "headers": config.headers.copy()
                }
                
                if config.auth_token:
                    if config.auth_type == "bearer":
                        client_config["headers"]["Authorization"] = f"Bearer {config.auth_token}"
                    else:
                        client_config["headers"]["Authorization"] = config.auth_token
            
            return Client(client_config)
            
        elif config.transport_type == "stdio":
            # STDIO transport (local script/process)
            if not config.command:
                raise ValueError("Command required for STDIO transport")
            
            # FastMCP supports passing a Python script path directly
            if config.command.endswith(".py"):
                return Client(config.command)
            
            # For other commands, use stdio configuration
            stdio_config = {
                "transport": "stdio",
                "command": config.command,
                "args": config.args,
                "env": config.env,
            }
            
            if config.cwd:
                stdio_config["cwd"] = config.cwd
            
            return Client(stdio_config)
        
        else:
            raise ValueError(f"Unsupported transport type: {config.transport_type}")
    
    async def _discover_capabilities(self, server_id: str):
        """
        Discover tools, resources, and prompts from server.
        
        Args:
            server_id: Server ID to discover from
        """
        if server_id not in self.clients:
            return
        
        client = self.clients[server_id]
        config = self.servers[server_id]
        
        try:
            # Discover tools
            tools = await client.list_tools()
            self.cached_tools[server_id] = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema.model_dump() if hasattr(tool.inputSchema, 'model_dump') else tool.inputSchema
                }
                for tool in tools
            ]
            config.tools_count = len(tools)
            logger.info(f"Discovered {len(tools)} tools from {server_id}")
            
            # Discover resources
            resources = await client.list_resources()
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
            logger.info(f"Discovered {len(resources)} resources from {server_id}")
            
            # Discover prompts
            prompts = await client.list_prompts()
            self.cached_prompts[server_id] = [
                {
                    "name": prompt.name,
                    "description": prompt.description,
                    "arguments": prompt.arguments
                }
                for prompt in prompts
            ]
            config.prompts_count = len(prompts)
            logger.info(f"Discovered {len(prompts)} prompts from {server_id}")
            
        except Exception as e:
            logger.error(f"Error discovering capabilities from {server_id}: {e}")
    
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

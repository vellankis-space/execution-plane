"""
MCP (Model Context Protocol) Service
Based on https://modelcontextprotocol.io/docs/getting-started/intro
Standardized way to connect agents to tools, data sources, and workflows
"""
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)


class MCPMethod(str, Enum):
    """MCP Protocol methods"""
    # Server info
    INITIALIZE = "initialize"
    PING = "ping"
    
    # Tools
    LIST_TOOLS = "tools/list"
    CALL_TOOL = "tools/call"
    
    # Resources
    LIST_RESOURCES = "resources/list"
    READ_RESOURCE = "resources/read"
    
    # Prompts
    LIST_PROMPTS = "prompts/list"
    GET_PROMPT = "prompts/get"


@dataclass
class MCPServer:
    """MCP Server configuration"""
    server_id: str
    name: str
    transport: str  # "stdio", "sse", "websocket"
    endpoint: Optional[str] = None  # For SSE/WebSocket
    command: Optional[List[str]] = None  # For stdio
    env: Optional[Dict[str, str]] = None
    capabilities: Optional[Dict[str, Any]] = None


@dataclass
class MCPTool:
    """MCP Tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]
    handler: Optional[Callable] = None


@dataclass
class MCPResource:
    """MCP Resource definition"""
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None


@dataclass
class MCPPrompt:
    """MCP Prompt definition"""
    name: str
    description: Optional[str] = None
    arguments: Optional[List[Dict[str, Any]]] = None


class MCPService:
    """MCP Service for managing MCP servers and tools"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.prompts: Dict[str, MCPPrompt] = {}
        self.clients: Dict[str, Any] = {}  # MCP client connections
    
    def register_server(self, server: MCPServer):
        """Register an MCP server"""
        self.servers[server.server_id] = server
        logger.info(f"Registered MCP server: {server.server_id} ({server.name})")
    
    def register_tool(self, tool: MCPTool):
        """Register an MCP tool"""
        self.tools[tool.name] = tool
        logger.info(f"Registered MCP tool: {tool.name}")
    
    def register_resource(self, resource: MCPResource):
        """Register an MCP resource"""
        self.resources[resource.uri] = resource
        logger.info(f"Registered MCP resource: {resource.uri}")
    
    def register_prompt(self, prompt: MCPPrompt):
        """Register an MCP prompt"""
        self.prompts[prompt.name] = prompt
        logger.info(f"Registered MCP prompt: {prompt.name}")
    
    async def connect_server(self, server_id: str) -> bool:
        """Connect to an MCP server"""
        server = self.servers.get(server_id)
        if not server:
            logger.error(f"MCP server not found: {server_id}")
            return False
        
        try:
            if server.transport == "sse":
                # Server-Sent Events transport
                client = await self._connect_sse(server)
            elif server.transport == "websocket":
                # WebSocket transport
                client = await self._connect_websocket(server)
            elif server.transport == "stdio":
                # Standard I/O transport
                client = await self._connect_stdio(server)
            else:
                logger.error(f"Unsupported transport: {server.transport}")
                return False
            
            self.clients[server_id] = client
            
            # Initialize the connection
            await self._initialize_client(server_id, client)
            
            logger.info(f"Connected to MCP server: {server_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error connecting to MCP server {server_id}: {e}")
            return False
    
    async def _connect_sse(self, server: MCPServer) -> Any:
        """Connect to MCP server via Server-Sent Events"""
        # Implementation for SSE transport
        # This would use httpx or similar for SSE connections
        async with httpx.AsyncClient() as client:
            response = await client.get(
                server.endpoint or "",
                headers={"Accept": "text/event-stream"}
            )
            # Handle SSE connection
            return client
    
    async def _connect_websocket(self, server: MCPServer) -> Any:
        """Connect to MCP server via WebSocket"""
        # Implementation for WebSocket transport
        import websockets
        ws = await websockets.connect(server.endpoint or "")
        return ws
    
    async def _connect_stdio(self, server: MCPServer) -> Any:
        """Connect to MCP server via stdio"""
        # Implementation for stdio transport
        # This would spawn a subprocess and communicate via stdin/stdout
        import subprocess
        process = subprocess.Popen(
            server.command or [],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=server.env
        )
        return process
    
    async def _initialize_client(self, server_id: str, client: Any):
        """Initialize MCP client connection using MCP protocol"""
        server = self.servers.get(server_id)
        if not server:
            return
        
        try:
            # MCP uses JSON-RPC 2.0 for communication
            initialize_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": MCPMethod.INITIALIZE,
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "clientInfo": {
                        "name": "execution-plane",
                        "version": "1.0.0"
                    }
                }
            }
            
            if server.transport == "stdio":
                # For stdio, send JSON-RPC request via stdin
                if hasattr(client, 'stdin') and client.stdin:
                    request_json = json.dumps(initialize_request) + "\n"
                    client.stdin.write(request_json.encode())
                    client.stdin.flush()
                    
                    # Read response from stdout
                    if hasattr(client, 'stdout') and client.stdout:
                        response_line = client.stdout.readline()
                        if response_line:
                            response = json.loads(response_line.decode())
                            logger.debug(f"MCP server {server_id} initialized: {response}")
            
            elif server.transport in ["sse", "websocket"]:
                # For SSE/WebSocket, use HTTP POST or WebSocket message
                if server.transport == "sse":
                    async with httpx.AsyncClient() as http_client:
                        response = await http_client.post(
                            f"{server.endpoint}/mcp",
                            json=initialize_request,
                            headers={"Content-Type": "application/json"}
                        )
                        if response.status_code == 200:
                            logger.debug(f"MCP server {server_id} initialized via SSE")
                elif server.transport == "websocket":
                    if hasattr(client, 'send'):
                        await client.send(json.dumps(initialize_request))
                        response = await client.recv()
                        logger.debug(f"MCP server {server_id} initialized via WebSocket")
            
            logger.info(f"MCP client initialized for {server_id}")
        
        except Exception as e:
            logger.error(f"Error initializing MCP client for {server_id}: {e}")
    
    async def list_tools(self, server_id: Optional[str] = None) -> List[MCPTool]:
        """List available MCP tools"""
        if server_id:
            # Get tools from specific server
            if server_id not in self.clients:
                await self.connect_server(server_id)
            
            # Call MCP tools/list method using JSON-RPC 2.0
            server = self.servers.get(server_id)
            if not server:
                return []
            
            try:
                request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": MCPMethod.LIST_TOOLS,
                    "params": {}
                }
                
                tools_list = []
                
                if server.transport == "stdio" and server_id in self.clients:
                    client = self.clients[server_id]
                    if hasattr(client, 'stdin') and client.stdin:
                        request_json = json.dumps(request) + "\n"
                        client.stdin.write(request_json.encode())
                        client.stdin.flush()
                        
                        if hasattr(client, 'stdout') and client.stdout:
                            response_line = client.stdout.readline()
                            if response_line:
                                response = json.loads(response_line.decode())
                                if "result" in response and "tools" in response["result"]:
                                    for tool_data in response["result"]["tools"]:
                                        mcp_tool = MCPTool(
                                            name=tool_data.get("name", ""),
                                            description=tool_data.get("description", ""),
                                            inputSchema=tool_data.get("inputSchema", {})
                                        )
                                        tools_list.append(mcp_tool)
                
                elif server.transport == "sse" and server.endpoint:
                    async with httpx.AsyncClient() as http_client:
                        response = await http_client.post(
                            f"{server.endpoint}/mcp",
                            json=request,
                            headers={"Content-Type": "application/json"}
                        )
                        if response.status_code == 200:
                            data = response.json()
                            if "result" in data and "tools" in data["result"]:
                                for tool_data in data["result"]["tools"]:
                                    mcp_tool = MCPTool(
                                        name=tool_data.get("name", ""),
                                        description=tool_data.get("description", ""),
                                        inputSchema=tool_data.get("inputSchema", {})
                                    )
                                    tools_list.append(mcp_tool)
                
                elif server.transport == "websocket" and server_id in self.clients:
                    client = self.clients[server_id]
                    if hasattr(client, 'send'):
                        await client.send(json.dumps(request))
                        response = await client.recv()
                        data = json.loads(response)
                        if "result" in data and "tools" in data["result"]:
                            for tool_data in data["result"]["tools"]:
                                mcp_tool = MCPTool(
                                    name=tool_data.get("name", ""),
                                    description=tool_data.get("description", ""),
                                    inputSchema=tool_data.get("inputSchema", {})
                                )
                                tools_list.append(mcp_tool)
                
                # Cache tools from remote server
                for tool in tools_list:
                    self.tools[f"{server_id}:{tool.name}"] = tool
                
                return tools_list
                
            except Exception as e:
                logger.error(f"Error listing tools from MCP server {server_id}: {e}")
                return []
        else:
            # Return all registered tools (local + cached from servers)
            return list(self.tools.values())
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        server_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call an MCP tool"""
        # Check if tool is registered locally
        if tool_name in self.tools:
            tool = self.tools[tool_name]
            if tool.handler:
                try:
                    result = await tool.handler(**arguments) if asyncio.iscoroutinefunction(tool.handler) else tool.handler(**arguments)
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result) if not isinstance(result, str) else result
                            }
                        ],
                        "isError": False
                    }
                except Exception as e:
                    logger.error(f"Error calling tool {tool_name}: {e}")
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error: {str(e)}"
                            }
                        ],
                        "isError": True
                    }
        
        # If server_id provided, try calling on remote MCP server
        if server_id and server_id in self.clients:
            server = self.servers.get(server_id)
            if not server:
                return {
                    "content": [{"type": "text", "text": f"Server {server_id} not found"}],
                    "isError": True
                }
            
            try:
                # MCP tools/call request using JSON-RPC 2.0
                request = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": MCPMethod.CALL_TOOL,
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                }
                
                if server.transport == "stdio":
                    client = self.clients[server_id]
                    if hasattr(client, 'stdin') and client.stdin:
                        request_json = json.dumps(request) + "\n"
                        client.stdin.write(request_json.encode())
                        client.stdin.flush()
                        
                        if hasattr(client, 'stdout') and client.stdout:
                            response_line = client.stdout.readline()
                            if response_line:
                                response = json.loads(response_line.decode())
                                if "result" in response:
                                    return {
                                        "content": response["result"].get("content", []),
                                        "isError": response["result"].get("isError", False)
                                    }
                                elif "error" in response:
                                    return {
                                        "content": [{"type": "text", "text": response["error"].get("message", "Unknown error")}],
                                        "isError": True
                                    }
                
                elif server.transport == "sse" and server.endpoint:
                    async with httpx.AsyncClient() as http_client:
                        response = await http_client.post(
                            f"{server.endpoint}/mcp",
                            json=request,
                            headers={"Content-Type": "application/json"}
                        )
                        if response.status_code == 200:
                            data = response.json()
                            if "result" in data:
                                return {
                                    "content": data["result"].get("content", []),
                                    "isError": data["result"].get("isError", False)
                                }
                            elif "error" in data:
                                return {
                                    "content": [{"type": "text", "text": data["error"].get("message", "Unknown error")}],
                                    "isError": True
                                }
                
                elif server.transport == "websocket":
                    client = self.clients[server_id]
                    if hasattr(client, 'send'):
                        await client.send(json.dumps(request))
                        response = await client.recv()
                        data = json.loads(response)
                        if "result" in data:
                            return {
                                "content": data["result"].get("content", []),
                                "isError": data["result"].get("isError", False)
                            }
                        elif "error" in data:
                            return {
                                "content": [{"type": "text", "text": data["error"].get("message", "Unknown error")}],
                                "isError": True
                            }
                
            except Exception as e:
                logger.error(f"Error calling tool {tool_name} on MCP server {server_id}: {e}")
                return {
                    "content": [{"type": "text", "text": f"Error calling tool: {str(e)}"}],
                    "isError": True
                }
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Tool {tool_name} not found"
                }
            ],
            "isError": True
        }
    
    async def list_resources(self, server_id: Optional[str] = None) -> List[MCPResource]:
        """List available MCP resources"""
        if server_id:
            # Get resources from specific server
            if server_id not in self.clients:
                await self.connect_server(server_id)
            
            server = self.servers.get(server_id)
            if not server:
                return []
            
            try:
                # Call MCP resources/list method using JSON-RPC 2.0
                request = {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": MCPMethod.LIST_RESOURCES,
                    "params": {}
                }
                
                resources_list = []
                
                if server.transport == "stdio" and server_id in self.clients:
                    client = self.clients[server_id]
                    if hasattr(client, 'stdin') and client.stdin:
                        request_json = json.dumps(request) + "\n"
                        client.stdin.write(request_json.encode())
                        client.stdin.flush()
                        
                        if hasattr(client, 'stdout') and client.stdout:
                            response_line = client.stdout.readline()
                            if response_line:
                                response = json.loads(response_line.decode())
                                if "result" in response and "resources" in response["result"]:
                                    for resource_data in response["result"]["resources"]:
                                        mcp_resource = MCPResource(
                                            uri=resource_data.get("uri", ""),
                                            name=resource_data.get("name", ""),
                                            description=resource_data.get("description"),
                                            mimeType=resource_data.get("mimeType")
                                        )
                                        resources_list.append(mcp_resource)
                
                elif server.transport == "sse" and server.endpoint:
                    async with httpx.AsyncClient() as http_client:
                        response = await http_client.post(
                            f"{server.endpoint}/mcp",
                            json=request,
                            headers={"Content-Type": "application/json"}
                        )
                        if response.status_code == 200:
                            data = response.json()
                            if "result" in data and "resources" in data["result"]:
                                for resource_data in data["result"]["resources"]:
                                    mcp_resource = MCPResource(
                                        uri=resource_data.get("uri", ""),
                                        name=resource_data.get("name", ""),
                                        description=resource_data.get("description"),
                                        mimeType=resource_data.get("mimeType")
                                    )
                                    resources_list.append(mcp_resource)
                
                elif server.transport == "websocket" and server_id in self.clients:
                    client = self.clients[server_id]
                    if hasattr(client, 'send'):
                        await client.send(json.dumps(request))
                        response = await client.recv()
                        data = json.loads(response)
                        if "result" in data and "resources" in data["result"]:
                            for resource_data in data["result"]["resources"]:
                                mcp_resource = MCPResource(
                                    uri=resource_data.get("uri", ""),
                                    name=resource_data.get("name", ""),
                                    description=resource_data.get("description"),
                                    mimeType=resource_data.get("mimeType")
                                )
                                resources_list.append(mcp_resource)
                
                # Cache resources from remote server
                for resource in resources_list:
                    self.resources[f"{server_id}:{resource.uri}"] = resource
                
                return resources_list
                
            except Exception as e:
                logger.error(f"Error listing resources from MCP server {server_id}: {e}")
                return []
        
        return list(self.resources.values())
    
    async def read_resource(self, uri: str, server_id: Optional[str] = None) -> Dict[str, Any]:
        """Read an MCP resource"""
        # Check local resources first
        if uri in self.resources:
            resource = self.resources[uri]
            # For local resources, try to read actual content
            try:
                if uri.startswith("file://"):
                    import os
                    file_path = uri.replace("file://", "")
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        return {
                            "contents": [
                                {
                                    "uri": resource.uri,
                                    "mimeType": resource.mimeType or "text/plain",
                                    "text": content
                                }
                            ]
                        }
            except Exception as e:
                logger.warning(f"Error reading local resource {uri}: {e}")
        
        # Try to read from remote server if server_id provided
        if server_id and server_id in self.clients:
            server = self.servers.get(server_id)
            if not server:
                return {"contents": []}
            
            try:
                # Call MCP resources/read method using JSON-RPC 2.0
                request = {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": MCPMethod.READ_RESOURCE,
                    "params": {
                        "uri": uri
                    }
                }
                
                if server.transport == "stdio":
                    client = self.clients[server_id]
                    if hasattr(client, 'stdin') and client.stdin:
                        request_json = json.dumps(request) + "\n"
                        client.stdin.write(request_json.encode())
                        client.stdin.flush()
                        
                        if hasattr(client, 'stdout') and client.stdout:
                            response_line = client.stdout.readline()
                            if response_line:
                                response = json.loads(response_line.decode())
                                if "result" in response:
                                    return {"contents": response["result"].get("contents", [])}
                
                elif server.transport == "sse" and server.endpoint:
                    async with httpx.AsyncClient() as http_client:
                        response = await http_client.post(
                            f"{server.endpoint}/mcp",
                            json=request,
                            headers={"Content-Type": "application/json"}
                        )
                        if response.status_code == 200:
                            data = response.json()
                            if "result" in data:
                                return {"contents": data["result"].get("contents", [])}
                
                elif server.transport == "websocket":
                    client = self.clients[server_id]
                    if hasattr(client, 'send'):
                        await client.send(json.dumps(request))
                        response = await client.recv()
                        data = json.loads(response)
                        if "result" in data:
                            return {"contents": data["result"].get("contents", [])}
                
            except Exception as e:
                logger.error(f"Error reading resource {uri} from MCP server {server_id}: {e}")
        
        return {"contents": []}
    
    async def list_prompts(self, server_id: Optional[str] = None) -> List[MCPPrompt]:
        """List available MCP prompts"""
        if server_id:
            # Get prompts from specific server
            if server_id not in self.clients:
                await self.connect_server(server_id)
            
            server = self.servers.get(server_id)
            if not server:
                return []
            
            try:
                # Call MCP prompts/list method using JSON-RPC 2.0
                request = {
                    "jsonrpc": "2.0",
                    "id": 6,
                    "method": MCPMethod.LIST_PROMPTS,
                    "params": {}
                }
                
                prompts_list = []
                
                if server.transport == "stdio" and server_id in self.clients:
                    client = self.clients[server_id]
                    if hasattr(client, 'stdin') and client.stdin:
                        request_json = json.dumps(request) + "\n"
                        client.stdin.write(request_json.encode())
                        client.stdin.flush()
                        
                        if hasattr(client, 'stdout') and client.stdout:
                            response_line = client.stdout.readline()
                            if response_line:
                                response = json.loads(response_line.decode())
                                if "result" in response and "prompts" in response["result"]:
                                    for prompt_data in response["result"]["prompts"]:
                                        mcp_prompt = MCPPrompt(
                                            name=prompt_data.get("name", ""),
                                            description=prompt_data.get("description"),
                                            arguments=prompt_data.get("arguments")
                                        )
                                        prompts_list.append(mcp_prompt)
                
                elif server.transport == "sse" and server.endpoint:
                    async with httpx.AsyncClient() as http_client:
                        response = await http_client.post(
                            f"{server.endpoint}/mcp",
                            json=request,
                            headers={"Content-Type": "application/json"}
                        )
                        if response.status_code == 200:
                            data = response.json()
                            if "result" in data and "prompts" in data["result"]:
                                for prompt_data in data["result"]["prompts"]:
                                    mcp_prompt = MCPPrompt(
                                        name=prompt_data.get("name", ""),
                                        description=prompt_data.get("description"),
                                        arguments=prompt_data.get("arguments")
                                    )
                                    prompts_list.append(mcp_prompt)
                
                elif server.transport == "websocket" and server_id in self.clients:
                    client = self.clients[server_id]
                    if hasattr(client, 'send'):
                        await client.send(json.dumps(request))
                        response = await client.recv()
                        data = json.loads(response)
                        if "result" in data and "prompts" in data["result"]:
                            for prompt_data in data["result"]["prompts"]:
                                mcp_prompt = MCPPrompt(
                                    name=prompt_data.get("name", ""),
                                    description=prompt_data.get("description"),
                                    arguments=prompt_data.get("arguments")
                                )
                                prompts_list.append(mcp_prompt)
                
                # Cache prompts from remote server
                for prompt in prompts_list:
                    self.prompts[f"{server_id}:{prompt.name}"] = prompt
                
                return prompts_list
                
            except Exception as e:
                logger.error(f"Error listing prompts from MCP server {server_id}: {e}")
                return []
        
        return list(self.prompts.values())
    
    async def get_prompt(
        self,
        prompt_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        server_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get an MCP prompt"""
        if prompt_name in self.prompts:
            prompt = self.prompts[prompt_name]
            return {
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": f"Prompt: {prompt.name}\nDescription: {prompt.description or ''}"
                        }
                    }
                ]
            }
        
        return {"messages": []}
    
    def get_tool_as_langchain_tool(self, tool_name: str):
        """Convert an MCP tool to a LangChain tool"""
        from langchain_core.tools import StructuredTool
        from pydantic import BaseModel, Field
        
        if tool_name not in self.tools:
            return None
        
        mcp_tool = self.tools[tool_name]
        
        # Create Pydantic model from input schema
        input_schema = mcp_tool.inputSchema
        properties = input_schema.get("properties", {})
        required = input_schema.get("required", [])
        
        # Build dynamic Pydantic model
        fields = {}
        for prop_name, prop_def in properties.items():
            field_type = str  # Default to string
            if prop_def.get("type") == "integer":
                field_type = int
            elif prop_def.get("type") == "number":
                field_type = float
            elif prop_def.get("type") == "boolean":
                field_type = bool
            
            field = Field(
                description=prop_def.get("description", ""),
                default=None if prop_name not in required else ...
            )
            fields[prop_name] = (field_type, field)
        
        # Create dynamic model class
        ToolInput = type("ToolInput", (BaseModel,), fields)
        ToolInput.model_config = {"arbitrary_types_allowed": True}
        
        # Create tool function
        async def tool_func(**kwargs):
            result = await self.call_tool(tool_name, kwargs)
            if result.get("isError"):
                return result["content"][0]["text"]
            return result["content"][0]["text"]
        
        # Create LangChain tool
        return StructuredTool.from_function(
            func=tool_func,
            name=mcp_tool.name,
            description=mcp_tool.description,
            args_schema=ToolInput
        )


# Global MCP service instance
mcp_service = MCPService()


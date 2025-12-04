"""
FastMCP Manager Service
Using FastMCP framework for robust MCP server/client management
"""
import logging
import asyncio
import time
from typing import Dict, Any, Optional, List, Tuple
from anyio import ClosedResourceError
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from fastmcp import Client
from fastmcp.exceptions import McpError
import json
import traceback
import hashlib
import shutil
import os
from contextlib import AsyncExitStack

# Import OpenLLMetry decorators and telemetry service
try:
    from traceloop.sdk.decorators import tool as tool_decorator
    TRACELOOP_ENABLED = True
except ImportError:
    def tool_decorator(name=None, **kwargs):
        def decorator(func):
            return func
        return decorator
    TRACELOOP_ENABLED = False

logger = logging.getLogger(__name__)

# Connection timeout settings
CONNECTION_TIMEOUT = 30  # seconds
PING_TIMEOUT = 10  # seconds
TOOL_EXECUTION_TIMEOUT = 60  # seconds for tool execution (wait tools need more time)
MAX_CONNECTION_ATTEMPTS = 3
BASE_RETRY_DELAY = 2  # seconds
MAX_RETRY_DELAY = 15  # seconds


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
        self.exit_stacks: Dict[str, AsyncExitStack] = {}  # Keep connections alive
        self.cached_tools: Dict[str, List[Dict[str, Any]]] = {}
        self.cached_resources: Dict[str, List[Dict[str, Any]]] = {}
        self.cached_prompts: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = asyncio.Lock()
        # Tool result cache: (server_id, tool_name, args_hash) -> (result, timestamp)
        self._tool_cache: Dict[Tuple[str, str, str], Tuple[Any, datetime]] = {}
        self._cache_ttl = 30  # Cache results for 30 seconds
        # Circuit breaker: (server_id, tool_name) -> failure_count
        self._failure_counts: Dict[Tuple[str, str], int] = {}
        self._circuit_breaker_threshold = 3  # Open circuit after 3 consecutive failures
    
    def _validate_auth_config(self, config: MCPServerConfig) -> None:
        """
        Validate authentication configuration and warn about potential issues.
        
        Args:
            config: MCP server configuration to validate
        """
        if config.transport_type in ("http", "sse"):
            has_auth_token = bool(config.auth_token and config.auth_token.strip())
            has_auth_header = False
            
            if config.headers:
                has_auth_header = any(k.lower() == 'authorization' for k in config.headers.keys())
            
            if not has_auth_token and not has_auth_header:
                logger.warning(
                    f"⚠️  Server '{config.name}' ({config.server_id}) has no authentication configured. "
                    f"If the remote MCP server requires authentication, connection will fail."
                )
            elif has_auth_token and len(config.auth_token.strip()) < 10:
                logger.warning(
                    f"⚠️  Server '{config.name}' ({config.server_id}) has a suspiciously short API key "
                    f"({len(config.auth_token.strip())} characters). Please verify it's correct."
                )
    
    async def register_server(self, config: MCPServerConfig) -> bool:
        """
        Register an MCP server configuration.
        
        Args:
            config: MCP server configuration
            
        Returns:
            True if successfully registered
        """
        async with self._lock:
            # Validate authentication configuration
            self._validate_auth_config(config)
            
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
        last_error_msg = None
        connection_successful = False
        
        # Use lock to prevent race conditions during connection
        async with self._lock:
            # Double check if already connected inside lock
            if server_id in self.clients:
                return True

            for attempt in range(1, MAX_CONNECTION_ATTEMPTS + 1):
                try:
                    config.status = "connecting"
                    logger.info(
                        f"Connecting to MCP server: {server_id} ({config.name}) via {config.transport_type}"
                        f" [attempt {attempt}/{MAX_CONNECTION_ATTEMPTS}]"
                    )
                    logger.info(f"URL/Command: {config.url or config.command}")
                    
                    # Create FastMCP client based on transport type
                    client = self._create_client_instance(config)
                    
                    # Create exit stack for persistent connection
                    stack = AsyncExitStack()
                    
                    try:
                        logger.info(f"Establishing persistent connection to {server_id}...")
                        async with asyncio.timeout(CONNECTION_TIMEOUT):
                            # Enter client context and keep it open
                            await stack.enter_async_context(client)
                            
                            # Store stack and client
                            # Lock is already held by outer block, no need to re-acquire
                            self.exit_stacks[server_id] = stack
                            self.clients[server_id] = client
                            
                            # Connection established! Now test it
                            logger.info(f"Testing connection to {server_id} with ping...")
                            try:
                                await asyncio.wait_for(client.ping(), timeout=PING_TIMEOUT)
                                logger.info(f"✓ Ping successful for {server_id}")
                            except asyncio.TimeoutError:
                                logger.warning(f"Ping timeout for {server_id}, trying list_tools as fallback...")
                                await asyncio.wait_for(client.list_tools(), timeout=PING_TIMEOUT)
                                logger.info(f"✓ Fallback connection test (list_tools) successful for {server_id}")
                            except Exception as ping_error:
                                logger.warning(
                                    f"Ping failed for {server_id}: {ping_error}. Trying to list tools as fallback..."
                                )
                                try:
                                    tools = await asyncio.wait_for(client.list_tools(), timeout=PING_TIMEOUT)
                                    logger.info(
                                        f"✓ Fallback connection test (list_tools) successful for {server_id}, found {len(tools)} tools"
                                    )
                                except Exception as list_error:
                                    raise Exception(
                                        f"Both ping and list_tools failed. Ping error: {ping_error}. List tools error: {list_error}"
                                    )
                            
                            # Discover capabilities while connection is active
                            logger.info(f"Discovering capabilities for {server_id}...")
                            await self._discover_capabilities_in_context(server_id, client)

                    except Exception as e:
                        # If connection failed, ensure we close the stack
                        await stack.aclose()
                        raise e
                    
                    # Connection test successful
                    config.status = "active"
                    config.last_connected = datetime.now()
                    config.last_error = None
                    connection_successful = True
                    
                    logger.info(
                        f"✓ Successfully connected to MCP server: {server_id} (Tools: {config.tools_count}, Resources: {config.resources_count}, Prompts: {config.prompts_count})"
                    )
                    return True
                    
                except asyncio.TimeoutError:
                    last_error_msg = (
                        f"Connection timeout after {CONNECTION_TIMEOUT}s - The MCP server is not responding. "
                        "Please check if the server URL is correct and the service is online."
                    )
                    logger.error(f"Timeout connecting to MCP server {server_id}: {last_error_msg}")
                except Exception as e:
                    error_msg = str(e)
                    user_friendly_msg = self._classify_connection_error(error_msg)
                    last_error_msg = user_friendly_msg
                    
                    logger.error(f"Error connecting to MCP server {server_id}: {e}")
                    logger.error("Full traceback:")
                    import traceback
                    traceback.print_exc()
                finally:
                    # Ensure client cleanup only if connection was not successful
                    if not connection_successful:
                        # Lock is already held
                        if server_id in self.exit_stacks:
                            await self.exit_stacks[server_id].aclose()
                            del self.exit_stacks[server_id]
                        if server_id in self.clients:
                            del self.clients[server_id]
                
                # Decide whether to retry
                if attempt < MAX_CONNECTION_ATTEMPTS and last_error_msg and self._is_transient_error(last_error_msg):
                    delay = self._get_backoff_delay(attempt)
                    logger.warning(
                        f"Retrying connection to {server_id} in {delay}s (attempt {attempt + 1}/{MAX_CONNECTION_ATTEMPTS})"
                    )
                    await asyncio.sleep(delay)
                    continue
                else:
                    break
            
            # All attempts failed
            config.status = "error"
            config.last_error = last_error_msg or "Failed to connect"
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
        # Build auth parameter for remote transports
        # Support multiple authentication methods:
        # 1. auth_token with auth_type="bearer" 
        # 2. Authorization header in headers dict
        # 3. auth_token alone (will be treated as bearer)
        auth = None
        headers = config.headers or {}
        
        # Debug logging to trace auth configuration
        logger.info(f"Creating client for {config.server_id}:")
        logger.info(f"  - transport_type: {config.transport_type}")
        logger.info(f"  - auth_type: {config.auth_type}")
        logger.info(f"  - auth_token present: {bool(config.auth_token)}")
        logger.info(f"  - auth_token length: {len(config.auth_token) if config.auth_token else 0}")
        logger.info(f"  - headers keys: {list(headers.keys())}")
        
        # Check if Authorization header already exists in headers
        has_auth_header = any(k.lower() == 'authorization' for k in headers.keys()) if headers else False
        
        if config.auth_type == "bearer" and config.auth_token:
            # Explicit bearer token configuration
            auth = config.auth_token
            # FORCE: Add to headers to be absolutely sure
            if not has_auth_header:
                # Special handling for Browser Use MCP
                if config.url and "api.browser-use.com" in config.url:
                    headers["X-Browser-Use-API-Key"] = config.auth_token
                    logger.info(f"✓ Added X-Browser-Use-API-Key header for {config.server_id}")
                else:
                    headers["Authorization"] = f"Bearer {config.auth_token}"
                    logger.info(f"✓ Added Authorization header for {config.server_id}")
            logger.info(f"✓ Using bearer token authentication for {config.server_id} (explicit auth_type)")
        elif config.auth_token and not has_auth_header:
            # auth_token provided without auth_type - assume bearer
            auth = config.auth_token
            # FORCE: Add to headers to be absolutely sure
            # Special handling for Browser Use MCP
            if config.url and "api.browser-use.com" in config.url:
                headers["X-Browser-Use-API-Key"] = config.auth_token
                logger.info(f"✓ Added X-Browser-Use-API-Key header for {config.server_id}")
            else:
                headers["Authorization"] = f"Bearer {config.auth_token}"
                logger.info(f"✓ Added Authorization header for {config.server_id}")
            logger.info(f"✓ Using token authentication (assuming bearer) for {config.server_id}")
        elif has_auth_header:
            # Authorization header already in headers - no need for separate auth
            logger.info(f"✓ Using Authorization header from headers dict for {config.server_id}")
        else:
            logger.info(f"⚠️  No authentication configured for {config.server_id}")
        
        # Remote HTTP/SSE transports
        if config.transport_type in ("http", "sse"):
            if not config.url:
                raise ValueError("URL required for HTTP/SSE transport")
            
            # Explicitly use transport classes to support headers
            from fastmcp.client import SSETransport, StreamableHttpTransport
            
            transport = None
            if config.transport_type == "sse":
                transport = SSETransport(
                    url=config.url,
                    headers=headers,
                    auth=auth,
                    sse_read_timeout=TOOL_EXECUTION_TIMEOUT
                )
            else: # http
                # Default to StreamableHttpTransport for "http" type if not specified
                # But FastMCP might infer SSE from URL if we didn't force it.
                # Since we have explicit types in config, we honor them.
                transport = StreamableHttpTransport(
                    url=config.url,
                    headers=headers,
                    auth=auth
                )
                
            return Client(
                transport=transport,
                timeout=TOOL_EXECUTION_TIMEOUT
            )
        
        # Local STDIO transports
        elif config.transport_type == "stdio":
            # STDIO transport (local script/process)
            if not config.command:
                raise ValueError("Command required for STDIO transport")

            # Resolve command path (e.g. 'npx' -> '/usr/local/bin/npx')
            command_path = shutil.which(config.command) or config.command
            logger.info(f"Creating STDIO client for command: {command_path} (original: {config.command})")

            server_key = (config.name or config.server_id).strip() or config.server_id

            # Prepare environment: Start with system env, then override with config env
            env = os.environ.copy()
            if config.env:
                config_env = config.env
                if isinstance(config_env, str):
                    try:
                        config_env = json.loads(config_env)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse env JSON for server {config.name}, using empty dict")
                        config_env = {}
                
                if isinstance(config_env, dict):
                    env.update(config_env)

            stdio_server_definition: Dict[str, Any] = {
                "transport": "stdio",
                "command": command_path,
                "args": config.args or [],
                "env": env
            }
            
            # Handle string args if necessary
            if isinstance(stdio_server_definition["args"], str):
                try:
                    stdio_server_definition["args"] = json.loads(stdio_server_definition["args"])
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse args JSON for server {config.name}, using empty list")
                    stdio_server_definition["args"] = []

            if config.cwd:
                stdio_server_definition["cwd"] = config.cwd

            mcp_config = {
                "mcpServers": {
                    server_key: stdio_server_definition
                }
            }

            return Client(mcp_config, timeout=TOOL_EXECUTION_TIMEOUT)
        
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
                    if server_id in self.exit_stacks:
                        await self.exit_stacks[server_id].aclose()
                        del self.exit_stacks[server_id]
                    if server_id in self.clients:
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
            cached = self.cached_tools.get(server_id)
            if cached:
                return cached
            
            # Ensure the server is registered before attempting reconnect
            if server_id not in self.servers:
                logger.warning(f"Requested tools for unregistered MCP server {server_id}")
                return []
            
            # No cached tools - attempt to reconnect/discover tools on demand
            logger.info(f"Tools for {server_id} not cached. Attempting to reconnect and discover tools...")
            success = await self.connect_server(server_id)
            if success:
                return self.cached_tools.get(server_id, [])
            else:
                logger.error(f"Unable to load tools for MCP server {server_id}: connection failed")
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
    
    def _get_cache_key(self, server_id: str, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Generate a cache key for tool results"""
        args_str = json.dumps(arguments, sort_keys=True)
        return hashlib.md5(f"{server_id}:{tool_name}:{args_str}".encode()).hexdigest()
    
    def _get_cached_result(self, server_id: str, tool_name: str, arguments: Dict[str, Any]) -> Optional[Any]:
        """Retrieve cached tool result if valid"""
        cache_key = (server_id, tool_name, self._get_cache_key(server_id, tool_name, arguments))
        if cache_key in self._tool_cache:
            result, timestamp = self._tool_cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self._cache_ttl):
                logger.debug(f"Cache hit for {tool_name} on {server_id}")
                return result
            else:
                # Expired, remove from cache
                del self._tool_cache[cache_key]
        return None
    
    def _cache_result(self, server_id: str, tool_name: str, arguments: Dict[str, Any], result: Any):
        """Cache a tool result"""
        cache_key = (server_id, tool_name, self._get_cache_key(server_id, tool_name, arguments))
        self._tool_cache[cache_key] = (result, datetime.now())
        logger.debug(f"Cached result for {tool_name} on {server_id}")
    
    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if error is a rate limit (429)"""
        error_str = str(error)
        return "429" in error_str or "Too Many Requests" in error_str or "rate limit" in error_str.lower()
    
    def _is_timeout_error(self, error: Exception) -> bool:
        """Check if error is a timeout"""
        error_str = str(error).lower()
        return "timeout" in error_str or "timed out" in error_str

    def _is_connection_error(self, error: Exception) -> bool:
        """Check if error is a connection/network issue"""
        error_str = str(error).lower()
        connection_keywords = [
            "connection refused",
            "connection reset",
            "broken pipe",
            "connection closed",
            "server disconnected",
            "socket closed",
            "network error",
            "remote end closed",
            "client is not connected"
        ]
        return (
            isinstance(error, (ConnectionError, BrokenPipeError, OSError, IOError)) or
            any(k in error_str for k in connection_keywords)
        )
    
    def _extract_retry_after(self, error: Exception) -> Optional[int]:
        """Extract Retry-After header value if present"""
        # This is a simple heuristic; in practice, you'd parse the actual HTTP response
        error_str = str(error)
        if "retry-after" in error_str.lower():
            import re
            match = re.search(r"retry-after[:\s]+(\d+)", error_str, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    async def call_tool(self, server_id: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on an MCP server with rate-limit handling and caching.
        
        CRITICAL: Uses async with to establish connection for each call.
        
        Args:
            server_id: Server ID
            tool_name: Tool name (unprefixed)
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        # Check cache first
        cached = self._get_cached_result(server_id, tool_name, arguments)
        if cached is not None:
            # Set telemetry attributes for cached result
            try:
                from services.telemetry_service import telemetry_service
                current_span = telemetry_service.get_current_span()
                if current_span and current_span.is_recording():
                    current_span.set_attribute("tool.name", tool_name)
                    current_span.set_attribute("tool.server_id", server_id)
                    current_span.set_attribute("tool.cached", True)
                    current_span.set_attribute("tool.success", True)
            except Exception:
                pass
            return cached
            
        logger.info(f"Executing tool {tool_name} on {server_id}")
        
        # Check circuit breaker
        circuit_key = (server_id, tool_name)
        failure_count = self._failure_counts.get(circuit_key, 0)
        logger.debug(f"Circuit breaker check for {tool_name} on {server_id}: {failure_count} failures (threshold: {self._circuit_breaker_threshold})")
        if failure_count >= self._circuit_breaker_threshold:
            logger.error(
                f"Circuit breaker OPEN for {tool_name} on {server_id} after {failure_count} failures. "
                f"Refusing to call tool to prevent hammering."
            )
            raise Exception(
                f"Circuit breaker open for {tool_name}: too many consecutive failures. "
                f"The tool or server may be experiencing issues. Please try a different approach."
            )
        
        max_attempts = 2  # Retry once on connection errors, but fail fast on tool errors
        attempt = 0
        last_error: Optional[Exception] = None
        base_delay = 2.0  # Base delay for exponential backoff

        while attempt < max_attempts:
            attempt += 1

            if server_id not in self.clients:
                # Try to connect if not connected
                if not await self.connect_server(server_id):
                    raise Exception(f"Server {server_id} not connected")
            
            client = self.clients[server_id]

            try:
                # Add OpenTelemetry tracing for tool execution
                from services.telemetry_service import telemetry_service
                
                start_time = time.time()
                
                # Create span for tool execution
                try:
                    current_span = telemetry_service.get_current_span()
                    if current_span and current_span.is_recording():
                        # Set tool attributes
                        current_span.set_attribute("tool.name", tool_name)
                        current_span.set_attribute("tool.server_id", server_id)
                        current_span.set_attribute("tool.server_name", self.servers[server_id].name if server_id in self.servers else "unknown")
                        current_span.set_attribute("tool.input", json.dumps(arguments)[:1000])  # Limit size
                        current_span.set_attribute("mcp.server_id", server_id)
                        current_span.set_attribute("mcp.tool_name", tool_name)
                except Exception as attr_error:
                    logger.debug(f"Could not set tool attributes: {attr_error}")
                
                # ✅ CRITICAL: Use existing persistent connection!
                # Client is already entered in connect_server
                result = await client.call_tool(tool_name, arguments)
                result_data = result.data if hasattr(result, 'data') else result
                
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000
                
                # Set success attributes
                try:
                    current_span = telemetry_service.get_current_span()
                    if current_span and current_span.is_recording():
                        current_span.set_attribute("tool.success", True)
                        current_span.set_attribute("tool.execution_time_ms", duration_ms)
                        current_span.set_attribute("tool.output", json.dumps(result_data)[:1000])  # Limit size
                        current_span.set_attribute("tool.cached", False)
                except Exception as attr_error:
                    logger.debug(f"Could not set success attributes: {attr_error}")
                
                # Success! Cache and return
                self._cache_result(server_id, tool_name, arguments, result_data)
                
                # Reset failure count on success
                if circuit_key in self._failure_counts:
                    del self._failure_counts[circuit_key]
                    
                return result_data

            except Exception as e:
                last_error = e
                
                # Helper to handle retry exhaustion for system errors
                async def handle_retry_or_raise(is_disconnect: bool = False):
                    if attempt == max_attempts:
                        current_failures = self._failure_counts.get(circuit_key, 0)
                        self._failure_counts[circuit_key] = current_failures + 1
                        logger.warning(f"Circuit breaker: Incrementing failure count for {tool_name} on {server_id}: {current_failures} -> {current_failures + 1} (all attempts exhausted)")
                        raise e
                    
                    if is_disconnect:
                        logger.info(f"Forcing disconnect for {server_id} to recover from connection error")
                        await self.disconnect_server(server_id)
                    
                    # Wait before retry
                    wait_time = base_delay if not self._is_rate_limit_error(e) else (self._extract_retry_after(e) or (base_delay * (2 ** (attempt - 1))))
                    if self._is_rate_limit_error(e):
                        logger.warning(f"Rate limit hit for {tool_name}, waiting {wait_time}s")
                    elif self._is_timeout_error(e):
                        logger.warning(f"Timeout calling {tool_name}, retrying...")
                    
                    await asyncio.sleep(wait_time)

                # 0. Check for Auth Errors -> Fail Fast
                if "401" in str(e) or "Unauthorized" in str(e):
                    logger.error(f"Authentication failed for {server_id} during tool execution. This usually means the API key is invalid or has insufficient credits.")
                    raise Exception(f"Authentication failed for {server_id}. Please check your API key and credits/quota.")

                # 1. Check for Rate Limits -> Wait & Retry
                if self._is_rate_limit_error(e):
                    await handle_retry_or_raise()
                    continue
                
                # 2. Check for Timeouts -> Wait & Retry
                if self._is_timeout_error(e):
                    await handle_retry_or_raise()
                    continue

                # 3. Check for Connection Errors -> Disconnect & Retry
                if self._is_connection_error(e):
                    logger.warning(f"Connection error calling {tool_name} on {server_id}: {e}")
                    await handle_retry_or_raise(is_disconnect=True)
                    continue
                
                # 4. Tool Logic Errors (e.g. "No open pages") -> Fail Fast
                # Do NOT disconnect (preserves browser state)
                # Do NOT retry (logic errors usually don't fix themselves)
                # Do NOT increment failure count (server is healthy)
                logger.warning(f"Tool logic error calling {tool_name} on {server_id}: {e}")
                raise e

                
            except Exception as e:
                last_error = e
                error_str = str(e)
                
                # Debug: Log response body if available
                if hasattr(e, 'response') and hasattr(e.response, 'text'):
                    logger.error(f"Error response body from {server_id}: {e.response.text}")
                if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                    logger.error(f"Error status code from {server_id}: {e.response.status_code}")

                # Check for rate limit or timeout in generic exceptions
                if self._is_rate_limit_error(e):
                    retry_after = self._extract_retry_after(e) or int(base_delay * (2 ** (attempt - 1)))
                    logger.warning(
                        f"Rate limit (429) detected for {tool_name} on {server_id} (attempt {attempt}/{max_attempts}). "
                        f"Backing off for {retry_after}s..."
                    )
                    if attempt < max_attempts:
                        await asyncio.sleep(retry_after)
                        continue
                elif self._is_timeout_error(e):
                    logger.warning(
                        f"Timeout calling {tool_name} on {server_id} (attempt {attempt}/{max_attempts})"
                    )
                    if attempt < max_attempts:
                        await asyncio.sleep(base_delay * attempt)
                        continue
                
                logger.error(f"Error calling tool {tool_name} on {server_id}: {e}")
                current_failures = self._failure_counts.get(circuit_key, 0)
                self._failure_counts[circuit_key] = current_failures + 1
                logger.warning(f"Circuit breaker: Incrementing failure count for {tool_name} on {server_id}: {current_failures} -> {current_failures + 1}")
                break

        # All attempts exhausted
        current_failures = self._failure_counts.get(circuit_key, 0)
        self._failure_counts[circuit_key] = current_failures + 1
        logger.warning(f"Circuit breaker: Incrementing failure count for {tool_name} on {server_id}: {current_failures} -> {current_failures + 1} (all attempts exhausted)")
        raise last_error if last_error else Exception(
            f"Failed to call tool {tool_name} on {server_id}: unknown error after {max_attempts} attempts"
        )
    
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
            # ✅ Use existing persistent connection
            # DO NOT use 'async with client' here as it closes the connection on exit!
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
            # ✅ Use existing persistent connection
            # DO NOT use 'async with client' here as it closes the connection on exit!
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
            # ✅ Use existing persistent connection
            # DO NOT use 'async with client' here as it closes the connection on exit!
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
    
    def _classify_connection_error(self, error_msg: str) -> str:
        """Classify error and return user-friendly message."""
        if "500" in error_msg or "Internal Server Error" in error_msg:
            return "The MCP server is experiencing technical issues (HTTP 500). This is a temporary problem with the service provider. Please try again in a few minutes."
        elif "502" in error_msg or "Bad Gateway" in error_msg:
            return "The MCP server gateway is unavailable (HTTP 502). The service may be temporarily down for maintenance."
        elif "503" in error_msg or "Service Unavailable" in error_msg:
            return "The MCP server is temporarily unavailable (HTTP 503). Please try again later."
        elif "504" in error_msg or "Gateway Timeout" in error_msg:
            return "The MCP server request timed out (HTTP 504). The service may be overloaded."
        elif "401" in error_msg or "Unauthorized" in error_msg:
            return "Authentication failed. Please check your API key or credentials."
        elif "403" in error_msg or "Forbidden" in error_msg:
            return "Access denied. You may not have permission to access this MCP server."
        elif "404" in error_msg or "Not Found" in error_msg:
            return "MCP server endpoint not found. Please verify the server URL is correct."
        elif "connection refused" in error_msg.lower():
            return "Connection refused. The MCP server may be offline or the URL may be incorrect."
        elif "name or service not known" in error_msg.lower() or "failed to resolve" in error_msg.lower():
            return "Cannot resolve server hostname. Please check the server URL."
        elif "timeout" in error_msg.lower():
            return "The MCP server is not responding. Please check if the server URL is correct and the service is online."
        else:
            return f"Failed to connect: {error_msg}"
    
    def _is_transient_error(self, message: str) -> bool:
        """Determine if error is transient and worth retrying."""
        transient_keywords = [
            "temporary",
            "try again",
            "gateway",
            "timeout",
            "unavailable",
            "overloaded",
            "experiencing"
        ]
        lowered = message.lower()
        return any(keyword in lowered for keyword in transient_keywords)
    
    def _get_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        import random
        delay = min(BASE_RETRY_DELAY * (2 ** (attempt - 1)), MAX_RETRY_DELAY)
        jitter = random.uniform(0, 1)
        return round(delay + jitter, 2)


# Global FastMCP manager instance
fastmcp_manager = FastMCPManager()

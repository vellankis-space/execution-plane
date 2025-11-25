import uuid
import json
import re
import os
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Annotated, Set
from pydantic import Field, create_model
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.language_models import FakeListLLM
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
import hashlib
import base64
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

from services.memory_service import MemoryService
from services.tools_service import ToolsService
from services.cost_tracking_service import CostTrackingService
from services.llm_service import LLMService
from services.rate_limit_handler import RateLimitHandler, RateLimitError
from services.fastmcp_manager import fastmcp_manager
from middleware.pii_middleware import create_pii_middleware_from_config, PIIMiddleware

from models.agent import Agent as AgentModel
from models.mcp_server import AgentMCPServer, MCPServer
from schemas.agent import AgentCreate, AgentInDB
from core.config import settings
from sqlalchemy import text


class AgentService:
    def __init__(self, db: Session):
        self.db = db
        # Generate encryption key from settings or create a default one
        # In production, this should be stored securely
        self._encryption_key = self._get_or_create_encryption_key()
        
        # Initialize memory service for mem0 integration
        self.memory_service = MemoryService()
        
        # Initialize tools service for external tools
        self.tools_service = ToolsService()
        
        # Initialize cost tracking service
        self.cost_service = CostTrackingService(db)
        
        # Initialize LLM service (with LiteLLM support)
        self.llm_service = LLMService()
        
        # Ensure database schema compatibility (add columns if missing)
        try:
            self._ensure_schema()
        except Exception as e:
            # Do not fail service init if schema check fails; log and continue
            print(f"Schema check warning: {e}")

    @staticmethod
    def _safeguard_puppeteer_script(script: str) -> str:
        """Automatically add optional chaining to common DOM selectors to prevent null errors."""
        if not isinstance(script, str) or not script:
            return script

        updated = script
        updated = re.sub(r"(document\.querySelector\([^)]*\))\.", r"\1?.", updated)
        updated = re.sub(r"(document\.querySelectorAll\([^)]*\)\[[^]]+\])\.", r"\1?.", updated)
        updated = re.sub(r"(\.querySelector\([^)]*\))\.", r"\1?.", updated)
        updated = re.sub(r"(\.querySelectorAll\([^)]*\)\[[^]]+\])\.", r"\1?.", updated)

        return updated

    @staticmethod
    def _json_schema_to_python_type(prop_schema: Dict[str, Any]) -> Any:
        """Map a JSON schema type definition to an approximate Python type for Pydantic."""
        schema_type = prop_schema.get("type")
        if schema_type == "string":
            return str
        if schema_type == "integer":
            return int
        if schema_type == "number":
            return float
        if schema_type == "boolean":
            return bool
        if schema_type == "array":
            return List[Any]
        if schema_type == "object":
            return Dict[str, Any]
        return Any

    @staticmethod
    def _is_missing_value(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        if isinstance(value, list) and len(value) == 0:
            return True
        if isinstance(value, dict) and len(value) == 0:
            return False  # allow empty dicts by default
        return False

    def _ensure_schema(self):
        """Ensure required columns exist; add them if missing (SQLite safe)."""
        # Only run for SQLite-like DBs where PRAGMA is supported; otherwise skip
        try:
            conn = self.db.connection()
            
            # Check agents table columns
            result = conn.execute(text("PRAGMA table_info(agents)")).fetchall()
            columns = {row[1] for row in result}
            # Add tool_configs column if missing
            if "tool_configs" not in columns:
                print("Adding missing 'tool_configs' column to agents table (auto-fix)...")
                conn.execute(text("ALTER TABLE agents ADD COLUMN tool_configs JSON"))
            # Add pii_config column if missing (backward-compat)
            if "pii_config" not in columns:
                print("Adding missing 'pii_config' column to agents table (auto-fix)...")
                conn.execute(text("ALTER TABLE agents ADD COLUMN pii_config JSON"))
            
            # Check agent_mcp_servers table columns
            result = conn.execute(text("PRAGMA table_info(agent_mcp_servers)")).fetchall()
            columns = {row[1] for row in result}
            # Add selected_tools column if missing
            if "selected_tools" not in columns:
                print("Adding missing 'selected_tools' column to agent_mcp_servers table (auto-fix)...")
                conn.execute(text("ALTER TABLE agent_mcp_servers ADD COLUMN selected_tools JSON"))
                print("✓ Tool selection feature enabled - users can now select specific MCP tools per agent")
        except Exception as e:
            # Re-raise to be caught by caller; helpful for logging only
            raise e
    
    def _get_or_create_encryption_key(self) -> bytes:
        # In production, this should come from a secure environment variable
        key_source = settings.SECRET_KEY.encode() if hasattr(settings, 'SECRET_KEY') and settings.SECRET_KEY else b'mech_agent_default_secret_key_32bytes!'
        # Ensure the key is 32 bytes for Fernet
        return base64.urlsafe_b64encode(hashlib.sha256(key_source).digest())
    
    def _encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key for storage"""
        f = Fernet(self._encryption_key)
        return f.encrypt(api_key.encode()).decode()
    
    def _decrypt_api_key(self, encrypted_api_key: str) -> str:
        """Decrypt API key for use"""
        f = Fernet(self._encryption_key)
        return f.decrypt(encrypted_api_key.encode()).decode()
    
    def _sanitize_tool_name(self, name: str, existing_names: Set[str]) -> str:
        """Sanitize tool names to satisfy provider constraints (Groq/OpenAI).

        Ensures names:
        - Contain only letters, numbers, underscores
        - Do not start with a digit
        - Do not exceed 64 characters
        - Are unique within the agent
        """

        sanitized = re.sub(r"\s+", "_", name)
        sanitized = re.sub(r"[^0-9A-Za-z_]", "_", sanitized)
        sanitized = re.sub(r"_+", "_", sanitized).strip("_") or "tool"

        if sanitized[0].isdigit():
            sanitized = f"tool_{sanitized}"

        sanitized = sanitized[:64]

        base_name = sanitized
        suffix = 1
        while sanitized in existing_names:
            sanitized = f"{base_name}_{suffix}"
            sanitized = sanitized[:64]
            suffix += 1

        existing_names.add(sanitized)
        return sanitized

    async def create_agent(self, agent_data: AgentCreate, tenant_id: Optional[str] = None) -> AgentInDB:
        """Create a new agent in the database"""
        agent_id = str(uuid.uuid4())
        
        # Encrypt the API key before storing
        encrypted_api_key = None
        if agent_data.api_key:
            encrypted_api_key = self._encrypt_api_key(agent_data.api_key)
        
        db_agent = AgentModel(
            agent_id=agent_id,
            name=agent_data.name,
            agent_type=agent_data.agent_type,
            llm_provider=agent_data.llm_provider,
            llm_model=agent_data.llm_model,
            temperature=agent_data.temperature,
            system_prompt=agent_data.system_prompt,
            tools=agent_data.tools,
            tool_configs=agent_data.tool_configs,
            max_iterations=agent_data.max_iterations,
            memory_type=agent_data.memory_type,
            streaming_enabled=agent_data.streaming_enabled,
            human_in_loop=agent_data.human_in_loop,
            recursion_limit=agent_data.recursion_limit,
            api_key_encrypted=encrypted_api_key,
            pii_config=agent_data.pii_config,
            version=1,  # Initial version
            tenant_id=tenant_id  # Set tenant_id for isolation
        )
        
        self.db.add(db_agent)
        self.db.commit()
        self.db.refresh(db_agent)
        print(f"Agent committed to database: {db_agent.agent_id}")
        
        # Handle MCP server associations with tool selection
        # Support both old format (mcp_servers) and new format (mcp_server_configs)
        if agent_data.mcp_server_configs:
            # New format with tool selection
            for server_config in agent_data.mcp_server_configs:
                association = AgentMCPServer(
                    agent_id=agent_id,
                    server_id=server_config.server_id,
                    enabled="true",
                    selected_tools=server_config.selected_tools
                )
                self.db.add(association)
            self.db.commit()
            print(f"Added {len(agent_data.mcp_server_configs)} MCP server associations with tool selection")
        elif agent_data.mcp_servers:
            # Old format for backward compatibility (all tools)
            for server_id in agent_data.mcp_servers:
                association = AgentMCPServer(
                    agent_id=agent_id,
                    server_id=server_id,
                    enabled="true",
                    selected_tools=None  # None = all tools
                )
                self.db.add(association)
            self.db.commit()
            print(f"Added {len(agent_data.mcp_servers)} MCP server associations")
        
        return AgentInDB.model_validate(db_agent)
    
    async def get_agent(self, agent_id: str, tenant_id: Optional[str] = None) -> Optional[AgentInDB]:
        """Retrieve an agent by ID, optionally filtered by tenant"""
        query = self.db.query(AgentModel).filter(AgentModel.agent_id == agent_id)
        
        # Apply tenant filter if provided
        if tenant_id:
            query = query.filter(AgentModel.tenant_id == tenant_id)
        
        db_agent = query.first()
        if db_agent:
            return AgentInDB.model_validate(db_agent)
        return None

    async def get_agents(self, tenant_id: Optional[str] = None) -> List[AgentInDB]:
        """Retrieve all agents, optionally filtered by tenant"""
        query = self.db.query(AgentModel)
        
        # Apply tenant filter if provided
        if tenant_id:
            query = query.filter(AgentModel.tenant_id == tenant_id)
        
        db_agents = query.all()
        return [AgentInDB.model_validate(agent) for agent in db_agents]
    
    async def delete_agent(self, agent_id: str, tenant_id: Optional[str] = None) -> bool:
        """Delete an agent by ID, optionally filtered by tenant"""
        query = self.db.query(AgentModel).filter(AgentModel.agent_id == agent_id)
        
        # Apply tenant filter if provided
        if tenant_id:
            query = query.filter(AgentModel.tenant_id == tenant_id)
        
        db_agent = query.first()
        if db_agent:
            self.db.delete(db_agent)
            self.db.commit()
            return True
        return False
    
    async def get_agent_mcp_tools(self, agent_id: str) -> List[Any]:
        """
        Load MCP tools for an agent from associated MCP servers.
        Returns a list of LangChain tools that can be used by the agent.
        """
        try:
            # Get MCP server associations for this agent
            associations = self.db.query(AgentMCPServer).filter(
                AgentMCPServer.agent_id == agent_id,
                AgentMCPServer.enabled == "true"
            ).all()
            
            if not associations:
                return []
            
            # Create a mapping of server_id to association (for selected_tools lookup)
            server_associations = {assoc.server_id: assoc for assoc in associations}
            
            # Get server IDs
            server_ids = [assoc.server_id for assoc in associations]
            
            # Get MCP servers (active or inactive - we'll try to connect inactive ones)
            servers = self.db.query(MCPServer).filter(
                MCPServer.server_id.in_(server_ids)
            ).all()
            
            if not servers:
                logger.warning(f"No MCP servers found in database for agent {agent_id}. Agent associations exist but servers are missing.")
                return []
            
            # Auto-connect inactive servers
            for server in servers:
                if server.status != "active":
                    logger.info(f"MCP server {server.name} is {server.status}. Attempting auto-connect...")
                    try:
                        # Register server if not already registered
                        if server.server_id not in fastmcp_manager.servers:
                            from services.fastmcp_manager import MCPServerConfig
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
                                cwd=server.cwd,
                                status=server.status
                            )
                            await fastmcp_manager.register_server(config)
                        
                        # Attempt connection
                        success = await fastmcp_manager.connect_server(server.server_id)
                        if success:
                            server.status = "active"
                            server.last_connected = datetime.now(timezone.utc)
                            server.last_error = None
                            self.db.commit()
                            logger.info(f"✅ Successfully auto-connected MCP server {server.name}")
                        else:
                            logger.warning(f"⚠️ Failed to auto-connect MCP server {server.name}. Server will be skipped.")
                            server.status = "error"
                            server.last_error = "Auto-connect failed"
                            self.db.commit()
                    except Exception as e:
                        logger.error(f"Error auto-connecting MCP server {server.name}: {e}")
                        server.status = "error"
                        server.last_error = str(e)
                        self.db.commit()
            
            # Filter to only active servers after connection attempts
            active_servers = [s for s in servers if s.status == "active"]
            
            if not active_servers:
                logger.warning(f"No active MCP servers available for agent {agent_id} after connection attempts. Agent will run in conversational mode without tools.")
                return []
            
            logger.info(f"Agent {agent_id} has {len(active_servers)} active MCP servers: {[s.name for s in active_servers]}")
            
            # Collect tools from all active MCP servers
            mcp_tools = []
            existing_tool_names: Set[str] = set()
            for server in active_servers:
                try:
                    # Ensure server is registered with FastMCP manager (in case backend restarted)
                    if server.server_id not in fastmcp_manager.servers:
                        logger.info(f"Re-registering MCP server {server.name} with FastMCP manager from DB")
                        from services.fastmcp_manager import MCPServerConfig

                        headers = server.headers
                        if isinstance(headers, str) and headers:
                            headers = json.loads(headers)
                        headers = headers or {}

                        args = server.args
                        if isinstance(args, str) and args:
                            args = json.loads(args)
                        args = args or []

                        env = server.env
                        env = server.env
                        if isinstance(env, str) and env:
                            try:
                                env = json.loads(env)
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse env JSON for server {server.name}, using empty dict")
                                env = {}
                        env = env or {}

                        config = MCPServerConfig(
                            server_id=server.server_id,
                            name=server.name,
                            description=server.description or "",
                            transport_type=server.transport_type,
                            url=server.url,
                            headers=headers,
                            auth_type=server.auth_type,
                            auth_token=server.auth_token,
                            command=server.command,
                            args=args,
                            env=env,
                            cwd=server.cwd,
                            status=server.status
                        )
                        await fastmcp_manager.register_server(config)
                        
                        # Connect to the server to discover tools
                        logger.info(f"Connecting to MCP server {server.name} to discover tools")
                        await fastmcp_manager.connect_server(server.server_id)
                    
                    # Get tools from FastMCP manager
                    tools = await fastmcp_manager.get_tools(server.server_id)
                    
                    # Get selected_tools for this server (if user has specified)
                    association = server_associations.get(server.server_id)
                    selected_tools = association.selected_tools if association and association.selected_tools else None
                    
                    # FIX: Handle selected_tools as JSON string (SQLAlchemy might return string instead of list)
                    if selected_tools and isinstance(selected_tools, str):
                        try:
                            selected_tools = json.loads(selected_tools)
                            logger.info(f"Parsed selected_tools from JSON string for server {server.name}")
                        except json.JSONDecodeError as e:
                            logger.warning(
                                f"selected_tools is a string but not valid JSON for server {server.name}. "
                                f"Value: {association.selected_tools}. Error: {e}"
                            )
                            selected_tools = None
                    
                    # Log for debugging
                    logger.info(f"Server {server.name}: selected_tools type={type(selected_tools)}, value={selected_tools}")
                    
                    # Filter tools if user has selected specific ones
                    if selected_tools:
                        # Only load tools that were selected by the user
                        original_count = len(tools)
                        tools = [t for t in tools if t.get("name") in selected_tools]
                        logger.info(f"Filtered from {original_count} to {len(tools)} selected tools from MCP server {server.name}")
                    else:
                        # Special handling for Playwright: Filter to core tools to save tokens
                        if "Playwright" in server.name:
                            core_playwright_tools = [
                                "browser_navigate",
                                "browser_click",
                                "browser_type",
                                "browser_wait_for",
                                "browser_evaluate",
                                "browser_take_screenshot",
                                "browser_press_key",
                                "browser_fill_form"
                            ]
                            original_count = len(tools)
                            tools = [t for t in tools if t.get("name") in core_playwright_tools]
                            logger.info(f"Auto-filtered Playwright tools from {original_count} to {len(tools)} core tools to save tokens")
                        else:
                            logger.info(f"No tool filtering - loading all {len(tools)} tools from MCP server {server.name}")
                    
                    # Convert MCP tools to LangChain tools
                    for tool_info in tools:
                        tool_name = tool_info.get("name")
                        input_schema = tool_info.get("inputSchema") or {}
                        schema_description = json.dumps(input_schema, indent=2) if input_schema else "{}"

                        # FIX: Use factory function to avoid closure bug
                        # Without this, all wrappers would call the LAST tool in the loop!
                        def make_mcp_tool_runner(server_id: str, tool_name: str, schema: dict):
                            async def _run_mcp_tool(payload: Any = None, *, extra_kwargs: Optional[Dict[str, Any]] = None) -> str:
                                arguments = payload
                                if isinstance(arguments, str):
                                    try:
                                        arguments = json.loads(arguments)
                                    except json.JSONDecodeError:
                                        raise ValueError("Payload must be valid JSON when provided as a string")
                                if arguments is None:
                                    arguments = {}
                                if not isinstance(arguments, dict):
                                    raise ValueError("Payload must be an object containing the MCP tool arguments")
                                if extra_kwargs:
                                    # kwargs take precedence / merge
                                    arguments = {**arguments, **extra_kwargs}

                                # CRITICAL FIX: Preprocess arguments to handle LLM quirks
                                # LLMs sometimes emit string 'null', 'undefined', 'none', '{}' instead of actual values
                                # This causes Pydantic validation errors like: input_value='null', input_type=str
                                if isinstance(arguments, dict):
                                    cleaned_args = {}
                                    for key, value in arguments.items():
                                        # Handle string representations of null/undefined/empty
                                        if isinstance(value, str):
                                            value_lower = value.lower().strip()
                                            
                                            # Skip null-like strings
                                            if value_lower in ['null', 'undefined', 'none']:
                                                logger.debug(f"Skipping argument '{key}' with string value '{value}' (treating as omitted)")
                                                continue
                                            
                                            # Handle string '{}' or '[]' - try to parse as JSON
                                            if value_lower in ['{}', '[]']:
                                                try:
                                                    parsed = json.loads(value)
                                                    logger.debug(f"Parsed argument '{key}' from string '{value}' to {type(parsed).__name__}")
                                                    value = parsed
                                                except json.JSONDecodeError:
                                                    logger.debug(f"Could not parse '{value}' as JSON for argument '{key}'")
                                                    continue  # Skip if can't parse
                                        
                                        cleaned_args[key] = value
                                    
                                    # Log the preprocessing results
                                    if len(cleaned_args) != len(arguments):
                                        logger.info(f"Preprocessed arguments for {tool_name}: removed {len(arguments) - len(cleaned_args)} problematic arguments")
                                    
                                    arguments = cleaned_args

                                # Validate browser_wait_for arguments to prevent circuit breaker trips
                                if "browser_wait_for" in tool_name:
                                    if not (arguments.get("time") or arguments.get("text") or arguments.get("textGone")):
                                        return (
                                            f"Missing required arguments for {tool_name}. "
                                            f"You MUST provide at least one of: 'time' (milliseconds), 'text' (wait for text to appear), or 'textGone' (wait for text to disappear). "
                                            f"Example: {{'text': 'Submit'}} or {{'time': 5000}}"
                                        )

                                # Validate required fields before calling MCP server to avoid -32602 errors
                                required_fields = schema.get("required", []) if isinstance(schema, dict) else []
                                properties = schema.get("properties", {}) if isinstance(schema, dict) else {}
                                missing_fields = []
                                for field_name in required_fields:
                                    if self._is_missing_value(arguments.get(field_name)):
                                        missing_fields.append(field_name)
                                if missing_fields:
                                    required_descriptions = []
                                    for missing in missing_fields:
                                        prop_info = properties.get(missing, {}) if isinstance(properties, dict) else {}
                                        prop_desc = prop_info.get("description", "")
                                        required_descriptions.append(f"- {missing}: {prop_desc or 'Required field'}")
                                    human_error = (
                                        f"Missing required field(s) for {tool_name}: {', '.join(missing_fields)}."
                                    )
                                    if required_descriptions:
                                        human_error += "\nRequired fields:\n" + "\n".join(required_descriptions)
                                    return human_error

                                # Auto-safeguard Puppeteer evaluate scripts to avoid null errors
                                if tool_name == "puppeteer_evaluate" and isinstance(arguments.get("script"), str):
                                    original_script = arguments["script"]
                                    safe_script = self._safeguard_puppeteer_script(original_script)
                                    if safe_script != original_script:
                                        logger.debug("Applied optional chaining safeguards to puppeteer_evaluate script")
                                    arguments["script"] = safe_script
                                
                                # Auto-map 'script' to 'function' for Playwright evaluate
                                if tool_name == "browser_evaluate" and "script" in arguments and "function" not in arguments:
                                    logger.info("Mapping 'script' argument to 'function' for browser_evaluate")
                                    arguments["function"] = arguments.pop("script")

                                try:
                                    result = await fastmcp_manager.call_tool(server_id, tool_name, arguments)
                                    logger.debug(
                                        "MCP tool %s on %s returned: %s",
                                        tool_name,
                                        server_id,
                                        result,
                                    )
                                    return str(result)
                                except Exception as call_error:
                                    error_msg = str(call_error)
                                    logger.error(f"Error calling MCP tool {tool_name} on server {server_id}: {call_error}")
                                
                                # Check for circuit breaker error
                                if "Circuit breaker open" in error_msg:
                                    return (
                                        f"Tool {tool_name} has failed too many times and is temporarily disabled. "
                                        f"The tool or API may be experiencing issues. Please try a different approach or tool, "
                                        f"or wait a few minutes before trying again."
                                    )
                                
                                # Check for rate limit errors
                                if "429" in error_msg or "Too Many Requests" in error_msg or "rate limit" in error_msg.lower():
                                    return (
                                        f"Rate limit reached for {tool_name}. The API is temporarily blocking requests. "
                                        f"This usually happens when making too many requests in a short time. "
                                        f"Please wait a moment or try a different tool."
                                    )
                                
                                # Check for jq parsing errors (common in CoinGecko and similar tools)
                                if "jq:" in error_msg or "jq error" in error_msg.lower():
                                    if "Cannot index" in error_msg:
                                        return (
                                            f"Data format error in {tool_name}: The API returned data in a different format than expected. "
                                            f"The tool script tried to access a field that doesn't exist. "
                                            f"This is likely a temporary issue with the external API. Try again later or use a different tool."
                                        )
                                    else:
                                        return (
                                            f"Data parsing error in {tool_name}: {error_msg}. "
                                            f"The tool couldn't process the API response correctly. This is usually a temporary issue. "
                                            f"Try again later or use a different tool."
                                        )
                                
                                # Check for timeout errors
                                if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                                    return (
                                        f"Timeout error for {tool_name}: The tool took too long to respond. "
                                        f"The external API may be slow or overloaded. Try again or use a different tool."
                                    )
                                
                                # Provide specific guidance for common JavaScript errors (Puppeteer)
                                if "puppeteer_evaluate" in tool_name:
                                    if "Cannot convert undefined or null" in error_msg:
                                        return (
                                            f"JavaScript error: The element you're trying to access doesn't exist or is null. "
                                            f"Use optional chaining (?.) and provide fallback values. "
                                            f"Example: document.querySelector('selector')?.textContent || 'Not found'"
                                        )
                                    elif "Illegal return statement" in error_msg:
                                        return (
                                            f"JavaScript syntax error: Do NOT use 'return' statements in evaluate. "
                                            f"Just write the expression directly. The result is automatically returned. "
                                            f"Example: document.querySelector('h1').textContent (not 'return document...')"
                                        )
                                    elif "has already been declared" in error_msg:
                                        return (
                                            f"JavaScript error: Variable redeclaration. Do NOT declare variables with const/let/var. "
                                            f"Use inline expressions or arrow functions instead. "
                                            f"Example: Array.from(document.querySelectorAll('a')).map(el => el.href)"
                                        )
                                    elif "SyntaxError" in error_msg or "Unexpected token" in error_msg:
                                        return (
                                            f"JavaScript syntax error: {error_msg}. "
                                            f"Write a single valid JavaScript expression without semicolons or statements. "
                                            f"Use arrow functions for complex logic: () => document.body.textContent"
                                        )
                                

                                

                                
                                # Handle "No open pages" error specifically
                                if "No open pages" in error_msg:
                                    return (
                                        f"Error: No open pages available. The browser session may have been reset. "
                                        f"Please call 'browser_navigate' again to reload the page, then retry this tool."
                                    )
                                
                                return (
                                    f"Tool execution error for {tool_name}: {error_msg}. "
                                    f"Please review the error and adjust your approach."
                                )
                            return _run_mcp_tool
                        
                        # Create the runner function with captured values
                        run_mcp_tool = make_mcp_tool_runner(server.server_id, tool_name, input_schema)

                        tool_properties = input_schema.get("properties") if isinstance(input_schema, dict) else None
                        required_props = input_schema.get("required", []) if isinstance(input_schema, dict) else []

                        if tool_properties:
                            schema_fields = {}
                            for prop_name, prop_schema in tool_properties.items():
                                is_required = prop_name in required_props
                                description = prop_schema.get("description", "")
                                python_type = self._json_schema_to_python_type(prop_schema)
                                
                                # For optional fields, use Optional[Type] and default=None
                                # This allows the LLM to omit fields or pass None/null
                                if is_required:
                                    default = ...
                                else:
                                    # Make it Optional
                                    python_type = Optional[python_type]
                                    default = prop_schema.get("default", None)
                                
                                schema_fields[prop_name] = (python_type, Field(default=default, description=description))

                            schema_model_name = f"{server.name}_{tool_name}_Schema".replace(" ", "_")
                            ToolArgsModel = create_model(schema_model_name, **schema_fields)  # type: ignore

                            @tool(args_schema=ToolArgsModel)
                            async def mcp_tool_wrapper(**kwargs):
                                """MCP Tool call. Provide arguments matching schema."""
                                return await run_mcp_tool(kwargs)
                        else:
                            @tool
                            async def mcp_tool_wrapper(payload: Optional[Dict[str, Any]] = None, **kwargs) -> str:
                                """MCP Tool call. Provide arguments as JSON object matching schema. Accepts either 'payload' or direct named parameters."""
                                return await run_mcp_tool(payload, extra_kwargs=kwargs)

                        # Set tool metadata (sanitize to satisfy provider requirements)
                        raw_tool_identifier = f"{server.name}_{tool_name}"
                        sanitized_tool_name = self._sanitize_tool_name(raw_tool_identifier, existing_tool_names)
                        if sanitized_tool_name != raw_tool_identifier:
                            logger.info(
                                "Sanitized MCP tool name from '%s' to '%s' to satisfy provider constraints",
                                raw_tool_identifier,
                                sanitized_tool_name,
                            )

                        mcp_tool_wrapper.name = sanitized_tool_name
                        description = tool_info.get('description', 'MCP tool')
                        
                        # Add enhanced guidance for Puppeteer/Playwright tools
                        if "puppeteer" in server.name.lower() or "playwright" in server.name.lower():
                            if tool_name == "puppeteer_evaluate" or tool_name == "browser_evaluate":
                                description += (
                                    "\n\n**IMPORTANT JavaScript Guidelines:**\n"
                                    "- Write a SINGLE JavaScript expression or statement\n"
                                    "- Do NOT use 'return' statements (the result is auto-returned)\n"
                                    "- Do NOT declare variables with 'const', 'let', or 'var'\n"
                                    "- Use arrow functions: () => expression\n"
                                    "- For element access: document.querySelector('selector')?.textContent\n"
                                    "- For arrays: Array.from(document.querySelectorAll('selector')).map(el => el.textContent)\n"
                                    "- Example: document.querySelector('h1')?.textContent || 'Not found'\n"
                                    "\n**WARNING**: If this tool fails, DO NOT retry with the same script. "
                                    "Use alternative tools like puppeteer_click, puppeteer_screenshot, or puppeteer_navigate instead.\n"
                                )
                                if tool_name == "browser_evaluate":
                                    description += (
                                        "\n**NOTE**: This tool expects a 'function' argument (e.g. '() => document.title'). "
                                        "If you have a 'script' or 'expression', wrap it in an arrow function."
                                    )
                            else:
                                # Add general Puppeteer tool guidance
                                description += (
                                    "\n\n**Puppeteer Tool - Reliable browser automation**\n"
                                    "This tool works well for browser interactions. Use it confidently!\n"
                                    "Other available Puppeteer tools: navigate, click, screenshot, evaluate, etc.\n"
                                    "Note: If this tool encounters an error, try a different Puppeteer tool.\n"
                                )
                        elif tool_name == "browser_navigate":
                            description += (
                                "\n\n**Navigation Tool:**\n"
                                "- Use this tool FIRST to open a website.\n"
                                "- Required argument: 'url' (e.g. 'https://google.com')\n"
                                "- You MUST navigate to a page before using other browser tools."
                            )
                        elif tool_name == "browser_wait_for":
                            description += (
                                "\n\n**Wait Tool Guidelines:**\n"
                                "- You MUST provide at least one of: 'time', 'text', or 'textGone'\n"
                                "- 'time': Wait for X milliseconds (e.g. 5000)\n"
                                "- 'text': Wait for text to appear on screen\n"
                                "- 'textGone': Wait for text to disappear\n"
                            )
                        elif tool_name == "ask_question":
                            description += (
                                "\n\n**DeepWiki Tool Guidelines:**\n"
                                "- Required field: question (string)\n"
                                "- Provide the exact question you want answered\n"
                                "- Example: 'What is LangGraph?'\n"
                            )
                        
                        description += f"\nOriginal MCP tool identifier: {raw_tool_identifier}"
                        description += f"\nInput schema: {schema_description}"
                        mcp_tool_wrapper.description = description

                        mcp_tools.append(mcp_tool_wrapper)
                        
                    logger.info(f"Loaded {len(tools)} tools from MCP server {server.name}")
                    
                except Exception as e:
                    logger.error(f"Error loading tools from MCP server {server.name}: {e}")
                    continue
            
            # Check if user has manually selected tools (if so, respect their selection)
            has_selected_tools = any(
                assoc.selected_tools is not None 
                for assoc in associations
            )
            
            # Limit total number of MCP tools to prevent token overflow
            # Only apply this limit if user hasn't manually selected specific tools
            # Large numbers of tools cause 413 Payload Too Large errors with LLMs
            max_tools = settings.MAX_MCP_TOOLS_PER_AGENT
            
            if not has_selected_tools and len(mcp_tools) > max_tools:
                trimmed_tool_names = [t.name for t in mcp_tools[max_tools:]]
                logger.warning(
                    f"⚠️  Agent {agent_id} has {len(mcp_tools)} MCP tools, which exceeds the limit of {max_tools}. "
                    f"Trimming to first {max_tools} tools to prevent token overflow. "
                    f"Trimmed tools: {trimmed_tool_names}. "
                    f"To avoid this, select specific tools for each MCP server, or set MAX_MCP_TOOLS_PER_AGENT in .env file."
                )
                print(
                    f"⚠️  WARNING: Too many MCP tools ({len(mcp_tools)})! Limiting to {max_tools} tools to prevent API errors. "
                    f"Trimmed tools: {', '.join(trimmed_tool_names[:5])}{'...' if len(trimmed_tool_names) > 5 else ''}. "
                    f"Use the tool selection feature to choose specific tools instead of loading all tools from MCP servers."
                )
                # Keep only the first N tools
                mcp_tools = mcp_tools[:max_tools]
            elif has_selected_tools and len(mcp_tools) > max_tools:
                logger.warning(
                    f"⚠️  Agent {agent_id} has {len(mcp_tools)} selected tools, which exceeds the recommended limit of {max_tools}. "
                    f"This may cause token overflow errors. Consider selecting fewer tools."
                )
            
            logger.info(f"Total MCP tools loaded for agent {agent_id}: {len(mcp_tools)}")
            return mcp_tools
            
        except Exception as e:
            logger.error(f"Error getting MCP tools for agent {agent_id}: {e}")
            return []
    
    async def update_agent(self, agent_id: str, agent_data: AgentCreate, tenant_id: Optional[str] = None) -> Optional[AgentInDB]:
        """Update an existing agent"""
        query = self.db.query(AgentModel).filter(AgentModel.agent_id == agent_id)
        
        # Apply tenant filter if provided
        if tenant_id:
            query = query.filter(AgentModel.tenant_id == tenant_id)
        
        db_agent = query.first()
        if not db_agent:
            return None
        
        # Encrypt the API key if provided
        if agent_data.api_key:
            db_agent.api_key_encrypted = self._encrypt_api_key(agent_data.api_key)
        
        # Update fields
        db_agent.name = agent_data.name
        db_agent.agent_type = agent_data.agent_type
        db_agent.llm_provider = agent_data.llm_provider
        db_agent.llm_model = agent_data.llm_model
        db_agent.temperature = agent_data.temperature
        db_agent.system_prompt = agent_data.system_prompt
        db_agent.tools = agent_data.tools
        db_agent.tool_configs = agent_data.tool_configs
        db_agent.max_iterations = agent_data.max_iterations
        db_agent.memory_type = agent_data.memory_type
        db_agent.streaming_enabled = agent_data.streaming_enabled
        db_agent.human_in_loop = agent_data.human_in_loop
        db_agent.recursion_limit = agent_data.recursion_limit
        db_agent.pii_config = agent_data.pii_config
        db_agent.version = (db_agent.version or 1) + 1  # Increment version
        
        self.db.commit()
        self.db.refresh(db_agent)
        print(f"Agent updated in database: {db_agent.agent_id}")
        
        # Update MCP server associations with tool selection
        # Support both old format (mcp_servers) and new format (mcp_server_configs)
        if agent_data.mcp_server_configs is not None:
            # New format with tool selection
            # Remove existing associations
            self.db.query(AgentMCPServer).filter(
                AgentMCPServer.agent_id == agent_id
            ).delete()
            
            # Add new associations with tool selection
            for server_config in agent_data.mcp_server_configs:
                association = AgentMCPServer(
                    agent_id=agent_id,
                    server_id=server_config.server_id,
                    enabled="true",
                    selected_tools=server_config.selected_tools
                )
                self.db.add(association)
            self.db.commit()
            print(f"Updated MCP server associations with tool selection: {len(agent_data.mcp_server_configs)} servers")
        elif agent_data.mcp_servers is not None:
            # Old format for backward compatibility
            # Remove existing associations
            self.db.query(AgentMCPServer).filter(
                AgentMCPServer.agent_id == agent_id
            ).delete()
            
            # Add new associations (all tools)
            for server_id in agent_data.mcp_servers:
                association = AgentMCPServer(
                    agent_id=agent_id,
                    server_id=server_id,
                    enabled="true",
                    selected_tools=None  # None = all tools
                )
                self.db.add(association)
            self.db.commit()
            print(f"Updated MCP server associations: {len(agent_data.mcp_servers)} servers")
        
        return AgentInDB.model_validate(db_agent)

    async def chat_with_agent(self, agent_id: str, message: str, thread_id: Optional[str] = None) -> str:
        """Chat with an agent"""
        try:
            # Use thread_id if provided (session-based), otherwise use agent_id (persistent)
            session_id = thread_id if thread_id else f"agent_{agent_id}"
            
            # Get agent config to check for PII filtering
            agent = await self.get_agent(agent_id)
            if not agent:
                raise ValueError("Agent not found")
            
            # Apply PII filtering to input if configured
            filtered_message = message
            if agent.pii_config:
                pii_middleware = create_pii_middleware_from_config(agent.pii_config)
                if pii_middleware:
                    filtered_message = pii_middleware.process_message(message, message_type="input")
            
            # Execute the agent and get response
            response = await self.execute_agent(agent_id, filtered_message, session_id=session_id)
            
            # Apply PII filtering to output if configured
            if agent.pii_config:
                pii_middleware = create_pii_middleware_from_config(agent.pii_config)
                if pii_middleware:
                    response = pii_middleware.process_message(response, message_type="output")
            
            # Store the interaction in mem0 memory if enabled
            # Store both user and assistant messages to preserve conversation context
            if self.memory_service.is_enabled():
                try:
                    # Get agent to access its LLM configuration
                    agent = await self.get_agent(agent_id)
                    if agent:
                        # Store both messages for full conversational context
                        # Mem0 is configured to extract user-specific facts
                        interaction = [
                            {"role": "user", "content": message},
                            {"role": "assistant", "content": response}
                        ]
                        self.memory_service.add_memory(
                            interaction, 
                            user_id=session_id, 
                            agent_id=agent_id,
                            llm_provider="groq",
                            llm_model="llama-3.1-8b-instant"
                        )
                except Exception as mem_error:
                    print(f"Error storing memory: {mem_error}")
            
            return response
        except Exception as e:
            # Log the error for debugging
            error_msg = str(e)
            
            # Clean HTML error responses
            if "<!DOCTYPE html>" in error_msg or "<html" in error_msg:
                if "500" in error_msg and "Internal server error" in error_msg:
                    error_msg = "The AI provider is experiencing server issues. Please try again in a few moments."
                elif "502" in error_msg or "Bad Gateway" in error_msg:
                    error_msg = "The AI provider is temporarily unavailable. Please try again."
                elif "503" in error_msg or "Service Unavailable" in error_msg:
                    error_msg = "The AI provider service is temporarily unavailable. Please try again."
                elif "504" in error_msg or "Gateway Timeout" in error_msg:
                    error_msg = "The AI provider request timed out. Please try again."
                else:
                    error_msg = "The AI provider returned an error. Please try again."
            
            print(f"Error chatting with agent {agent_id}: {error_msg}")
            
            # Return a more user-friendly error message
            # Check for decommissioned model errors (Groq)
            if "model_decommissioned" in error_msg or "has been decommissioned" in error_msg:
                # Extract model name if possible
                import re
                model_match = re.search(r'model `([^`]+)`', error_msg)
                model_name = model_match.group(1) if model_match else "the selected model"
                
                return (
                    f"⚠️ Model Decommissioned: {model_name} is no longer supported by Groq.\n\n"
                    f"📋 Recommended Actions:\n"
                    f"1. Edit this agent and change the model to 'llama-3.3-70b-versatile' (recommended) or 'llama-3.1-8b-instant'\n"
                    f"2. Save the agent with the new model\n"
                    f"3. Try your request again\n\n"
                    f"💡 Groq regularly updates their model lineup. See https://console.groq.com/docs/models for currently supported models."
                )
            # Check for specific API key errors from LLM providers
            elif (("API key" in error_msg or "401" in error_msg) and 
                ("OpenAI" in error_msg or "Anthropic" in error_msg or "Groq" in error_msg or "api_key" in error_msg.lower())):
                return "Invalid API key. Please check your API key configuration."
            elif "403" in error_msg and ("OpenAI" in error_msg or "Anthropic" in error_msg or "Groq" in error_msg):
                return "Access forbidden. Please check your API key permissions."
            elif "429" in error_msg and ("OpenAI" in error_msg or "Anthropic" in error_msg or "Groq" in error_msg):
                return "Rate limit exceeded. Please try again later."
            else:
                return f"Error communicating with the agent: {error_msg}"
    
    async def execute_agent(self, agent_id: str, input_text: str, session_id: Optional[str] = None, recursion_limit: int = 50) -> str:
        """Execute an agent with automatic rate limit handling"""
        agent = await self.get_agent(agent_id)
        if not agent:
            raise ValueError("Agent not found")
        
        # Check if rate limit fallback is enabled (can be disabled via env var)
        enable_rate_limit_fallback = os.getenv("ENABLE_RATE_LIMIT_FALLBACK", "true").lower() == "true"
        
        # Track original configuration for fallback
        # IMPORTANT: Use separate variables instead of modifying agent object
        current_provider = agent.llm_provider
        current_model = agent.llm_model
        original_provider = agent.llm_provider
        original_model = agent.llm_model
        # Increase max retries to allow trying all Groq models + alternative providers
        # We now have 17 Groq models, so allow up to 25 attempts total
        max_retries = 25 if enable_rate_limit_fallback else 1
        retry_count = 0
        last_provider_tried = None
        
        # Apply PII filtering to input if configured
        filtered_input = input_text
        if agent.pii_config:
            pii_middleware = create_pii_middleware_from_config(agent.pii_config)
            if pii_middleware:
                filtered_input = pii_middleware.process_message(input_text, message_type="input")
        
        # Retry loop with fallback support
        while retry_count < max_retries:
            try:
                return await self._execute_agent_with_fallback(
                    agent=agent,
                    filtered_input=filtered_input,
                    session_id=session_id,
                    user_id=session_id if session_id else f"agent_{agent_id}",
                    override_provider=current_provider,
                    override_model=current_model,
                    recursion_limit=recursion_limit
                )
            except Exception as e:
                error_msg = str(e)
                
                # IMPORTANT: Only treat as rate limit if it's actually a rate limit error
                # Exclude tool errors, validation errors, and decommissioned model errors
                is_tool_error = "tool" in error_msg.lower() and ("validation" in error_msg.lower() or "execution" in error_msg.lower())
                is_decommissioned_error = "decommissioned" in error_msg.lower() or "model_decommissioned" in error_msg.lower()
                
                # Check if it's a rate limit error (but not a tool or model error) and fallback is enabled
                if enable_rate_limit_fallback and RateLimitHandler.is_rate_limit_error(error_msg) and not is_tool_error and not is_decommissioned_error:
                    retry_count += 1
                    provider = RateLimitHandler.extract_provider(error_msg) or current_provider
                    
                    logger.warning(f"⚠️ Rate limit hit on {provider}/{current_model} (attempt {retry_count}/{max_retries})")
                    print(f"⚠️ Rate limit hit on {provider}/{current_model} (attempt {retry_count}/{max_retries})")
                    
                    # Extract and cache the rate limit with wait time
                    wait_time = RateLimitHandler.extract_wait_time(error_msg)
                    RateLimitHandler.cache_rate_limit(
                        provider,
                        current_model,
                        wait_time if wait_time else 300  # Default 5 minutes
                    )
                    
                    if retry_count >= max_retries:
                        # Check how many models are still available
                        available_count = len(RateLimitHandler.get_all_available_models(provider))
                        raise ValueError(
                            f"❌ Exhausted all {max_retries} retry attempts. "
                            f"Rate limits on multiple models. {available_count} models may still be available. "
                            f"Please try again later or use a different API key."
                        )
                    
                    # Strategy 1: Try next model in SAME provider first
                    fallback_model = RateLimitHandler.get_fallback_model(provider, current_model)
                    
                    if fallback_model:
                        # Found available model in same provider
                        # DO NOT modify agent object - use local variables instead
                        current_model = fallback_model
                        logger.info(f"🔄 Attempt {retry_count}: Switching to {provider}/{fallback_model}")
                        print(f"🔄 Attempt {retry_count}: Switching to {provider}/{fallback_model}")
                        continue
                    
                    # Strategy 2: All models in current provider are rate-limited, try alternative provider
                    logger.warning(f"⚠️ All models in {provider} appear rate-limited or exhausted")
                    print(f"⚠️ All models in {provider} appear rate-limited or exhausted")
                    
                    alt_provider = RateLimitHandler.get_alternative_provider(provider)
                    if alt_provider:
                        # Get first available model from alternative provider
                        alt_models = RateLimitHandler.get_all_available_models(alt_provider)
                        if alt_models:
                            # DO NOT modify agent object - use local variables instead
                            current_provider = alt_provider
                            current_model = alt_models[0]
                            logger.info(f"🔄 Attempt {retry_count}: Switching provider to {alt_provider}/{alt_models[0]}")
                            print(f"🔄 Attempt {retry_count}: Switching provider to {alt_provider}/{alt_models[0]}")
                            last_provider_tried = alt_provider
                            continue
                    
                    # Strategy 3: No fallbacks available
                    logger.error("❌ No more fallback models or providers available")
                    print("❌ No more fallback models or providers available")
                    
                    # Build helpful error message
                    groq_available = len(RateLimitHandler.get_all_available_models("groq"))
                    openai_available = len(RateLimitHandler.get_all_available_models("openai"))
                    anthropic_available = len(RateLimitHandler.get_all_available_models("anthropic"))
                    
                    error_parts = [
                        f"⚠️ Rate limit reached on {provider}/{current_model}.",
                    ]
                    if wait_time:
                        if wait_time < 60:
                            wait_str = f"{wait_time} seconds"
                        elif wait_time < 3600:
                            wait_str = f"{wait_time // 60} minutes"
                        else:
                            wait_str = f"{wait_time // 3600} hours"
                        error_parts.append(f"Provider requests waiting {wait_str}.")
                    
                    error_parts.append(
                        f"\n\nAvailable models status:"
                        f"\n  • Groq: {groq_available} models available"
                        f"\n  • OpenAI: {openai_available} models available"
                        f"\n  • Anthropic: {anthropic_available} models available"
                    )
                    
                    if groq_available + openai_available + anthropic_available == 0:
                        error_parts.append(
                            "\n\n💡 All known models are currently rate-limited. "
                            "Please try again later or add additional API keys."
                        )
                    
                    raise ValueError(" ".join(error_parts))
                else:
                    # Not a rate limit error, raise immediately
                    raise
        
        # If we exhausted all retries
        raise ValueError(f"Failed to execute agent after {max_retries} attempts with different models/providers.")
    
    async def _execute_agent_with_fallback(
        self, 
        agent: AgentModel,
        filtered_input: str,
        session_id: Optional[str],
        user_id: str,
        override_provider: Optional[str] = None,
        override_model: Optional[str] = None,
        recursion_limit: int = 50
    ) -> str:
        """Execute agent with current configuration (helper method for retry logic)"""
        try:
            # Use override values if provided, otherwise use agent's configured values
            active_provider = override_provider or agent.llm_provider
            active_model = override_model or agent.llm_model
            
            # Retrieve relevant memories from mem0 if enabled
            memory_context = ""
            if self.memory_service.is_enabled():
                try:
                    memories = self.memory_service.search_memory(
                        query=filtered_input,
                        user_id=user_id,
                        agent_id=agent.agent_id,
                        top_k=5,  # Increased from 3 to 5 for more context
                        llm_provider="groq",
                        llm_model="llama-3.1-8b-instant"
                    )
                    
                    # Build memory context string
                    if memories:
                        memory_context = "\nRelevant information from previous conversations:\n"
                        for i, memory in enumerate(memories, 1):
                            memory_content = memory.get('memory', '') if isinstance(memory, dict) else str(memory)
                            memory_context += f"{i}. {memory_content}\n"
                        # Note: Memory context is from previous trusted conversations and should not be PII filtered
                except Exception as mem_error:
                    print(f"Error retrieving memory context: {mem_error}")
            
            # Retrieve knowledge base context with timeout
            knowledge_context = ""
            try:
                import asyncio
                from services.knowledge_base_service import KnowledgeBaseService
                kb_service = KnowledgeBaseService(self.db)
                # Add 30 second timeout for KB queries to allow for embedding generation
                knowledge_context = await asyncio.wait_for(
                    kb_service.query_agent_knowledge(agent.agent_id, filtered_input, top_k=5),
                    timeout=30.0
                )
                # Note: Knowledge base content is trusted and should not be PII filtered
                if knowledge_context:
                    print(f"Retrieved KB context for agent {agent.agent_id}: {len(knowledge_context)} chars")
            except asyncio.TimeoutError:
                print(f"Knowledge base query timed out for agent {agent.agent_id}")
            except Exception as kb_error:
                print(f"Error retrieving knowledge base context: {kb_error}")
                import traceback
                traceback.print_exc()
            
            # Create the LangGraph agent based on configuration with memory context
            # Pass active provider/model to override agent's stored values during retries
            langgraph_agent, available_tools = await self._create_langgraph_agent(
                agent, 
                memory_context,
                knowledge_context=knowledge_context,
                override_provider=active_provider,
                override_model=active_model
            )
            
            # Prepare messages with context from mem0 memory if enabled
            messages = [HumanMessage(content=filtered_input)]
            
            # Execute the agent with the appropriate input format based on agent type

            # Add timeout to prevent hanging on slow LLM responses
            import asyncio
            try:
                # Get recursion limit from argument (precedence) or agent config, default to 50
                # For MCP tool agents (like Puppeteer), higher limits are often needed
                effective_recursion_limit = recursion_limit
                if effective_recursion_limit == 50 and getattr(agent, "recursion_limit", None):
                     # If default was passed but agent has specific config, use that? 
                     # Actually, let's just trust the passed value if it's explicit, but since 50 is default...
                     # Let's just say: use max of passed and configured? Or just use passed.
                     # For this specific fix, I want to ensure the 100 passed from script is used.
                     pass
                
                # If the argument is the default 50, but agent has a higher stored limit, we might want to respect that?
                # But for now, let's just use the argument value as it's what we want to control.
                
                config = {"recursion_limit": recursion_limit}
                logger.info(f"Executing agent {agent.agent_id} with recursion_limit={recursion_limit}")

                if agent.agent_type == "react":
                    # ReAct agents expect messages format
                    # Increase timeout to 300s for agents with knowledge bases and MCP tools
                    timeout_duration = 300.0
                    if hasattr(langgraph_agent, "ainvoke"):
                        response = await asyncio.wait_for(
                            langgraph_agent.ainvoke({"messages": messages}, config=config),
                            timeout=timeout_duration
                        )
                    else:
                        response = await asyncio.wait_for(
                            asyncio.to_thread(langgraph_agent.invoke, {"messages": messages}, config=config),
                            timeout=timeout_duration
                        )
                else:
                    # Other agents (plan-execute, reflection, custom) expect input format
                    # For these, we'll add the knowledge base and memory context to the input
                    # KB provides static info; tools provide real-time/external capabilities
                    enhanced_input = filtered_input
                    if knowledge_context or memory_context:
                        context_parts = []
                        
                        # Add KB context with balanced guidance
                        if knowledge_context:
                            kb_section = "## Knowledge Base Information\n"
                            kb_section += knowledge_context
                            kb_section += "\n\n**Note**: This knowledge base contains static domain information. Your tools are available for real-time data and external actions."
                            context_parts.append(kb_section)
                        
                        # Add memory context second
                        if memory_context:
                            context_parts.append("## Previous Conversation Context\n" + memory_context)
                        
                        enhanced_input = f"{filtered_input}\n\n" + "\n\n".join(context_parts)
                    
                    # Increase timeout to 180s for agents with knowledge bases
                    timeout_duration = 180.0 if (knowledge_context or memory_context) else 90.0
                    if hasattr(langgraph_agent, "ainvoke"):
                        response = await asyncio.wait_for(
                            langgraph_agent.ainvoke({"input": enhanced_input}, config=config),
                            timeout=timeout_duration
                        )
                    else:
                        response = await asyncio.wait_for(
                            asyncio.to_thread(langgraph_agent.invoke, {"input": enhanced_input}, config=config),
                            timeout=timeout_duration
                        )
            except asyncio.TimeoutError:
                raise ValueError("Agent response timed out. The LLM provider may be slow or unreachable. Please try again.")
            except Exception as e:
                # Handle API errors more gracefully
                error_msg = str(e)
                
                # Clean HTML error responses
                if "<!DOCTYPE html>" in error_msg or "<html" in error_msg:
                    # Extract error code if present
                    if "500" in error_msg and "Internal server error" in error_msg:
                        error_msg = "The AI provider (Groq) is experiencing server issues. Please try again in a few moments."
                    elif "502" in error_msg or "Bad Gateway" in error_msg:
                        error_msg = "The AI provider is temporarily unavailable. Please try again."
                    elif "503" in error_msg or "Service Unavailable" in error_msg:
                        error_msg = "The AI provider service is temporarily unavailable. Please try again."
                    elif "504" in error_msg or "Gateway Timeout" in error_msg:
                        error_msg = "The AI provider request timed out. Please try again."
                    else:
                        error_msg = "The AI provider returned an error. Please try again."
                
                print(f"Error executing agent {agent.agent_id}: {error_msg}")
                
                # Check for decommissioned model errors (Groq)
                if "model_decommissioned" in error_msg or "has been decommissioned" in error_msg:
                    import re
                    model_match = re.search(r'model `([^`]+)`', error_msg)
                    model_name = model_match.group(1) if model_match else "the selected model"
                    raise ValueError(
                        f"Model Decommissioned: {model_name} is no longer supported by Groq. "
                        f"Please edit the agent and select a currently supported model like 'llama-3.3-70b-versatile' or 'llama-3.1-8b-instant'. "
                        f"See https://console.groq.com/docs/models for the current model list."
                    )
                # Check for specific API key errors from LLM providers
                elif (("API key" in error_msg or "401" in error_msg) and 
                    ("OpenAI" in error_msg or "Anthropic" in error_msg or "Groq" in error_msg or "api_key" in error_msg.lower())):
                    raise ValueError("Invalid API key. Please check your API key configuration.")
                elif "403" in error_msg and ("OpenAI" in error_msg or "Anthropic" in error_msg or "Groq" in error_msg):
                    raise ValueError("Access forbidden. Please check your API key permissions.")
                elif "tool_use_failed" in error_msg or "Failed to call a function" in error_msg:
                    # Handle tool execution failures more gracefully
                    raise ValueError("Tool execution failed. This may be due to rate limiting, network issues, or missing API keys. Please try again or check your tool configuration.")
                elif "<!DOCTYPE html>" in str(e) or "Internal server error" in error_msg or "server issues" in error_msg:
                    # Provider server error - provide clean message
                    raise ValueError(error_msg)
                else:
                    # For other errors (including 429 rate limits), re-raise to be caught by outer handler
                    raise e
            
            # Extract the final response
            # Handle different response formats
            if isinstance(response, dict):
                logger.info(f"DEBUG: Agent response keys: {response.keys()}")
                if "messages" in response:
                    msgs = response["messages"]
                    logger.info(f"DEBUG: Agent returned {len(msgs)} messages")
                    for i, m in enumerate(msgs):
                        content_preview = str(m.content)[:200] if hasattr(m, 'content') else "No content"
                        logger.info(f"DEBUG: Msg {i} type={type(m).__name__}: {content_preview}")

                if "messages" in response and len(response["messages"]) > 0:
                    # Standard format with messages key
                    final_message = response["messages"][-1]
            # Return the content if available, otherwise convert to string
            try:
                response_text = None
                if hasattr(final_message, 'content') and final_message.content is not None:
                    response_text = str(final_message.content)
                elif isinstance(final_message, dict):
                    # If it's a dict, try to get content or convert to string
                    response_text = str(final_message.get('content', str(final_message)))
                else:
                    response_text = str(final_message)
                
                # Track cost (estimate based on input/output sizes)
                # Rough estimation: ~4 characters per token
                try:
                    input_tokens = len(filtered_input) // 4
                    output_tokens = len(response_text) // 4
                    
                    # Track API call
                    await self.cost_service.track_api_call(
                        provider=agent.llm_provider,
                        model=agent.llm_model,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        agent_id=agent.agent_id,
                        workflow_id=None,  # Will be set if called from workflow
                        execution_id=None,  # Will be set if called from workflow
                        call_type="chat",
                        metadata={
                            "agent_type": agent.agent_type,
                            "estimated": True
                        }
                    )
                except Exception as cost_error:
                    logger.warning(f"Error tracking cost: {str(cost_error)}")
                
                return response_text
            except Exception as e:
                # Fallback to string representation
                return str(final_message)
        except Exception as e:
            # Handle any unexpected errors in the execution method
            error_msg = str(e)
            
            # Clean HTML error responses
            if "<!DOCTYPE html>" in error_msg or "<html" in error_msg:
                if "500" in error_msg and "Internal server error" in error_msg:
                    error_msg = "The AI provider is experiencing server issues. Please try again in a few moments."
                elif "502" in error_msg or "Bad Gateway" in error_msg:
                    error_msg = "The AI provider is temporarily unavailable. Please try again."
                elif "503" in error_msg or "Service Unavailable" in error_msg:
                    error_msg = "The AI provider service is temporarily unavailable. Please try again."
                elif "504" in error_msg or "Gateway Timeout" in error_msg:
                    error_msg = "The AI provider request timed out. Please try again."
                else:
                    error_msg = "The AI provider returned an error. Please try again."
            
            print(f"Unexpected error executing agent {agent.agent_id}: {error_msg}")
            import traceback
            traceback.print_exc()
            raise ValueError(f"An unexpected error occurred while processing your request: {error_msg}")
    
    async def stream_agent(self, websocket, agent_id: str, message: Optional[str] = None, session_id: Optional[str] = None):
        """Stream agent responses via WebSocket using AG-UI Protocol"""
        from services.ag_ui_protocol import AGUIProtocol, AGUIEventType
        import uuid
        
        agent = await self.get_agent(agent_id)
        if not agent:
            error_msg = AGUIProtocol.create_error(
                error="Agent not found",
                error_code="AGENT_NOT_FOUND",
                session_id=session_id
            )
            await websocket.send_text(error_msg.to_json())
            await websocket.close()
            return
        
        run_id = str(uuid.uuid4())
        session_id = session_id or f"session_{run_id}"
        
        try:
            # Send RUN_STARTED event
            run_started = AGUIProtocol.create_run_started(
                run_id=run_id,
                session_id=session_id,
                metadata={"agent_id": agent_id, "agent_name": agent.name}
            )
            await websocket.send_text(run_started.to_json())
            
            # If message provided, process it
            if message:
                # Send user message
                user_msg = AGUIProtocol.create_text_message(
                    content=message,
                    run_id=run_id,
                    session_id=session_id,
                    role="user"
                )
                await websocket.send_text(user_msg.to_json())
                
                # Execute agent with streaming
                response = await self._execute_agent_with_streaming(
                    agent_id=agent_id,
                    input_text=message,
                    session_id=session_id,
                    websocket=websocket,
                    run_id=run_id
                )
            
            # Send RUN_FINISHED event
            run_finished = AGUIProtocol.create_run_finished(
                run_id=run_id,
                session_id=session_id
            )
            await websocket.send_text(run_finished.to_json())
            
        except Exception as e:
            logger.error(f"Error in stream_agent: {e}")
            error_msg = AGUIProtocol.create_error(
                error=str(e),
                error_code="EXECUTION_ERROR",
                run_id=run_id,
                session_id=session_id
            )
            await websocket.send_text(error_msg.to_json())
        finally:
            await websocket.close()
    
    async def _execute_agent_with_streaming(
        self,
        agent_id: str,
        input_text: str,
        session_id: str,
        websocket,
        run_id: str
    ) -> str:
        """Execute agent with AG-UI Protocol streaming"""
        from services.ag_ui_protocol import AGUIProtocol
        
        agent = await self.get_agent(agent_id)
        if not agent:
            raise ValueError("Agent not found")
        
        # Apply PII filtering if configured
        filtered_input = input_text
        if agent.pii_config:
            pii_middleware = create_pii_middleware_from_config(agent.pii_config)
            if pii_middleware:
                filtered_input = pii_middleware.process_message(input_text, message_type="input")
        
        # Create agent graph
        memory_context = ""
        if self.memory_service.is_enabled():
            try:
                memories = self.memory_service.search_memory(
                    query=filtered_input,
                    user_id=session_id,
                    agent_id=agent_id,
                    top_k=3,
                    llm_provider="groq",
                    llm_model="llama-3.1-8b-instant"
                )
                if memories:
                    memory_context = "\n".join([m.get("memory", "") for m in memories])
            except Exception as e:
                logger.warning(f"Error retrieving memory: {e}")
        
        agent_graph, _ = await self._create_langgraph_agent(agent, memory_context)
        
        # Execute with streaming callback
        accumulated_response = ""
        
        async def stream_callback(chunk: str):
            """Callback for streaming chunks"""
            nonlocal accumulated_response
            accumulated_response += chunk
            
            # Send stream chunk via AG-UI Protocol
            chunk_msg = AGUIProtocol.create_stream_chunk(
                chunk=chunk,
                run_id=run_id,
                session_id=session_id,
                is_final=False
            )
            await websocket.send_text(chunk_msg.to_json())
        
        try:
            # Execute agent (this would need to be adapted for actual streaming)
            # For now, we'll simulate streaming
            response = await self.execute_agent(agent_id, filtered_input, session_id)
            
            # Send response as text message
            text_msg = AGUIProtocol.create_text_message(
                content=response,
                run_id=run_id,
                session_id=session_id,
                role="assistant"
            )
            await websocket.send_text(text_msg.to_json())
            
            # Apply PII filtering to output if configured
            if agent.pii_config:
                pii_middleware = create_pii_middleware_from_config(agent.pii_config)
                if pii_middleware:
                    response = pii_middleware.process_message(response, message_type="output")
            
            # Store in memory if enabled
            if self.memory_service.is_enabled():
                try:
                    interaction = [
                        {"role": "user", "content": input_text},
                        {"role": "assistant", "content": response}
                    ]
                    self.memory_service.add_memory(
                        interaction,
                        user_id=session_id,
                        agent_id=agent_id,
                        llm_provider="groq",
                        llm_model="llama-3.1-8b-instant"
                    )
                except Exception as e:
                    logger.warning(f"Error storing memory: {e}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error executing agent: {e}")
            error_msg = AGUIProtocol.create_error(
                error=str(e),
                error_code="AGENT_EXECUTION_ERROR",
                run_id=run_id,
                session_id=session_id
            )
            await websocket.send_text(error_msg.to_json())
            raise
    
    async def _create_langgraph_agent(
        self, 
        agent_config: AgentInDB, 
        memory_context: str = "",
        knowledge_context: str = "",
        override_provider: Optional[str] = None,
        override_model: Optional[str] = None
    ):
        """Create a LangGraph agent based on the configuration"""
        # Log agent type for debugging MCP tool issues
        logger.info(f"Creating agent {agent_config.agent_id} with type={agent_config.agent_type}")
        
        # Decrypt the user API key if available
        user_api_key = None
        if hasattr(agent_config, 'api_key_encrypted') and agent_config.api_key_encrypted:
            try:
                user_api_key = self._decrypt_api_key(agent_config.api_key_encrypted)
            except Exception as e:
                print(f"Warning: Could not decrypt API key for agent {agent_config.agent_id}: {e}")
        
        # Use override values if provided (for rate limit fallback), otherwise use agent's configured values
        active_provider = override_provider or agent_config.llm_provider
        active_model = override_model or agent_config.llm_model

        # For Groq agents, require a user-supplied API key so we don't fall back to the system key
        if active_provider.lower() == "groq" and not user_api_key:
            raise ValueError("No API key configured for Groq. Please add an API key to this agent.")
        
        # Initialize the LLM based on provider and user API key
        llm = self._initialize_llm(
            active_provider,
            active_model,
            agent_config.temperature,
            user_api_key
        )
        
        # Create the agent graph based on type
        # NOTE: MCP tools are ONLY loaded for agent_type="react"
        if agent_config.agent_type == "react":
            logger.info(f"Agent {agent_config.agent_id} is type='react' - will load MCP tools")
            return await self._create_react_agent(llm, agent_config, memory_context, knowledge_context)
        elif agent_config.agent_type == "plan-execute":
            return self._create_plan_execute_agent(llm, agent_config, memory_context), []
        elif agent_config.agent_type == "reflection":
            return self._create_reflection_agent(llm, agent_config, memory_context), []
        else:  # custom
            return self._create_custom_agent(llm, agent_config, memory_context), []
    
    def _initialize_llm(self, provider: str, model: str, temperature: float, user_api_key: Optional[str] = None):
        """Initialize the LLM based on provider and user API key"""
        # Use LLMService which supports LiteLLM
        use_litellm = os.getenv("USE_LITELLM", "true").lower() == "true"
        
        try:
            return self.llm_service.initialize_llm(
                provider=provider,
                model=model,
                temperature=temperature,
                max_tokens=2048, # Safe default for most models
                user_api_key=user_api_key,
                use_litellm=use_litellm
            )
        except Exception as e:
            logger.warning(f"Error initializing LLM with LLMService: {e}, falling back to direct")
            # Fallback to direct initialization
            return self._initialize_llm_direct(provider, model, temperature, user_api_key)
    
    def _initialize_llm_direct(self, provider: str, model: str, temperature: float, user_api_key: Optional[str] = None):
        """Direct LLM initialization (fallback)"""
        # Use user-provided API key if available, otherwise fall back to system keys
        openai_api_key = user_api_key or settings.OPENAI_API_KEY
        anthropic_api_key = user_api_key or settings.ANTHROPIC_API_KEY
        groq_api_key = user_api_key or settings.GROQ_API_KEY
        
        # Check if API keys are available
        openai_key_available = bool(openai_api_key and openai_api_key.strip())
        anthropic_key_available = bool(anthropic_api_key and anthropic_api_key.strip())
        groq_key_available = bool(groq_api_key and groq_api_key.strip())
        
        if provider == "openai" and openai_key_available:
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=openai_api_key,
                max_tokens=2000  # Increased from 300 to allow tool reasoning and responses
            )
        elif provider == "anthropic" and anthropic_key_available:
            return ChatAnthropic(
                model=model,
                temperature=temperature,
                anthropic_api_key=anthropic_api_key,
                max_tokens=2000  # Increased from 300 to allow tool reasoning and responses
            )
        elif provider == "openrouter" and user_api_key:
            # OpenRouter uses OpenAI-compatible API with custom base_url
            # For tool use, ensure routing to tool-capable providers
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=user_api_key,
                base_url="https://openrouter.ai/api/v1",
                max_tokens=2000,  # Increased from 300 to allow tool reasoning and responses
                default_headers={
                    "HTTP-Referer": "https://execution-plane.local",
                    "X-Title": "Execution Plane Agent"
                },
                model_kwargs={
                    # Prefer providers that support tool use
                    "provider": {
                        "order": [
                            "OpenAI",
                            "Anthropic",
                            "Google",
                            "Cohere",
                            "Fireworks"
                        ],
                        "allow_fallbacks": True
                    }
                }
            )
        elif provider == "groq" and groq_key_available:
            return ChatGroq(
                model=model,
                temperature=temperature,
                groq_api_key=groq_api_key,
                max_tokens=2000  # Increased from 300 to allow tool reasoning and responses
            )
        # Add other providers as needed
        elif openai_key_available:
            # Default to OpenAI if provider not recognized but key is available
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=openai_api_key,
                max_tokens=2000  # Increased from 300 to allow tool reasoning and responses
            )
        else:
            # Return a mock LLM that provides informative responses when no API key is available
            # Note: FakeListLLM doesn't support tools, so we need to handle this case specially
            return FakeListLLM(responses=[
                f"I'm a {model} agent simulation. In a real deployment, I would connect to the {provider} API to generate responses.",
                f"This is a simulated response from a {model} model. Please configure your {provider} API key to get real responses.",
                f"Mock response from {provider} {model} model. Add your API key to .env file to enable real functionality."
            ])
    
    def _create_custom_react_agent(self, llm, tools, system_prompt: str):
        """Create a custom ReAct agent using LangGraph for better control"""
        from langgraph.graph import StateGraph, START, END
        from langgraph.prebuilt import ToolNode
        from typing import Annotated, Sequence, TypedDict, Union
        from langchain_core.messages import BaseMessage, SystemMessage
        from langgraph.graph.message import add_messages

        class AgentState(TypedDict):
            messages: Annotated[Sequence[BaseMessage], add_messages]

        # Bind tools to LLM
        llm_with_tools = llm.bind_tools(tools)

        def agent_node(state: AgentState):
            """Call the LLM"""
            messages = state["messages"]
            # Ensure system prompt is first
            # Ensure system prompt is first and not duplicated
            if not messages or not isinstance(messages[0], SystemMessage) or messages[0].content != system_prompt:
                # Remove any existing system messages to avoid stacking
                messages = [m for m in messages if not isinstance(m, SystemMessage)]
                messages = [SystemMessage(content=system_prompt)] + list(messages)
            
            response = llm_with_tools.invoke(messages)
            return {"messages": [response]}

        def should_continue(state: AgentState):
            """Determine if we should continue to tools or end"""
            messages = state["messages"]
            last_message = messages[-1]
            if last_message.tool_calls:
                return "tools"
            return END

        # Create the graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", ToolNode(tools, handle_tool_errors=True))

        # Add edges
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            ["tools", END]
        )
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    async def _create_react_agent(self, llm, agent_config, memory_context: str = "", knowledge_context: str = ""):
        """Create a generic ReAct agent with adaptable tools.
        Returns a tuple of (agent_graph, tool_names).
        """
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        
        # Check if the LLM supports tools (bind_tools method)
        # FakeListLLM doesn't support tools, so we need to handle this case
        tools = []
        llm_supports_tools = hasattr(llm, 'bind_tools')
        
        # DEBUGGING: Log LLM type and tool support
        logger.info(f"_create_react_agent: LLM type={type(llm).__name__}, supports bind_tools={llm_supports_tools}")
        if not llm_supports_tools:
            logger.warning(f"⚠️ LLM {type(llm).__name__} does NOT support bind_tools - MCP tools will NOT be loaded!")

        if llm_supports_tools:
            # Load MCP tools first (from connected MCP servers)
            # Load MCP tools first (from connected MCP servers)
            # CRITICAL: Do not silence errors here. If MCP tools fail to load, the agent is broken.
            try:
                mcp_tools = await self.get_agent_mcp_tools(agent_config.agent_id)
                if mcp_tools:
                    tools.extend(mcp_tools)
            except Exception as e:
                logger.error(f"CRITICAL: Failed to load MCP tools for agent {agent_config.agent_id}: {e}")
                # We re-raise because an agent configured with tools MUST have them
                raise Exception(f"Failed to initialize agent tools: {e}")
            
            # Add external tools if configured
            if hasattr(agent_config, 'tools') and agent_config.tools:
                try:
                    # Get tool configurations if available
                    tool_configs = {}
                    if hasattr(agent_config, 'tool_configs') and agent_config.tool_configs:
                        tool_configs = agent_config.tool_configs
                    
                    print(f"DEBUG: Agent tools requested: {agent_config.tools}")
                    print(f"DEBUG: Agent tool_configs: {tool_configs}")
                    
                    other_tools = []
                    for tool_name in agent_config.tools:
                        if tool_name == "mcp_database" and tool_configs.get("mcp_database"):
                            continue
                        other_tools.append(tool_name)
                    
                    print(f"DEBUG: Non-MCP tools to load: {other_tools}")
                    
                    # Get non-MCP external tools first
                    if other_tools:
                        external_tools = self.tools_service.get_tools(other_tools, tool_configs)
                        tools.extend(external_tools)
                        print(f"DEBUG: External tools loaded: {[t.name for t in external_tools]}")
                except Exception as e:
                    print(f"Error loading agent tools: {e}")
            
        # ✅ FIX: Only use create_react_agent when we actually have tools
        # When tools=[] is passed to create_react_agent, LangGraph still configures it
        # in "tool mode" with tool_choice="none", which causes Groq to error when
        # the model tries to call tools despite tool_choice being "none"
        if llm_supports_tools and tools:
            # We have tools - use ReAct agent with tool binding
            logger.info(f"Creating ReAct agent with {len(tools)} tools for agent {agent_config.agent_id}")
            logger.info(f"Tool names: {[t.name for t in tools]}")
            
            # Build tool metadata for system prompt (name + description)
            tool_metadata = []
            for t in tools:
                tool_info = {
                    "name": t.name,
                    "description": t.description if hasattr(t, 'description') and t.description else "No description available"
                }
                tool_metadata.append(tool_info)
            
            # IMPORTANT: Don't just bind tools - create_react_agent does this internally
            # Passing llm_with_tools AND tools to create_react_agent can cause duplicate binding
            # Just pass the base LLM and let create_react_agent handle tool binding
            
            # Construct the full system prompt here to pass as state_modifier
            system_content = agent_config.system_prompt or "You are a helpful AI assistant."
            
            # Add knowledge base context if available
            has_kb = False
            if knowledge_context:
                has_kb = True
                system_content += f"\n\n## Knowledge Base Information\n{knowledge_context}"
                system_content += "\n\n**Note**: This knowledge base contains verified information about this domain. You can use it for static/reference information, but remember your tools are available for real-time data and external actions."
            
            # Add memory context from previous conversations
            if memory_context:
                system_content += f"\n\n## Context from Previous Conversations\n{memory_context}"
            
            # Add available tools information with CLEAR ENCOURAGEMENT to use them
            if tool_metadata:
                # Build tool list with full descriptions from tool metadata
                tool_descriptions = []
                for tool in tool_metadata:
                    tool_name = tool.get("name", "")
                    tool_desc = tool.get("description", "") or "No description provided."

                    # Preserve full instructions for Puppeteer evaluate (contains critical guidance)
                    if tool_name and "puppeteer_evaluate" in tool_name.lower():
                        final_desc = tool_desc
                    else:
                        max_len = 400
                        final_desc = tool_desc if len(tool_desc) <= max_len else tool_desc[:max_len].rstrip() + "..."

                    tool_descriptions.append(f"  • **{tool_name}**: {final_desc}")
                
                tools_list = "\n".join(tool_descriptions)
                
                system_content += (
                    f"\n\n## 🛠️ YOUR AVAILABLE TOOLS (USE THESE ACTIVELY!)\n"
                    f"You have {len(tools)} powerful tools ready to use:\n"
                    f"{tools_list}\n\n"
                    "**⚡ TOOL USAGE IS ENCOURAGED:**\n"
                    "• These tools are your PRIMARY way to complete tasks that require external actions\n"
                    "• Use tools for web browsing, data extraction, API calls, automation, etc.\n"
                    "• Tools work reliably - don't hesitate to use them!\n"
                    "• When a task clearly needs a tool (like browsing a website), USE IT IMMEDIATELY\n"
                )
                
                # Add balanced guidance about KB if it exists
                if has_kb:
                    system_content += (
                        "\n**Balancing Knowledge Base and Tools:**\n"
                        "• Knowledge Base: Good for static, verified domain information\n"
                        "• Tools: REQUIRED for real-time data, external websites, automation, current information\n"
                        "• If the task needs external data or actions → USE TOOLS (don't rely on KB)\n"
                        "• If KB has the exact answer → You can use KB directly\n"
                        "• When in doubt → Using tools is safer than guessing from KB\n"
                    )
                
                system_content += (
                    "\n**Tool Usage Best Practices:**\n"
                    "• Choose the right tool for each task\n"
                    "• Follow the tool's schema carefully (provide all required parameters)\n"
                    "• If a tool fails once, read the error and try a different approach or tool\n"
                    "• Break complex tasks into multiple tool calls if needed\n"
                )
            
            # Add error recovery guidance (de-emphasized, only as reference)
            if tools:
                system_content += (
                    "\n\n## Error Recovery (Reference Only - Most Tools Work Fine)\n"
                    "If a tool fails with an error:\n"
                    "1. Read the error message - it often contains specific fix instructions\n"
                    "2. Don't retry the exact same action - try a different approach or fix the parameters\n"
                    "3. If one tool doesn't work, try an alternative tool\n"
                    "4. After 2 failures with the same tool, switch to a different tool\n"
                    "\nFor Puppeteer tools: If puppeteer_evaluate fails, try puppeteer_click, puppeteer_screenshot, or other tools.\n"
                    "\n**CRITICAL PUPPETEER INSTRUCTION:**\n"
                    "• You MUST call `browser_navigate` to open a page BEFORE using any other browser tool (wait, click, type, etc.).\n"
                    "• If you see 'No open pages available', it means you forgot to navigate or the browser closed. Call `browser_navigate` immediately.\n"
                )
            
            # Enforce concise response style
            system_content += (
                "\n\nGuidelines:\n"
                "1. **Step-by-Step**: Perform multi-step tasks one by one. Do not stop until the user's goal is fully achieved.\n"
                "2. **Conciseness**: Keep responses concise (<=120 words). Use at most 5 bullet points.\n"
                "3. **Clarification**: Ask at most one clarifying question only if necessary.\n"
                "4. **No Fluff**: Avoid long introductions."
            )
            
            return self._create_custom_react_agent(llm, tools, system_prompt=system_content), tool_metadata
        else:
            # NO TOOLS or LLM doesn't support tools - create a simple conversational agent
            # This avoids tool_choice configuration entirely and works with all providers
            from langgraph.graph import StateGraph, START
            from typing import Annotated
            from typing_extensions import TypedDict
            from operator import add
            from langchain_core.messages import HumanMessage, AIMessage
            
            class MessagesState(TypedDict):
                messages: Annotated[list, add]
            
            async def call_model(state: MessagesState):
                """Simple conversational agent without tool infrastructure"""
                messages = state["messages"]
                
                # Check if LLM has async support
                if hasattr(llm, 'ainvoke'):
                    response = await llm.ainvoke(messages)
                else:
                    # Fallback to sync invoke for mock LLMs
                    import asyncio
                    response = await asyncio.to_thread(llm.invoke, messages)
                
                return {"messages": [response]}
            
            # Create a simple conversational agent graph
            logger.info(f"Creating simple conversational agent (no tools) for agent {agent_config.agent_id}")
            workflow = StateGraph(MessagesState)
            workflow.add_node("call_model", call_model)
            workflow.add_edge(START, "call_model")
            workflow.add_edge("call_model", END)
            
            return workflow.compile(), []
    
    def _create_plan_execute_agent(self, llm, agent_config, memory_context: str = ""):
        """Create a generic Plan & Execute agent for complex multi-step tasks"""
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        
        # Define state for the agent
        from typing import Annotated, Sequence, TypedDict
        from langgraph.graph import add_messages
        
        class PlanExecuteState(TypedDict):
            input: str
            agent_plan: str
            past_steps: Annotated[Sequence[str], add_messages]
            response: str
        
        # Planner node - creates a plan
        def planner_node(state: PlanExecuteState):
            """Create a plan for executing the user request"""
            system_prompt = agent_config.system_prompt or "You are an expert at creating plans for complex tasks."
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
                
            planner_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
For the user request, create a SHORT plan of up to 5 steps. Each step must be a single actionable line. Be concise.

User Request: {{input}}

Plan:""")
            
            chain = planner_prompt | llm | StrOutputParser()
            plan = chain.invoke({"input": state["input"]})
            return {"agent_plan": plan}
        
        # Executor node - executes the plan
        def executor_node(state: PlanExecuteState):
            """Execute the plan steps"""
            system_prompt = agent_config.system_prompt or "You are an expert at executing plans."
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
                
            executor_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
Here is the plan to execute (concise execution, <=100 words):
{{agent_plan}}

Execute the next step and return a brief result.

Previous steps: {{past_steps}}

Next step result:""")
            
            chain = executor_prompt | llm | StrOutputParser()
            result = chain.invoke({
                "agent_plan": state["agent_plan"],
                "past_steps": "\n".join(state["past_steps"]) if state["past_steps"] else "None"
            })
            
            return {"past_steps": [result]}
        
        # Create the workflow
        workflow = StateGraph(PlanExecuteState)
        
        # Add nodes
        workflow.add_node("planner", planner_node)
        workflow.add_node("executor", executor_node)
        
        # Add edges
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "executor")
        workflow.add_edge("executor", END)
        
        # Compile without checkpointer
        return workflow.compile()
    
    def _create_reflection_agent(self, llm, agent_config, memory_context: str = ""):
        """Create a generic Reflection agent that improves its responses through self-evaluation"""
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from typing import Annotated, Sequence, TypedDict
        from langgraph.graph import add_messages
        
        class ReflectionState(TypedDict):
            input: str
            agent_draft: str
            agent_critique: str
            agent_revision: str
        
        # Agent node - generates initial response
        def agent_node(state: ReflectionState):
            """Generate initial response"""
            system_prompt = agent_config.system_prompt or "You are a helpful AI assistant."
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
                
            agent_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
Provide a concise response to the user request (<=120 words, up to 5 bullets if needed).

User Request: {{input}}

Response:""")
            
            chain = agent_prompt | llm | StrOutputParser()
            draft = chain.invoke({"input": state["input"]})
            return {"agent_draft": draft}
        
        # Critique node - evaluates the response
        def critique_node(state: ReflectionState):
            """Critique the initial response"""
            system_prompt = agent_config.system_prompt or "You are an expert reviewer."
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
                
            critique_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
Review the following response for quality, accuracy, and unnecessary verbosity. Suggest how to make it shorter while preserving key information.

Response: {{agent_draft}}

User Request: {{input}}

Critique:""")
            
            chain = critique_prompt | llm | StrOutputParser()
            critique = chain.invoke({"agent_draft": state["agent_draft"], "input": state["input"]})
            return {"agent_critique": critique}
        
        # Revision node - improves based on critique
        def revision_node(state: ReflectionState):
            """Revise the response based on critique"""
            system_prompt = agent_config.system_prompt or "You are an expert editor."
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
                
            revision_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
Improve the response based on the critique. Make it concise (<=120 words) and to the point.

Original Response: {{agent_draft}}

Critique: {{agent_critique}}

User Request: {{input}}

Improved Response:""")
            
            chain = revision_prompt | llm | StrOutputParser()
            revision = chain.invoke({
                "agent_draft": state["agent_draft"], 
                "agent_critique": state["agent_critique"],
                "input": state["input"]
            })
            return {"agent_revision": revision}
        
        # Create the workflow
        workflow = StateGraph(ReflectionState)
        
        # Add nodes
        workflow.add_node("agent", agent_node)
        workflow.add_node("critique", critique_node)
        workflow.add_node("revision", revision_node)
        
        # Add edges
        workflow.set_entry_point("agent")
        workflow.add_edge("agent", "critique")
        workflow.add_edge("critique", "revision")
        workflow.add_edge("revision", END)
        
        # Compile without checkpointer
        return workflow.compile()
    
    def _create_custom_agent(self, llm, agent_config, memory_context: str = ""):
        """Create a flexible custom agent graph for specialized workflows"""
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from typing import Annotated, Sequence, TypedDict
        from langgraph.graph import add_messages
        
        class CustomAgentState(TypedDict):
            input: str
            agent_analysis: str
            agent_action: str
            agent_result: str
        
        # Analysis node - analyzes the request
        def analysis_node(state: CustomAgentState):
            """Analyze the user request and determine the approach"""
            system_prompt = agent_config.system_prompt or "You are a helpful assistant."
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
                
            analysis_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
You are an expert problem analyzer. Provide a brief analysis (3-5 bullet points max).

User Request: {{input}}

Analysis:""")
            
            chain = analysis_prompt | llm | StrOutputParser()
            analysis = chain.invoke({"input": state["input"]})
            return {"agent_analysis": analysis}
        
        # Action node - takes action based on analysis
        def action_node(state: CustomAgentState):
            """Take action based on analysis"""
            system_prompt = agent_config.system_prompt or "You are a helpful assistant."
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
                
            action_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
You are an expert problem solver. Based on the analysis, determine the best action. Keep it brief (<=80 words).

Analysis: {{agent_analysis}}

User Request: {{input}}

Action:""")
            
            chain = action_prompt | llm | StrOutputParser()
            action = chain.invoke({"agent_analysis": state["agent_analysis"], "input": state["input"]})
            return {"agent_action": action}
        
        # Result formatter node - formats the result
        def result_node(state: CustomAgentState):
            """Format the final result"""
            system_prompt = agent_config.system_prompt or "You are a helpful assistant."
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
                
            result_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
Provide a clear, concise response to the user's request based on the action taken (<=120 words, up to 5 bullets).

Action Taken: {{agent_action}}

User Request: {{input}}

Final Response:""")
            
            chain = result_prompt | llm | StrOutputParser()
            result = chain.invoke({
                "agent_action": state["agent_action"], 
                "input": state["input"]
            })
            return {"agent_result": result}
        
        # Create the workflow
        workflow = StateGraph(CustomAgentState)
        
        # Add nodes
        workflow.add_node("analysis", analysis_node)
        workflow.add_node("action", action_node)
        workflow.add_node("result", result_node)
        
        # Add edges
        workflow.set_entry_point("analysis")
        workflow.add_edge("analysis", "action")
        workflow.add_edge("action", "result")
        workflow.add_edge("result", END)
        
        # Compile without checkpointer
        return workflow.compile()
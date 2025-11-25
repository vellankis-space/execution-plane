from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class MCPServerConfig(BaseModel):
    """Configuration for MCP server association with tool selection"""
    server_id: str
    selected_tools: Optional[List[str]] = None  # None = all tools, or specific tool names


class AgentBase(BaseModel):
    name: str
    agent_type: str
    llm_provider: str
    llm_model: str
    temperature: float  # Changed from int to float to match the model
    system_prompt: Optional[str] = ""
    tools: List[str] = []
    tool_configs: Optional[Dict[str, Any]] = None  # Tool-specific configurations (API keys, settings)
    max_iterations: int
    memory_type: Optional[str] = None  # Deprecated field for backward compatibility
    streaming_enabled: bool
    human_in_loop: bool
    recursion_limit: int
    pii_config: Optional[Dict[str, Any]] = None  # PII filtering configuration
    mcp_servers: Optional[List[str]] = None  # List of MCP server IDs (backward compatibility)
    mcp_server_configs: Optional[List[MCPServerConfig]] = None  # MCP servers with tool selection

class AgentCreate(AgentBase):
    api_key: Optional[str] = ""  # Optional: user's API key (will be encrypted if provided)

class AgentInDB(AgentBase):
    agent_id: str
    api_key_encrypted: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AgentExecutionRequest(BaseModel):
    input: str

class AgentChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None  # Session ID for ephemeral memory


class AgentResponse(BaseModel):
    """Response schema that excludes sensitive fields"""
    agent_id: str
    name: str
    agent_type: str
    llm_provider: str
    llm_model: str
    temperature: float
    system_prompt: Optional[str] = ""
    tools: List[str] = []
    max_iterations: int
    streaming_enabled: bool
    human_in_loop: bool
    recursion_limit: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgentExecutionResponse(BaseModel):
    response: str
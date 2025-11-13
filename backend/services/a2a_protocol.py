"""
A2A Protocol (Agent-to-Agent) Implementation
Based on https://a2a-protocol.org/latest/
Enables standardized agent-to-agent communication using JSON-RPC 2.0
"""
import json
import logging
import uuid
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, asdict
import httpx

logger = logging.getLogger(__name__)


class A2AMethod(str, Enum):
    """A2A Protocol JSON-RPC methods"""
    # Agent discovery
    DISCOVER_AGENTS = "a2a.discover"
    GET_AGENT_CARD = "a2a.getAgentCard"
    
    # Task execution
    EXECUTE_TASK = "a2a.executeTask"
    CANCEL_TASK = "a2a.cancelTask"
    GET_TASK_STATUS = "a2a.getTaskStatus"
    
    # Streaming
    STREAM_TASK = "a2a.streamTask"
    
    # Capabilities
    GET_CAPABILITIES = "a2a.getCapabilities"
    
    # Health check
    PING = "a2a.ping"
    PONG = "a2a.pong"


@dataclass
class AgentCard:
    """Agent Card - machine-readable JSON document describing an agent"""
    agent_id: str
    name: str
    version: str
    description: str
    capabilities: List[str]
    endpoint: str  # Base URL for A2A communication
    authentication: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Agent Card to dictionary"""
        result = {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": self.capabilities,
            "endpoint": self.endpoint,
        }
        if self.authentication:
            result["authentication"] = self.authentication
        if self.metadata:
            result["metadata"] = self.metadata
        return result
    
    def to_json(self) -> str:
        """Convert Agent Card to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class A2ARequest:
    """A2A Protocol JSON-RPC 2.0 request"""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary"""
        result = {
            "jsonrpc": self.jsonrpc,
            "method": self.method,
            "id": self.id
        }
        if self.params:
            result["params"] = self.params
        return result
    
    def to_json(self) -> str:
        """Convert request to JSON string"""
        return json.dumps(self.to_dict())


@dataclass
class A2AResponse:
    """A2A Protocol JSON-RPC 2.0 response"""
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        result = {
            "jsonrpc": self.jsonrpc,
            "id": self.id
        }
        if self.error:
            result["error"] = self.error
        else:
            result["result"] = self.result
        return result
    
    def to_json(self) -> str:
        """Convert response to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AResponse":
        """Create A2AResponse from dictionary"""
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            result=data.get("result"),
            error=data.get("error"),
            id=data.get("id")
        )
    
    @classmethod
    def error_response(cls, request_id: str, code: int, message: str, data: Optional[Any] = None) -> "A2AResponse":
        """Create an error response"""
        error = {
            "code": code,
            "message": message
        }
        if data is not None:
            error["data"] = data
        
        return cls(
            jsonrpc="2.0",
            error=error,
            id=request_id
        )


class A2AProtocol:
    """A2A Protocol handler for agent-to-agent communication"""
    
    def __init__(self, agent_id: str, agent_card: AgentCard):
        self.agent_id = agent_id
        self.agent_card = agent_card
        self.method_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default method handlers"""
        self.method_handlers[A2AMethod.PING] = self._handle_ping
        self.method_handlers[A2AMethod.GET_AGENT_CARD] = self._handle_get_agent_card
        self.method_handlers[A2AMethod.GET_CAPABILITIES] = self._handle_get_capabilities
    
    def register_handler(self, method: str, handler: Callable):
        """Register a custom method handler"""
        self.method_handlers[method] = handler
    
    def handle_request(self, request_data: Dict[str, Any]) -> A2AResponse:
        """Handle an incoming A2A request"""
        try:
            request = A2ARequest(
                method=request_data.get("method", ""),
                params=request_data.get("params"),
                id=request_data.get("id")
            )
            
            if not request.method:
                return A2AResponse.error_response(
                    request.id or "",
                    -32600,
                    "Invalid Request",
                    "Method is required"
                )
            
            # Find handler
            handler = self.method_handlers.get(request.method)
            if not handler:
                return A2AResponse.error_response(
                    request.id or "",
                    -32601,
                    "Method not found",
                    f"Method '{request.method}' is not supported"
                )
            
            # Execute handler
            try:
                result = handler(request.params or {})
                return A2AResponse(
                    jsonrpc="2.0",
                    result=result,
                    id=request.id
                )
            except Exception as e:
                logger.error(f"Error executing handler for {request.method}: {e}")
                return A2AResponse.error_response(
                    request.id or "",
                    -32603,
                    "Internal error",
                    str(e)
                )
        
        except Exception as e:
            logger.error(f"Error handling A2A request: {e}")
            return A2AResponse.error_response(
                request_data.get("id", ""),
                -32700,
                "Parse error",
                str(e)
            )
    
    def _handle_ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping request"""
        return {
            "status": "pong",
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": self.agent_id
        }
    
    def _handle_get_agent_card(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get agent card request"""
        return self.agent_card.to_dict()
    
    def _handle_get_capabilities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get capabilities request"""
        return {
            "capabilities": self.agent_card.capabilities,
            "agent_id": self.agent_id,
            "version": self.agent_card.version
        }
    
    async def call_remote_agent(
        self,
        agent_endpoint: str,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0
    ) -> A2AResponse:
        """Call a remote agent using A2A Protocol"""
        request = A2ARequest(
            method=method,
            params=params or {}
        )
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    agent_endpoint,
                    json=request.to_dict(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                data = response.json()
                return A2AResponse.from_dict(data)
        
        except httpx.TimeoutException:
            return A2AResponse.error_response(
                request.id,
                -32000,
                "Timeout",
                "Request to remote agent timed out"
            )
        except httpx.HTTPStatusError as e:
            return A2AResponse.error_response(
                request.id,
                -32001,
                "HTTP Error",
                f"HTTP {e.response.status_code}: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Error calling remote agent: {e}")
            return A2AResponse.error_response(
                request.id,
                -32603,
                "Internal error",
                str(e)
            )
    
    async def discover_agents(self, discovery_endpoint: str, query: Optional[Dict[str, Any]] = None) -> List[AgentCard]:
        """Discover available agents"""
        try:
            response = await self.call_remote_agent(
                discovery_endpoint,
                A2AMethod.DISCOVER_AGENTS,
                params=query or {}
            )
            
            if response.error:
                logger.error(f"Error discovering agents: {response.error}")
                return []
            
            # Parse agent cards from response
            agents_data = response.result.get("agents", [])
            return [AgentCard(**agent_data) for agent_data in agents_data]
        
        except Exception as e:
            logger.error(f"Error in agent discovery: {e}")
            return []
    
    async def execute_task_on_agent(
        self,
        agent_endpoint: str,
        task: Dict[str, Any],
        timeout: float = 60.0
    ) -> A2AResponse:
        """Execute a task on a remote agent"""
        return await self.call_remote_agent(
            agent_endpoint,
            A2AMethod.EXECUTE_TASK,
            params={"task": task},
            timeout=timeout
        )
    
    async def get_task_status(
        self,
        agent_endpoint: str,
        task_id: str
    ) -> A2AResponse:
        """Get status of a task on a remote agent"""
        return await self.call_remote_agent(
            agent_endpoint,
            A2AMethod.GET_TASK_STATUS,
            params={"task_id": task_id}
        )


class A2AAgentRegistry:
    """Registry for managing A2A agents"""
    
    def __init__(self):
        self.agents: Dict[str, AgentCard] = {}
        self.protocols: Dict[str, A2AProtocol] = {}
    
    def register_agent(self, agent_card: AgentCard, protocol: A2AProtocol):
        """Register an agent in the registry"""
        self.agents[agent_card.agent_id] = agent_card
        self.protocols[agent_card.agent_id] = protocol
        logger.info(f"Registered A2A agent: {agent_card.agent_id} at {agent_card.endpoint}")
    
    def get_agent_card(self, agent_id: str) -> Optional[AgentCard]:
        """Get agent card by ID"""
        return self.agents.get(agent_id)
    
    def get_protocol(self, agent_id: str) -> Optional[A2AProtocol]:
        """Get A2A protocol instance for an agent"""
        return self.protocols.get(agent_id)
    
    def list_agents(self, capabilities: Optional[List[str]] = None) -> List[AgentCard]:
        """List all registered agents, optionally filtered by capabilities"""
        agents = list(self.agents.values())
        
        if capabilities:
            agents = [
                agent for agent in agents
                if any(cap in agent.capabilities for cap in capabilities)
            ]
        
        return agents
    
    def discover_remote_agents(self, discovery_endpoint: str) -> List[AgentCard]:
        """Discover agents from a remote discovery service"""
        # This would typically call a discovery service
        # For now, return empty list
        return []


# Global registry instance
a2a_registry = A2AAgentRegistry()


"""
Agent UI Protocol - Standardized protocol for UI-Agent communication
Supports real-time streaming, status updates, tool calls, and structured messages
"""
import json
import logging
from typing import Dict, Any, Optional, AsyncIterator
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, asdict
from json import JSONEncoder

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Message types in Agent UI Protocol"""
    # Connection management
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"
    
    # User messages
    USER_MESSAGE = "user_message"
    
    # Agent responses
    AGENT_RESPONSE = "agent_response"
    AGENT_THINKING = "agent_thinking"
    AGENT_ERROR = "agent_error"
    
    # Streaming
    STREAM_START = "stream_start"
    STREAM_CHUNK = "stream_chunk"
    STREAM_END = "stream_end"
    
    # Tool execution
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_PROGRESS = "tool_call_progress"
    TOOL_CALL_END = "tool_call_end"
    TOOL_CALL_ERROR = "tool_call_error"
    
    # Status updates
    STATUS_UPDATE = "status_update"
    PROGRESS_UPDATE = "progress_update"
    
    # Workflow specific
    WORKFLOW_START = "workflow_start"
    WORKFLOW_STEP_START = "workflow_step_start"
    WORKFLOW_STEP_END = "workflow_step_end"
    WORKFLOW_END = "workflow_end"
    
    # Memory operations
    MEMORY_UPDATE = "memory_update"
    
    # Cost tracking
    COST_UPDATE = "cost_update"


class StatusType(str, Enum):
    """Status types for agent operations"""
    IDLE = "idle"
    PROCESSING = "processing"
    THINKING = "thinking"
    EXECUTING_TOOL = "executing_tool"
    STREAMING = "streaming"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class ProtocolMessage:
    """Base protocol message structure"""
    type: MessageType
    timestamp: str
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    workflow_id: Optional[str] = None
    execution_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        result = {
            "type": self.type.value,
            "timestamp": self.timestamp,
        }
        if self.session_id:
            result["session_id"] = self.session_id
        if self.agent_id:
            result["agent_id"] = self.agent_id
        if self.workflow_id:
            result["workflow_id"] = self.workflow_id
        if self.execution_id:
            result["execution_id"] = self.execution_id
        if self.data:
            result["data"] = self.data
        if self.metadata:
            result["metadata"] = self.metadata
        return result
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict())


class ProtocolMessageEncoder(JSONEncoder):
    """Custom JSON encoder for protocol messages"""
    def default(self, obj):
        if isinstance(obj, ProtocolMessage):
            return obj.to_dict()
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class AgentUIProtocol:
    """Agent UI Protocol handler for standardized communication"""
    
    @staticmethod
    def create_message(
        message_type: MessageType,
        data: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProtocolMessage:
        """Create a protocol message"""
        return ProtocolMessage(
            type=message_type,
            timestamp=datetime.utcnow().isoformat(),
            session_id=session_id,
            agent_id=agent_id,
            workflow_id=workflow_id,
            execution_id=execution_id,
            data=data,
            metadata=metadata
        )
    
    @staticmethod
    def create_user_message(
        content: str,
        session_id: str,
        agent_id: Optional[str] = None
    ) -> ProtocolMessage:
        """Create a user message"""
        return AgentUIProtocol.create_message(
            message_type=MessageType.USER_MESSAGE,
            data={"content": content},
            session_id=session_id,
            agent_id=agent_id
        )
    
    @staticmethod
    def create_agent_response(
        content: str,
        session_id: str,
        agent_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProtocolMessage:
        """Create an agent response message"""
        return AgentUIProtocol.create_message(
            message_type=MessageType.AGENT_RESPONSE,
            data={"content": content},
            session_id=session_id,
            agent_id=agent_id,
            metadata=metadata
        )
    
    @staticmethod
    def create_stream_chunk(
        chunk: str,
        session_id: str,
        agent_id: str,
        is_final: bool = False
    ) -> ProtocolMessage:
        """Create a streaming chunk message"""
        return AgentUIProtocol.create_message(
            message_type=MessageType.STREAM_CHUNK,
            data={"chunk": chunk, "is_final": is_final},
            session_id=session_id,
            agent_id=agent_id
        )
    
    @staticmethod
    def create_stream_start(
        session_id: str,
        agent_id: str
    ) -> ProtocolMessage:
        """Create a stream start message"""
        return AgentUIProtocol.create_message(
            message_type=MessageType.STREAM_START,
            session_id=session_id,
            agent_id=agent_id
        )
    
    @staticmethod
    def create_stream_end(
        session_id: str,
        agent_id: str,
        total_tokens: Optional[int] = None,
        cost: Optional[float] = None
    ) -> ProtocolMessage:
        """Create a stream end message"""
        data = {}
        if total_tokens is not None:
            data["total_tokens"] = total_tokens
        if cost is not None:
            data["cost"] = cost
        
        return AgentUIProtocol.create_message(
            message_type=MessageType.STREAM_END,
            data=data,
            session_id=session_id,
            agent_id=agent_id
        )
    
    @staticmethod
    def create_thinking_message(
        thought: str,
        session_id: str,
        agent_id: str
    ) -> ProtocolMessage:
        """Create an agent thinking message"""
        return AgentUIProtocol.create_message(
            message_type=MessageType.AGENT_THINKING,
            data={"thought": thought},
            session_id=session_id,
            agent_id=agent_id
        )
    
    @staticmethod
    def create_tool_call_start(
        tool_name: str,
        tool_args: Dict[str, Any],
        session_id: str,
        agent_id: str
    ) -> ProtocolMessage:
        """Create a tool call start message"""
        return AgentUIProtocol.create_message(
            message_type=MessageType.TOOL_CALL_START,
            data={
                "tool_name": tool_name,
                "tool_args": tool_args
            },
            session_id=session_id,
            agent_id=agent_id
        )
    
    @staticmethod
    def create_tool_call_end(
        tool_name: str,
        result: Any,
        session_id: str,
        agent_id: str,
        execution_time: Optional[float] = None
    ) -> ProtocolMessage:
        """Create a tool call end message"""
        data = {
            "tool_name": tool_name,
            "result": str(result) if not isinstance(result, (str, int, float, bool, dict, list)) else result
        }
        if execution_time is not None:
            data["execution_time"] = execution_time
        
        return AgentUIProtocol.create_message(
            message_type=MessageType.TOOL_CALL_END,
            data=data,
            session_id=session_id,
            agent_id=agent_id
        )
    
    @staticmethod
    def create_tool_call_error(
        tool_name: str,
        error: str,
        session_id: str,
        agent_id: str
    ) -> ProtocolMessage:
        """Create a tool call error message"""
        return AgentUIProtocol.create_message(
            message_type=MessageType.TOOL_CALL_ERROR,
            data={
                "tool_name": tool_name,
                "error": error
            },
            session_id=session_id,
            agent_id=agent_id
        )
    
    @staticmethod
    def create_status_update(
        status: StatusType,
        message: Optional[str] = None,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        progress: Optional[float] = None
    ) -> ProtocolMessage:
        """Create a status update message"""
        data = {"status": status.value}
        if message:
            data["message"] = message
        if progress is not None:
            data["progress"] = progress
        
        return AgentUIProtocol.create_message(
            message_type=MessageType.STATUS_UPDATE,
            data=data,
            session_id=session_id,
            agent_id=agent_id,
            workflow_id=workflow_id,
            execution_id=execution_id
        )
    
    @staticmethod
    def create_error_message(
        error: str,
        error_code: Optional[str] = None,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> ProtocolMessage:
        """Create an error message"""
        data = {"error": error}
        if error_code:
            data["error_code"] = error_code
        
        return AgentUIProtocol.create_message(
            message_type=MessageType.AGENT_ERROR,
            data=data,
            session_id=session_id,
            agent_id=agent_id
        )
    
    @staticmethod
    def create_cost_update(
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> ProtocolMessage:
        """Create a cost update message"""
        return AgentUIProtocol.create_message(
            message_type=MessageType.COST_UPDATE,
            data={
                "provider": provider,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "cost": cost
            },
            session_id=session_id,
            agent_id=agent_id
        )
    
    @staticmethod
    def parse_message(message_str: str) -> Optional[ProtocolMessage]:
        """Parse a protocol message from JSON string"""
        try:
            data = json.loads(message_str)
            return ProtocolMessage(
                type=MessageType(data["type"]),
                timestamp=data["timestamp"],
                session_id=data.get("session_id"),
                agent_id=data.get("agent_id"),
                workflow_id=data.get("workflow_id"),
                execution_id=data.get("execution_id"),
                data=data.get("data"),
                metadata=data.get("metadata")
            )
        except Exception as e:
            logger.error(f"Error parsing protocol message: {e}")
            return None


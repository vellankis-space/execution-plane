"""
AG-UI Protocol Implementation
Agent-User Interaction Protocol for standardized UI-Agent communication
Based on https://docs.ag-ui.com/
"""
import json
import logging
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AGUIEventType(str, Enum):
    """AG-UI Protocol event types"""
    # Run lifecycle
    RUN_STARTED = "run_started"
    RUN_FINISHED = "run_finished"
    RUN_CANCELLED = "run_cancelled"
    
    # Messages
    TEXT_MESSAGE_CONTENT = "text_message_content"
    ATTACHMENT_MESSAGE_CONTENT = "attachment_message_content"
    
    # Tool calls
    TOOL_CALL_STARTED = "tool_call_started"
    TOOL_CALL_FINISHED = "tool_call_finished"
    TOOL_CALL_ERROR = "tool_call_error"
    
    # State management
    STATE_UPDATE = "state_update"
    STATE_DIFF = "state_diff"
    
    # Frontend actions
    FRONTEND_ACTION_REQUEST = "frontend_action_request"
    FRONTEND_ACTION_RESPONSE = "frontend_action_response"
    
    # Human-in-the-loop
    HUMAN_INPUT_REQUEST = "human_input_request"
    HUMAN_INPUT_RESPONSE = "human_input_response"
    
    # Streaming
    STREAM_START = "stream_start"
    STREAM_CHUNK = "stream_chunk"
    STREAM_END = "stream_end"
    
    # Error handling
    ERROR = "error"
    
    # Metadata
    METADATA = "metadata"


@dataclass
class AGUIMessage:
    """AG-UI Protocol message structure"""
    event: AGUIEventType
    run_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        result = {
            "event": self.event.value,
            "timestamp": self.timestamp,
        }
        if self.run_id:
            result["run_id"] = self.run_id
        if self.session_id:
            result["session_id"] = self.session_id
        if self.data:
            result["data"] = self.data
        if self.metadata:
            result["metadata"] = self.metadata
        return result
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict(), default=str)


class AGUIProtocol:
    """AG-UI Protocol handler"""
    
    @staticmethod
    def create_run_started(
        run_id: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AGUIMessage:
        """Create a RUN_STARTED event"""
        return AGUIMessage(
            event=AGUIEventType.RUN_STARTED,
            run_id=run_id,
            session_id=session_id,
            data={"run_id": run_id},
            metadata=metadata
        )
    
    @staticmethod
    def create_run_finished(
        run_id: str,
        session_id: Optional[str] = None,
        result: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AGUIMessage:
        """Create a RUN_FINISHED event"""
        data = {}
        if result is not None:
            data["result"] = result
        
        return AGUIMessage(
            event=AGUIEventType.RUN_FINISHED,
            run_id=run_id,
            session_id=session_id,
            data=data,
            metadata=metadata
        )
    
    @staticmethod
    def create_text_message(
        content: str,
        run_id: str,
        session_id: Optional[str] = None,
        role: str = "assistant",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AGUIMessage:
        """Create a TEXT_MESSAGE_CONTENT event"""
        return AGUIMessage(
            event=AGUIEventType.TEXT_MESSAGE_CONTENT,
            run_id=run_id,
            session_id=session_id,
            data={
                "content": content,
                "role": role
            },
            metadata=metadata
        )
    
    @staticmethod
    def create_stream_chunk(
        chunk: str,
        run_id: str,
        session_id: Optional[str] = None,
        is_final: bool = False
    ) -> AGUIMessage:
        """Create a STREAM_CHUNK event"""
        return AGUIMessage(
            event=AGUIEventType.STREAM_CHUNK,
            run_id=run_id,
            session_id=session_id,
            data={
                "chunk": chunk,
                "is_final": is_final
            }
        )
    
    @staticmethod
    def create_tool_call_started(
        tool_name: str,
        tool_args: Dict[str, Any],
        run_id: str,
        session_id: Optional[str] = None,
        call_id: Optional[str] = None
    ) -> AGUIMessage:
        """Create a TOOL_CALL_STARTED event"""
        return AGUIMessage(
            event=AGUIEventType.TOOL_CALL_STARTED,
            run_id=run_id,
            session_id=session_id,
            data={
                "tool_name": tool_name,
                "tool_args": tool_args,
                "call_id": call_id or f"{run_id}_{tool_name}_{datetime.utcnow().timestamp()}"
            }
        )
    
    @staticmethod
    def create_tool_call_finished(
        tool_name: str,
        result: Any,
        run_id: str,
        session_id: Optional[str] = None,
        call_id: Optional[str] = None,
        execution_time: Optional[float] = None
    ) -> AGUIMessage:
        """Create a TOOL_CALL_FINISHED event"""
        data = {
            "tool_name": tool_name,
            "result": str(result) if not isinstance(result, (str, int, float, bool, dict, list, type(None))) else result
        }
        if call_id:
            data["call_id"] = call_id
        if execution_time is not None:
            data["execution_time"] = execution_time
        
        return AGUIMessage(
            event=AGUIEventType.TOOL_CALL_FINISHED,
            run_id=run_id,
            session_id=session_id,
            data=data
        )
    
    @staticmethod
    def create_tool_call_error(
        tool_name: str,
        error: str,
        run_id: str,
        session_id: Optional[str] = None,
        call_id: Optional[str] = None
    ) -> AGUIMessage:
        """Create a TOOL_CALL_ERROR event"""
        data = {
            "tool_name": tool_name,
            "error": error
        }
        if call_id:
            data["call_id"] = call_id
        
        return AGUIMessage(
            event=AGUIEventType.TOOL_CALL_ERROR,
            run_id=run_id,
            session_id=session_id,
            data=data
        )
    
    @staticmethod
    def create_state_update(
        state: Dict[str, Any],
        run_id: str,
        session_id: Optional[str] = None,
        diff: Optional[Dict[str, Any]] = None
    ) -> AGUIMessage:
        """Create a STATE_UPDATE event"""
        data = {"state": state}
        if diff:
            data["diff"] = diff
        
        return AGUIMessage(
            event=AGUIEventType.STATE_UPDATE,
            run_id=run_id,
            session_id=session_id,
            data=data
        )
    
    @staticmethod
    def create_human_input_request(
        prompt: str,
        run_id: str,
        session_id: Optional[str] = None,
        input_type: str = "text",
        options: Optional[List[str]] = None
    ) -> AGUIMessage:
        """Create a HUMAN_INPUT_REQUEST event"""
        data = {
            "prompt": prompt,
            "input_type": input_type
        }
        if options:
            data["options"] = options
        
        return AGUIMessage(
            event=AGUIEventType.HUMAN_INPUT_REQUEST,
            run_id=run_id,
            session_id=session_id,
            data=data
        )
    
    @staticmethod
    def create_error(
        error: str,
        error_code: Optional[str] = None,
        run_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> AGUIMessage:
        """Create an ERROR event"""
        data = {"error": error}
        if error_code:
            data["error_code"] = error_code
        
        return AGUIMessage(
            event=AGUIEventType.ERROR,
            run_id=run_id,
            session_id=session_id,
            data=data
        )
    
    @staticmethod
    def create_metadata(
        metadata: Dict[str, Any],
        run_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> AGUIMessage:
        """Create a METADATA event"""
        return AGUIMessage(
            event=AGUIEventType.METADATA,
            run_id=run_id,
            session_id=session_id,
            data=metadata
        )
    
    @staticmethod
    def parse_message(message_str: str) -> Optional[AGUIMessage]:
        """Parse an AG-UI message from JSON string"""
        try:
            data = json.loads(message_str)
            return AGUIMessage(
                event=AGUIEventType(data["event"]),
                run_id=data.get("run_id"),
                session_id=data.get("session_id"),
                timestamp=data.get("timestamp"),
                data=data.get("data"),
                metadata=data.get("metadata")
            )
        except Exception as e:
            logger.error(f"Error parsing AG-UI message: {e}")
            return None


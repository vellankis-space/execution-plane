from fastapi import APIRouter, Depends, HTTPException, WebSocket
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from schemas.agent import AgentCreate, AgentInDB, AgentExecutionRequest, AgentExecutionResponse, AgentChatRequest
from services.agent_service import AgentService
from services.tools_service import ToolsService
from core.database import get_db
from pydantic import BaseModel

# Response model that excludes sensitive information like encrypted API keys
class AgentResponse(BaseModel):
    agent_id: str
    name: str
    agent_type: str
    llm_provider: str
    llm_model: str
    temperature: float  # Changed from int to float to match the model
    system_prompt: Optional[str] = ""
    tools: List[str] = []
    tool_configs: Optional[Dict[str, Any]] = None
    max_iterations: int
    streaming_enabled: bool
    human_in_loop: bool
    recursion_limit: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Memory-related models
class MemoryAddRequest(BaseModel):
    messages: List[Dict[str, str]]
    user_id: str
    agent_id: Optional[str] = None

class MemorySearchRequest(BaseModel):
    query: str
    user_id: str
    agent_id: Optional[str] = None
    top_k: int = 5

class MemoryResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None

router = APIRouter()

@router.post("/", response_model=AgentResponse)
async def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """Create a new LangGraph agent"""
    try:
        tenant_id = get_current_tenant_id()
        agent_service = AgentService(db)
        agent = await agent_service.create_agent(agent_data, tenant_id=tenant_id)
        # Convert AgentInDB to AgentResponse to exclude sensitive fields
        return AgentResponse(**agent.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get agent configuration by ID"""
    try:
        tenant_id = get_current_tenant_id()
        agent_service = AgentService(db)
        agent = await agent_service.get_agent(agent_id, tenant_id=tenant_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        # Convert AgentInDB to AgentResponse to exclude sensitive fields
        return AgentResponse(**agent.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[AgentResponse])
async def get_agents(db: Session = Depends(get_db)):
    """Get all agents"""
    try:
        tenant_id = get_current_tenant_id()
        agent_service = AgentService(db)
        agents = await agent_service.get_agents(tenant_id=tenant_id)
        # Convert AgentInDB to AgentResponse to exclude sensitive fields
        return [AgentResponse(**agent.model_dump()) for agent in agents]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """Delete an agent"""
    try:
        tenant_id = get_current_tenant_id()
        agent_service = AgentService(db)
        success = await agent_service.delete_agent(agent_id, tenant_id=tenant_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"message": "Agent deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{agent_id}/execute", response_model=AgentExecutionResponse)
async def execute_agent(agent_id: str, request: AgentExecutionRequest, db: Session = Depends(get_db)):
    """Execute an agent with input"""
    try:
        agent_service = AgentService(db)
        response = await agent_service.execute_agent(agent_id, request.input)
        return AgentExecutionResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{agent_id}/chat/", response_model=AgentExecutionResponse)
async def chat_with_agent(agent_id: str, request: AgentChatRequest, db: Session = Depends(get_db)):
    """Chat with an agent"""
    try:
        agent_service = AgentService(db)
        response = await agent_service.chat_with_agent(agent_id, request.message, thread_id=request.thread_id)
        return AgentExecutionResponse(response=response)
    except ValueError as e:
        # Handle validation errors (like API key issues) with 400 status
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle unexpected errors with 500 status
        print(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.websocket("/{agent_id}/stream")
async def stream_agent(websocket: WebSocket, agent_id: str, db: Session = Depends(get_db)):
    """WebSocket endpoint for streaming agent responses using AG-UI Protocol"""
    try:
        await websocket.accept()
        agent_service = AgentService(db)
        
        # Wait for initial message from client (optional)
        try:
            # Wait for message with timeout
            import asyncio
            initial_data = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
            data = json.loads(initial_data)
            message = data.get("message", "")
            session_id = data.get("session_id")
        except (asyncio.TimeoutError, json.JSONDecodeError, KeyError):
            # No initial message or invalid format, proceed without it
            message = None
            session_id = None
        
        await agent_service.stream_agent(websocket, agent_id, message=message, session_id=session_id)
    except Exception as e:
        try:
            # Check if websocket is still connected before trying to close
            if not websocket.client_state.name == "DISCONNECTED":
                from services.ag_ui_protocol import AGUIProtocol
                error_msg = AGUIProtocol.create_error(
                    error=str(e),
                    error_code="WEBSOCKET_ERROR"
                )
                await websocket.send_text(error_msg.to_json())
                await websocket.close(code=1011, reason=str(e))
            else:
                print(f"WebSocket already disconnected: {str(e)}")
        except Exception:
            # If we can't close the websocket, just log the error
            print(f"Error closing websocket: {str(e)}")
    finally:
        # Ensure websocket is closed
        try:
            if not websocket.client_state.name == "DISCONNECTED":
                await websocket.close()
        except Exception:
            # If we can't close the websocket, just continue
            pass
# Memory endpoints
@router.post("/memory/add", response_model=MemoryResponse)
async def add_memory(request: MemoryAddRequest, db: Session = Depends(get_db)):
    """Add a memory to mem0"""
    try:
        agent_service = AgentService(db)
        if not agent_service.memory_service.is_enabled():
            return MemoryResponse(success=False, message="Memory service not enabled. Please configure MEM0_API_KEY.")
        
        result = agent_service.memory_service.add_memory(
            messages=request.messages,
            user_id=request.user_id,
            agent_id=request.agent_id or None
        )
        
        if result:
            return MemoryResponse(success=True, data=result, message="Memory added successfully")
        else:
            return MemoryResponse(success=False, message="Failed to add memory")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/memory/search", response_model=MemoryResponse)
async def search_memory(request: MemorySearchRequest, db: Session = Depends(get_db)):
    """Search for memories in mem0"""
    try:
        agent_service = AgentService(db)
        if not agent_service.memory_service.is_enabled():
            return MemoryResponse(success=False, message="Memory service not enabled. Please configure MEM0_API_KEY.")
        
        results = agent_service.memory_service.search_memory(
            query=request.query,
            user_id=request.user_id,
            agent_id=request.agent_id or None,
            top_k=request.top_k
        )
        
        if results is not None:
            return MemoryResponse(success=True, data=results, message="Memories retrieved successfully")
        else:
            return MemoryResponse(success=False, message="Failed to search memories")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/memory/user/{user_id}", response_model=MemoryResponse)
async def get_user_memories(user_id: str, agent_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all memories for a user"""
    try:
        agent_service = AgentService(db)
        if not agent_service.memory_service.is_enabled():
            return MemoryResponse(success=False, message="Memory service not enabled. Please configure MEM0_API_KEY.")
        
        results = agent_service.memory_service.get_user_memories(user_id=user_id, agent_id=agent_id or None)
        
        if results is not None:
            return MemoryResponse(success=True, data=results, message="User memories retrieved successfully")
        else:
            return MemoryResponse(success=False, message="Failed to retrieve user memories")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/memory/session/{session_id}", response_model=MemoryResponse)
async def delete_session_memories(session_id: str, db: Session = Depends(get_db)):
    """Delete all memories for a session (called on refresh/session end)"""
    try:
        agent_service = AgentService(db)
        if not agent_service.memory_service.is_enabled():
            return MemoryResponse(success=False, message="Memory service not enabled.")
        
        success = agent_service.memory_service.delete_session_memories(session_id=session_id)
        
        if success:
            return MemoryResponse(success=True, message=f"Session memories deleted successfully for {session_id}")
        else:
            return MemoryResponse(success=False, message="Failed to delete session memories")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/memory/session/{session_id}", response_model=MemoryResponse)
async def delete_session_memories_post(session_id: str, db: Session = Depends(get_db)):
    """Delete all memories for a session (supports POST for navigator.sendBeacon)."""
    try:
        agent_service = AgentService(db)
        if not agent_service.memory_service.is_enabled():
            return MemoryResponse(success=False, message="Memory service not enabled.")

        success = agent_service.memory_service.delete_session_memories(session_id=session_id)

        if success:
            return MemoryResponse(success=True, message=f"Session memories deleted successfully for {session_id}")
        else:
            return MemoryResponse(success=False, message="Failed to delete session memories")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Tools endpoints
@router.get("/tools/available")
async def get_available_tools():
    """Get information about available tools"""
    try:
        return ToolsService.get_available_tools_info()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from typing import List
from sqlalchemy.orm import Session

from schemas.agent import AgentCreate, AgentInDB, AgentExecutionRequest, AgentExecutionResponse, AgentChatRequest
from services.agent_service import AgentService
from core.database import get_db
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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
    max_iterations: int
    streaming_enabled: bool
    human_in_loop: bool
    recursion_limit: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

router = APIRouter()

@router.post("/", response_model=AgentResponse)
async def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """Create a new LangGraph agent"""
    try:
        agent_service = AgentService(db)
        agent = await agent_service.create_agent(agent_data)
        # Convert AgentInDB to AgentResponse to exclude sensitive fields
        return AgentResponse(**agent.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get agent configuration by ID"""
    try:
        agent_service = AgentService(db)
        agent = await agent_service.get_agent(agent_id)
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
        agent_service = AgentService(db)
        agents = await agent_service.get_agents()
        # Convert AgentInDB to AgentResponse to exclude sensitive fields
        return [AgentResponse(**agent.model_dump()) for agent in agents]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """Delete an agent"""
    try:
        agent_service = AgentService(db)
        success = await agent_service.delete_agent(agent_id)
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
        response = await agent_service.chat_with_agent(agent_id, request.message)
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
    """WebSocket endpoint for streaming agent responses"""
    try:
        await websocket.accept()
        agent_service = AgentService(db)
        await agent_service.stream_agent(websocket, agent_id)
    except Exception as e:
        try:
            # Check if websocket is still connected before trying to close
            if not websocket.client_state.name == "DISCONNECTED":
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
"""
A2A Protocol API Endpoints
Agent-to-Agent communication endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import logging

from core.database import get_db
from services.a2a_protocol import (
    A2AProtocol, AgentCard, A2ARequest, A2AResponse,
    a2a_registry, A2AMethod
)
from services.agent_service import AgentService
from models.agent import Agent

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/{agent_id}/a2a")
async def handle_a2a_request(
    agent_id: str,
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Handle incoming A2A Protocol request"""
    try:
        # Get agent
        agent_service = AgentService(db)
        agent = await agent_service.get_agent(agent_id)
        if not agent:
            return A2AResponse.error_response(
                request.get("id", ""),
                -32000,
                "Agent not found",
                f"Agent {agent_id} not found"
            ).to_dict()
        
        # Get or create A2A protocol instance
        protocol = a2a_registry.get_protocol(agent_id)
        if not protocol:
            # Create agent card
            agent_card = AgentCard(
                agent_id=agent.agent_id,
                name=agent.name,
                version="1.0.0",
                description=agent.system_prompt or f"Agent: {agent.name}",
                capabilities=agent.tools or [],
                endpoint=f"/api/v1/a2a/{agent_id}/a2a",
                metadata={
                    "agent_type": agent.agent_type,
                    "llm_provider": agent.llm_provider,
                    "llm_model": agent.llm_model
                }
            )
            
            # Create protocol instance
            protocol = A2AProtocol(agent_id, agent_card)
            
            # Register handler for task execution
            def handle_execute_task(params: Dict[str, Any]) -> Dict[str, Any]:
                task = params.get("task", {})
                input_text = task.get("input", "")
                
                # Execute agent (synchronous wrapper)
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                response = loop.run_until_complete(
                    agent_service.execute_agent(agent_id, input_text)
                )
                
                return {
                    "task_id": task.get("task_id", ""),
                    "status": "completed",
                    "result": response
                }
            
            protocol.register_handler(A2AMethod.EXECUTE_TASK, handle_execute_task)
            
            # Register in registry
            a2a_registry.register_agent(agent_card, protocol)
        
        # Handle request
        response = protocol.handle_request(request)
        return response.to_dict()
    
    except Exception as e:
        logger.error(f"Error handling A2A request: {e}")
        return A2AResponse.error_response(
            request.get("id", ""),
            -32603,
            "Internal error",
            str(e)
        ).to_dict()


@router.get("/{agent_id}/agent-card")
async def get_agent_card(
    agent_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get Agent Card for an agent"""
    try:
        agent_service = AgentService(db)
        agent = await agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get or create agent card
        agent_card = a2a_registry.get_agent_card(agent_id)
        if not agent_card:
            agent_card = AgentCard(
                agent_id=agent.agent_id,
                name=agent.name,
                version="1.0.0",
                description=agent.system_prompt or f"Agent: {agent.name}",
                capabilities=agent.tools or [],
                endpoint=f"/api/v1/a2a/{agent_id}/a2a",
                metadata={
                    "agent_type": agent.agent_type,
                    "llm_provider": agent.llm_provider,
                    "llm_model": agent.llm_model
                }
            )
        
        return agent_card.to_dict()
    
    except Exception as e:
        logger.error(f"Error getting agent card: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/discover")
async def discover_agents(
    capabilities: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Discover available agents"""
    try:
        agent_service = AgentService(db)
        agents = await agent_service.get_agents()
        
        # Filter by capabilities if provided
        capability_list = capabilities.split(",") if capabilities else None
        
        agent_cards = []
        for agent in agents:
            agent_card = AgentCard(
                agent_id=agent.agent_id,
                name=agent.name,
                version="1.0.0",
                description=agent.system_prompt or f"Agent: {agent.name}",
                capabilities=agent.tools or [],
                endpoint=f"/api/v1/a2a/{agent.agent_id}/a2a",
                metadata={
                    "agent_type": agent.agent_type,
                    "llm_provider": agent.llm_provider,
                    "llm_model": agent.llm_model
                }
            )
            
            # Filter by capabilities
            if capability_list:
                if any(cap in agent_card.capabilities for cap in capability_list):
                    agent_cards.append(agent_card.to_dict())
            else:
                agent_cards.append(agent_card.to_dict())
        
        return {
            "agents": agent_cards,
            "count": len(agent_cards)
        }
    
    except Exception as e:
        logger.error(f"Error discovering agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/execute-task")
async def execute_task_on_agent(
    agent_id: str,
    task: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Execute a task on an agent via A2A Protocol"""
    try:
        agent_service = AgentService(db)
        agent = await agent_service.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get or create protocol
        protocol = a2a_registry.get_protocol(agent_id)
        if not protocol:
            agent_card = AgentCard(
                agent_id=agent.agent_id,
                name=agent.name,
                version="1.0.0",
                description=agent.system_prompt or f"Agent: {agent.name}",
                capabilities=agent.tools or [],
                endpoint=f"/api/v1/a2a/{agent_id}/a2a",
                metadata={
                    "agent_type": agent.agent_type,
                    "llm_provider": agent.llm_provider,
                    "llm_model": agent.llm_model
                }
            )
            protocol = A2AProtocol(agent_id, agent_card)
            a2a_registry.register_agent(agent_card, protocol)
        
        # Execute task
        input_text = task.get("input", "")
        response = await agent_service.execute_agent(agent_id, input_text)
        
        return {
            "task_id": task.get("task_id", ""),
            "status": "completed",
            "result": response
        }
    
    except Exception as e:
        logger.error(f"Error executing task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


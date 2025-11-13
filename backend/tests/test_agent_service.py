"""
Unit tests for AgentService
"""
import pytest
from services.agent_service import AgentService
from schemas.agent import AgentCreate


@pytest.mark.asyncio
async def test_create_agent(db_session, test_tenant):
    """Test creating an agent"""
    agent_service = AgentService(db_session)
    
    agent_data = AgentCreate(
        name="Test Agent",
        agent_type="react",
        llm_provider="openai",
        llm_model="gpt-3.5-turbo",
        temperature=0.7,
        system_prompt="You are a helpful assistant",
        tools=[],
        max_iterations=10,
        recursion_limit=25
    )
    
    agent = await agent_service.create_agent(agent_data)
    
    assert agent is not None
    assert agent.name == "Test Agent"
    assert agent.agent_type == "react"
    assert agent.llm_provider == "openai"
    assert agent.version == 1  # Initial version


@pytest.mark.asyncio
async def test_get_agent(db_session, test_agent):
    """Test retrieving an agent"""
    agent_service = AgentService(db_session)
    
    agent = await agent_service.get_agent(test_agent.agent_id)
    
    assert agent is not None
    assert agent.agent_id == test_agent.agent_id
    assert agent.name == test_agent.name


@pytest.mark.asyncio
async def test_get_agent_not_found(db_session):
    """Test retrieving a non-existent agent"""
    agent_service = AgentService(db_session)
    
    agent = await agent_service.get_agent("non-existent-id")
    
    assert agent is None


@pytest.mark.asyncio
async def test_get_agents(db_session, test_agent):
    """Test retrieving all agents"""
    agent_service = AgentService(db_session)
    
    agents = await agent_service.get_agents()
    
    assert len(agents) >= 1
    assert any(a.agent_id == test_agent.agent_id for a in agents)


@pytest.mark.asyncio
async def test_delete_agent(db_session, test_agent):
    """Test deleting an agent"""
    agent_service = AgentService(db_session)
    
    success = await agent_service.delete_agent(test_agent.agent_id)
    
    assert success is True
    
    # Verify agent is deleted
    agent = await agent_service.get_agent(test_agent.agent_id)
    assert agent is None


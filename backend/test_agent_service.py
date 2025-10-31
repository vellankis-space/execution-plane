import asyncio
from sqlalchemy.orm import Session
from core.database import get_db, init_db
from services.agent_service import AgentService
from schemas.agent import AgentCreate

async def test_agent_service():
    print("Testing Agent Service...")
    
    # Initialize database
    await init_db()
    print("Database initialized")
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    # Create agent service
    agent_service = AgentService(db)
    
    # Create test agent
    agent_data = AgentCreate(
        name="Test Agent",
        agent_type="react",
        llm_provider="openai",
        llm_model="gpt-3.5-turbo",
        api_key="test-key",
        temperature=0.7,
        system_prompt="You are a helpful assistant",
        tools=["tavily_search"],
        max_iterations=15,
        streaming_enabled=True,
        human_in_loop=False,
        recursion_limit=25
    )
    
    print("Creating agent...")
    agent = await agent_service.create_agent(agent_data)
    print(f"Agent created: {agent}")
    
    # Retrieve agent
    print("Retrieving agent...")
    retrieved_agent = await agent_service.get_agent(agent.agent_id)
    print(f"Agent retrieved: {retrieved_agent}")

if __name__ == "__main__":
    asyncio.run(test_agent_service())
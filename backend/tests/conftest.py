"""
Pytest configuration and fixtures
"""
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.database import Base, get_db
from models.agent import Agent
from models.workflow import Workflow
from models.user import User, Tenant


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop tables
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def test_tenant(db_session):
    """Create a test tenant"""
    tenant = Tenant(
        tenant_id="test-tenant-1",
        name="Test Tenant",
        is_active=True
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture(scope="function")
def test_user(db_session, test_tenant):
    """Create a test user"""
    from services.auth_service import AuthService
    
    auth_service = AuthService(db_session)
    user = auth_service.create_user(
        username="testuser",
        email="test@example.com",
        password="testpassword123",
        tenant_id=test_tenant.tenant_id
    )
    return user


@pytest.fixture(scope="function")
def test_agent(db_session, test_tenant):
    """Create a test agent"""
    agent = Agent(
        agent_id="test-agent-1",
        name="Test Agent",
        agent_type="react",
        llm_provider="openai",
        llm_model="gpt-3.5-turbo",
        temperature=0.7,
        system_prompt="You are a test agent",
        tools=[],
        max_iterations=10,
        recursion_limit=25
    )
    db_session.add(agent)
    db_session.commit()
    db_session.refresh(agent)
    return agent


@pytest.fixture(scope="function")
def test_workflow(db_session, test_tenant):
    """Create a test workflow"""
    workflow = Workflow(
        workflow_id="test-workflow-1",
        name="Test Workflow",
        description="A test workflow",
        definition={
            "steps": [
                {
                    "id": "step1",
                    "agent_id": "test-agent-1",
                    "input": "{{input}}"
                }
            ]
        }
    )
    db_session.add(workflow)
    db_session.commit()
    db_session.refresh(workflow)
    return workflow


@pytest.fixture(scope="function")
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, Float
from sqlalchemy.sql import func
from core.database import Base

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    agent_type = Column(String)  # react, plan-execute, reflection, custom
    llm_provider = Column(String)  # openai, anthropic, google, etc.
    llm_model = Column(String)
    temperature = Column(Float)  # Changed from Integer to Float
    system_prompt = Column(Text)
    tools = Column(JSON)  # List of tools
    tool_configs = Column(JSON)  # Tool-specific configurations (API keys, settings)
    max_iterations = Column(Integer)
    memory_type = Column(String)  # memory-saver, postgres, redis, none (deprecated)
    streaming_enabled = Column(Boolean, default=True)
    human_in_loop = Column(Boolean, default=False)
    recursion_limit = Column(Integer)
    api_key_encrypted = Column(String)  # Encrypted user API key
    pii_config = Column(JSON)  # PII configuration: allowed types, custom categories, strategy
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
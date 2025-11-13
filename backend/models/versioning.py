"""
Versioning models for agents and workflows
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, UniqueConstraint
from sqlalchemy.sql import func
from core.database import Base


class AgentVersion(Base):
    """Version history for agents"""
    __tablename__ = "agent_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, index=True, nullable=False)
    version = Column(Integer, nullable=False)
    config_snapshot = Column(JSON, nullable=False)  # Full agent configuration at this version
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String)  # User who created this version
    
    __table_args__ = (
        UniqueConstraint('agent_id', 'version', name='uq_agent_version'),
    )


class WorkflowVersion(Base):
    """Version history for workflows"""
    __tablename__ = "workflow_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String, index=True, nullable=False)
    version = Column(Integer, nullable=False)
    definition_snapshot = Column(JSON, nullable=False)  # Full workflow definition at this version
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String)  # User who created this version
    
    __table_args__ = (
        UniqueConstraint('workflow_id', 'version', name='uq_workflow_version'),
    )


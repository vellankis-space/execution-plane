"""
Human-in-the-loop models
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class ApprovalGate(Base):
    """Approval gate configuration for workflows"""
    __tablename__ = "approval_gates"
    
    id = Column(Integer, primary_key=True, index=True)
    gate_id = Column(String, unique=True, index=True)
    workflow_id = Column(String, ForeignKey("workflows.workflow_id"), nullable=False)
    step_id = Column(String)  # Step in workflow where approval is required
    name = Column(String, nullable=False)
    description = Column(Text)
    approver_type = Column(String, nullable=False)  # user, role, any
    approver_ids = Column(JSON, default=list)  # List of user IDs or role names
    timeout_seconds = Column(Integer)  # Timeout for approval (None for no timeout)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    workflow = relationship("Workflow", backref="approval_gates")
    tasks = relationship("HumanTask", back_populates="approval_gate")


class HumanTask(Base):
    """Human task for approval or input"""
    __tablename__ = "human_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)
    gate_id = Column(String, ForeignKey("approval_gates.gate_id"), nullable=False)
    workflow_id = Column(String, nullable=False)
    execution_id = Column(String, nullable=False)
    step_id = Column(String)
    task_type = Column(String, nullable=False)  # approval, input, review
    title = Column(String, nullable=False)
    description = Column(Text)
    assigned_to = Column(String, index=True)  # User ID assigned to task
    status = Column(String, default="pending")  # pending, in_progress, approved, rejected, expired, cancelled
    input_data = Column(JSON, default=dict)  # Input data for the task
    response_data = Column(JSON)  # Response from human
    response_text = Column(Text)  # Text response
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    assigned_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    metadata = Column(JSON, default=dict)
    
    # Relationship
    approval_gate = relationship("ApprovalGate", back_populates="tasks")
    
    # Composite index for efficient querying
    __table_args__ = (
        Index('idx_human_tasks_status_assigned', 'status', 'assigned_to', 'created_at'),
    )


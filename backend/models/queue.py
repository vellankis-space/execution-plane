"""
Queue management models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text, Float, Index
from sqlalchemy.sql import func
from core.database import Base


class WorkflowQueue(Base):
    """Queue for workflow executions"""
    __tablename__ = "workflow_queues"
    
    id = Column(Integer, primary_key=True, index=True)
    queue_id = Column(String, unique=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    priority_levels = Column(Integer, default=5)  # Number of priority levels (1-5)
    max_concurrent_executions = Column(Integer, default=10)  # Max concurrent executions
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default=dict)  # Queue-specific settings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QueuedExecution(Base):
    """Workflow execution in queue"""
    __tablename__ = "queued_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    queue_item_id = Column(String, unique=True, index=True)
    queue_id = Column(String, ForeignKey("workflow_queues.queue_id"), nullable=False)
    workflow_id = Column(String, nullable=False)
    execution_id = Column(String, unique=True, index=True)  # Reference to WorkflowExecution
    priority = Column(Integer, default=3)  # 1 (highest) to 5 (lowest)
    status = Column(String, default="pending")  # pending, queued, running, completed, failed, cancelled
    input_data = Column(JSON, default=dict)
    scheduled_at = Column(DateTime(timezone=True))  # When to execute (optional)
    queued_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Composite index for efficient queue processing
    __table_args__ = (
        Index('idx_queue_priority_status', 'queue_id', 'priority', 'status', 'queued_at'),
    )


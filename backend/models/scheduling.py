"""
Workflow scheduling models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class WorkflowSchedule(Base):
    """Schedule configuration for workflows"""
    __tablename__ = "workflow_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(String, unique=True, index=True)
    workflow_id = Column(String, ForeignKey("workflows.workflow_id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    cron_expression = Column(String, nullable=False)  # Cron expression for scheduling
    timezone = Column(String, default="UTC")  # Timezone for schedule
    is_active = Column(Boolean, default=True)
    input_data = Column(JSON, default=dict)  # Default input data for scheduled executions
    created_by = Column(String)  # User ID who created the schedule
    next_run_at = Column(DateTime(timezone=True))  # Next scheduled execution time
    last_run_at = Column(DateTime(timezone=True))  # Last execution time
    last_run_status = Column(String)  # Status of last execution: success, failed, skipped
    run_count = Column(Integer, default=0)  # Total number of executions
    max_runs = Column(Integer)  # Maximum number of runs (None for unlimited)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to workflow
    workflow = relationship("Workflow", backref="schedules")


class ScheduledExecution(Base):
    """Record of scheduled workflow executions"""
    __tablename__ = "scheduled_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String, unique=True, index=True)
    schedule_id = Column(String, ForeignKey("workflow_schedules.schedule_id"), nullable=False)
    workflow_id = Column(String, nullable=False)
    workflow_execution_id = Column(String)  # Reference to WorkflowExecution
    scheduled_at = Column(DateTime(timezone=True), nullable=False)  # When it was scheduled to run
    executed_at = Column(DateTime(timezone=True))  # When it actually ran
    status = Column(String, default="pending")  # pending, running, completed, failed, skipped
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to schedule
    schedule = relationship("WorkflowSchedule", backref="executions")


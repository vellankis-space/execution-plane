from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    definition = Column(JSON)  # Workflow definition in JSON format
    created_by = Column(String)  # User ID who created the workflow
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to workflow executions
    executions = relationship("WorkflowExecution", back_populates="workflow")


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String, unique=True, index=True)
    workflow_id = Column(String, ForeignKey("workflows.workflow_id"))
    status = Column(String)  # pending, running, completed, failed, cancelled
    input_data = Column(JSON)  # Input data for the workflow
    output_data = Column(JSON)  # Output data from the workflow
    error_message = Column(Text)  # Error message if failed
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Enhanced monitoring fields
    execution_time = Column(Float)  # Total execution time in seconds
    step_count = Column(Integer)  # Total number of steps
    success_count = Column(Integer)  # Number of successful steps
    failure_count = Column(Integer)  # Number of failed steps
    retry_count = Column(Integer, default=0)  # Number of retries
    resource_usage = Column(JSON)  # Resource usage metrics (CPU, memory, etc.)
    
    # Relationship to workflow
    workflow = relationship("Workflow", back_populates="executions")
    
    # Relationship to step executions
    step_executions = relationship("StepExecution", back_populates="workflow_execution")


class StepExecution(Base):
    __tablename__ = "step_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    step_id = Column(String, index=True)
    execution_id = Column(String, ForeignKey("workflow_executions.execution_id"))
    agent_id = Column(String)  # Agent used in this step
    status = Column(String)  # pending, running, completed, failed
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Enhanced monitoring fields
    execution_time = Column(Float)  # Execution time in seconds
    retry_count = Column(Integer, default=0)  # Number of retries
    memory_usage = Column(Float)  # Memory usage in MB
    cpu_usage = Column(Float)  # CPU usage percentage
    io_operations = Column(Integer)  # Number of I/O operations
    network_requests = Column(Integer)  # Number of network requests
    
    # Relationship to workflow execution
    workflow_execution = relationship("WorkflowExecution", back_populates="step_executions")


class ExecutionLog(Base):
    __tablename__ = "execution_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String, ForeignKey("workflow_executions.execution_id"))
    step_id = Column(String, ForeignKey("step_executions.step_id"), nullable=True)
    log_level = Column(String)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    log_metadata = Column(JSON)  # Additional metadata
    
    # Relationship to workflow execution
    workflow_execution = relationship("WorkflowExecution", back_populates="logs")


# Add relationship to ExecutionLog in WorkflowExecution
WorkflowExecution.logs = relationship("ExecutionLog", back_populates="workflow_execution")
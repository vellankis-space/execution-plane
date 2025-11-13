from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class WorkflowStep(BaseModel):
    id: str
    name: str
    agent_id: str
    description: Optional[str] = ""
    input_mapping: Optional[Dict[str, str]] = None  # Map input fields from context
    position: Optional[Dict[str, float]] = None  # For visualization positioning (x, y coordinates)
    retry_policy: Optional[Dict[str, Any]] = None  # Retry configuration: max_retries, initial_delay, max_delay, exponential_base


class WorkflowDefinition(BaseModel):
    steps: List[WorkflowStep]
    dependencies: Optional[Dict[str, List[str]]] = None  # Step dependencies
    conditions: Optional[Dict[str, Dict[str, Any]]] = None  # Conditional execution rules


class WorkflowVisualizationData(BaseModel):
    """Schema for workflow visualization data"""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    layout: Optional[Dict[str, Any]] = None


class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = ""
    definition: WorkflowDefinition


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowInDB(WorkflowBase):
    workflow_id: str
    created_by: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[WorkflowDefinition] = None
    is_active: Optional[bool] = None


class WorkflowExecutionBase(BaseModel):
    workflow_id: str
    input_data: Optional[Dict[str, Any]] = None


class WorkflowExecutionCreate(WorkflowExecutionBase):
    pass


class WorkflowExecutionInDB(WorkflowExecutionBase):
    execution_id: str
    status: str
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StepExecutionBase(BaseModel):
    step_id: str
    agent_id: str
    input_data: Optional[Dict[str, Any]] = None


class StepExecutionCreate(StepExecutionBase):
    execution_id: str


class StepExecutionInDB(StepExecutionBase):
    id: int
    execution_id: str
    status: str
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowExecutionResponse(WorkflowExecutionInDB):
    step_executions: List[StepExecutionInDB] = []


class WorkflowResponse(WorkflowInDB):
    pass
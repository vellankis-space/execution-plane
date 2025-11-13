from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class WorkflowStep(BaseModel):
    id: str
    name: Optional[str] = None
    type: Optional[str] = "agent"  # Node type: start, end, agent, condition, loop, action, error_handler
    agent_id: Optional[str] = None  # Required only for agent nodes
    description: Optional[str] = ""
    data: Optional[Dict[str, Any]] = None  # Additional node data
    input_mapping: Optional[Dict[str, str]] = None  # Map input fields from context
    position: Optional[Dict[str, float]] = None  # For visualization positioning (x, y coordinates)
    retry_policy: Optional[Dict[str, Any]] = None  # Retry configuration
    condition: Optional[Dict[str, Any]] = None  # For condition nodes
    loop_config: Optional[Dict[str, Any]] = None  # For loop nodes
    action_type: Optional[str] = None  # For action nodes
    action_config: Optional[Dict[str, Any]] = None  # For action nodes


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


# Credential schemas
class CredentialBase(BaseModel):
    name: str
    type: str  # api_key, oauth2, basic_auth, database, smtp, aws
    data: Dict[str, Any]  # Credential data (will be encrypted)


class CredentialCreate(CredentialBase):
    pass


class CredentialUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class CredentialResponse(BaseModel):
    id: str
    name: str
    type: str
    data: Dict[str, Any]  # Sensitive fields will be masked
    createdAt: datetime
    updatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True


# Webhook trigger schemas
class WebhookTriggerCreate(BaseModel):
    workflow_id: str
    name: str
    method: str = "POST"  # GET, POST, PUT
    auth_type: str = "none"  # none, api_key, bearer
    auth_config: Optional[Dict[str, Any]] = None


class WebhookTriggerResponse(BaseModel):
    id: str
    workflow_id: str
    name: str
    webhook_url: str
    method: str
    auth_type: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
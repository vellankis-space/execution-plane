from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    WorkflowExecutionCreate, WorkflowExecutionResponse
)
from services.workflow_service import WorkflowService
from services.langgraph_service import LangGraphWorkflowService
from core.database import get_db
from middleware.tenant_middleware import get_current_tenant_id

router = APIRouter()

@router.post("/", response_model=WorkflowResponse)
async def create_workflow(workflow_data: WorkflowCreate, db: Session = Depends(get_db)):
    """Create a new workflow"""
    try:
        tenant_id = get_current_tenant_id()
        workflow_service = WorkflowService(db)
        workflow = await workflow_service.create_workflow(workflow_data, tenant_id=tenant_id)
        return workflow
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """Get workflow by ID"""
    try:
        tenant_id = get_current_tenant_id()
        workflow_service = WorkflowService(db)
        workflow = await workflow_service.get_workflow(workflow_id, tenant_id=tenant_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return workflow
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[WorkflowResponse])
async def get_workflows(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all workflows"""
    try:
        tenant_id = get_current_tenant_id()
        workflow_service = WorkflowService(db)
        workflows = await workflow_service.get_workflows(skip, limit, tenant_id=tenant_id)
        return workflows
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(workflow_id: str, workflow_data: WorkflowUpdate, db: Session = Depends(get_db)):
    """Update a workflow"""
    try:
        workflow_service = WorkflowService(db)
        workflow = await workflow_service.update_workflow(workflow_id, workflow_data)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return workflow
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """Delete a workflow"""
    try:
        workflow_service = WorkflowService(db)
        success = await workflow_service.delete_workflow(workflow_id)
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return {"message": "Workflow deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(workflow_id: str, execution_data: WorkflowExecutionCreate, db: Session = Depends(get_db)):
    """Execute a workflow"""
    try:
        tenant_id = get_current_tenant_id()
        workflow_service = WorkflowService(db)
        execution = await workflow_service.execute_workflow(workflow_id, execution_data.input_data or {}, tenant_id=tenant_id)
        return execution
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{workflow_id}/executions", response_model=List[WorkflowExecutionResponse])
async def get_workflow_executions(workflow_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all executions for a workflow"""
    try:
        workflow_service = WorkflowService(db)
        executions = await workflow_service.get_workflow_executions(workflow_id, skip=skip, limit=limit)
        return executions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse)
async def get_workflow_execution(execution_id: str, db: Session = Depends(get_db)):
    """Get workflow execution by ID with step executions"""
    try:
        workflow_service = WorkflowService(db)
        execution = await workflow_service.get_workflow_execution_with_steps(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Workflow execution not found")
        return execution
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{workflow_id}/execute-langgraph")
async def execute_workflow_with_langgraph(
    workflow_id: str,
    execution_data: WorkflowExecutionCreate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Execute a workflow using LangGraph state machine.
    
    This endpoint uses LangGraph to execute workflows with:
    - State management
    - Checkpointing
    - Cyclic flows
    - Conditional routing
    - Agent orchestration
    
    Returns the final state including:
    - messages: List of all node executions
    - context: Workflow variables
    - step_results: Results from each step
    - completed_steps: List of completed step IDs
    - failed_steps: List of failed step IDs
    - metadata: Execution metadata
    """
    try:
        # Get workflow
        workflow_service = WorkflowService(db)
        workflow = await workflow_service.get_workflow(workflow_id)
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Execute with LangGraph
        langgraph_service = LangGraphWorkflowService(db)
        final_state = await langgraph_service.execute_langgraph_workflow(
            workflow_definition=workflow.definition,
            input_data=execution_data.input_data or {},
            workflow_name=workflow.name
        )
        
        return {
            "success": final_state["metadata"]["success"],
            "workflow_id": workflow_id,
            "execution_state": final_state,
            "completed_steps": final_state["completed_steps"],
            "failed_steps": final_state["failed_steps"],
            "step_results": final_state["step_results"],
            "messages": final_state["messages"],
            "metadata": final_state["metadata"]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
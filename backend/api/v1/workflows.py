from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    WorkflowExecutionCreate, WorkflowExecutionResponse
)
from services.workflow_service import WorkflowService
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
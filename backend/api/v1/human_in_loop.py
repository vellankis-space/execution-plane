"""
Human-in-the-loop API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from services.human_in_loop_service import HumanInLoopService
from core.database import get_db
from api.v1.auth import get_current_user

router = APIRouter()


# Request/Response models
class ApprovalGateCreate(BaseModel):
    workflow_id: str
    name: str
    approver_type: str  # user, role, any
    approver_ids: List[str]
    step_id: Optional[str] = None
    description: Optional[str] = None
    timeout_seconds: Optional[int] = None
    is_active: bool = True


class HumanTaskCreate(BaseModel):
    gate_id: str
    workflow_id: str
    execution_id: str
    task_type: str  # approval, input, review
    title: str
    description: Optional[str] = None
    step_id: Optional[str] = None
    assigned_to: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    timeout_seconds: Optional[int] = None


class TaskResponse(BaseModel):
    task_id: str
    task_type: str
    title: str
    description: Optional[str]
    status: str
    assigned_to: Optional[str]
    workflow_id: str
    execution_id: str
    created_at: str
    expires_at: Optional[str]

    class Config:
        from_attributes = True


class TaskApprovalRequest(BaseModel):
    response_data: Optional[Dict[str, Any]] = None
    response_text: Optional[str] = None


class TaskRejectionRequest(BaseModel):
    reason: Optional[str] = None


# Approval Gate Endpoints

@router.post("/approval-gates")
async def create_approval_gate(
    gate_data: ApprovalGateCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create an approval gate"""
    try:
        service = HumanInLoopService(db)
        gate = await service.create_approval_gate(
            workflow_id=gate_data.workflow_id,
            name=gate_data.name,
            approver_type=gate_data.approver_type,
            approver_ids=gate_data.approver_ids,
            step_id=gate_data.step_id,
            description=gate_data.description,
            timeout_seconds=gate_data.timeout_seconds,
            is_active=gate_data.is_active
        )
        return {
            "gate_id": gate.gate_id,
            "name": gate.name,
            "is_active": gate.is_active
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/approval-gates/workflow/{workflow_id}")
async def get_workflow_approval_gates(
    workflow_id: str,
    is_active: Optional[bool] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get approval gates for a workflow"""
    try:
        service = HumanInLoopService(db)
        gates = await service.get_workflow_approval_gates(
            workflow_id=workflow_id,
            is_active=is_active
        )
        return [
            {
                "gate_id": gate.gate_id,
                "name": gate.name,
                "description": gate.description,
                "approver_type": gate.approver_type,
                "approver_ids": gate.approver_ids or [],
                "step_id": gate.step_id,
                "timeout_seconds": gate.timeout_seconds,
                "is_active": gate.is_active
            }
            for gate in gates
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Human Task Endpoints

@router.post("/tasks", response_model=TaskResponse)
async def create_human_task(
    task_data: HumanTaskCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a human task"""
    try:
        service = HumanInLoopService(db)
        task = await service.create_human_task(
            gate_id=task_data.gate_id,
            workflow_id=task_data.workflow_id,
            execution_id=task_data.execution_id,
            task_type=task_data.task_type,
            title=task_data.title,
            description=task_data.description,
            step_id=task_data.step_id,
            assigned_to=task_data.assigned_to,
            input_data=task_data.input_data,
            timeout_seconds=task_data.timeout_seconds
        )
        return TaskResponse(
            task_id=task.task_id,
            task_type=task.task_type,
            title=task.title,
            description=task.description,
            status=task.status,
            assigned_to=task.assigned_to,
            workflow_id=task.workflow_id,
            execution_id=task.execution_id,
            created_at=task.created_at.isoformat() if task.created_at else "",
            expires_at=task.expires_at.isoformat() if task.expires_at else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/my-tasks", response_model=List[TaskResponse])
async def get_my_tasks(
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tasks assigned to current user"""
    try:
        service = HumanInLoopService(db)
        tasks = await service.get_user_tasks(
            user_id=current_user.user_id,
            status=status,
            task_type=task_type,
            limit=limit
        )
        return [
            TaskResponse(
                task_id=task.task_id,
                task_type=task.task_type,
                title=task.title,
                description=task.description,
                status=task.status,
                assigned_to=task.assigned_to,
                workflow_id=task.workflow_id,
                execution_id=task.execution_id,
                created_at=task.created_at.isoformat() if task.created_at else "",
                expires_at=task.expires_at.isoformat() if task.expires_at else None
            )
            for task in tasks
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/execution/{execution_id}", response_model=List[TaskResponse])
async def get_execution_tasks(
    execution_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tasks for a workflow execution"""
    try:
        service = HumanInLoopService(db)
        tasks = await service.get_execution_tasks(execution_id)
        return [
            TaskResponse(
                task_id=task.task_id,
                task_type=task.task_type,
                title=task.title,
                description=task.description,
                status=task.status,
                assigned_to=task.assigned_to,
                workflow_id=task.workflow_id,
                execution_id=task.execution_id,
                created_at=task.created_at.isoformat() if task.created_at else "",
                expires_at=task.expires_at.isoformat() if task.expires_at else None
            )
            for task in tasks
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/approve")
async def approve_task(
    task_id: str,
    approval_data: TaskApprovalRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a human task"""
    try:
        service = HumanInLoopService(db)
        task = await service.approve_task(
            task_id=task_id,
            user_id=current_user.user_id,
            response_data=approval_data.response_data,
            response_text=approval_data.response_text
        )
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task approved successfully", "task_id": task.task_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/reject")
async def reject_task(
    task_id: str,
    rejection_data: TaskRejectionRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a human task"""
    try:
        service = HumanInLoopService(db)
        task = await service.reject_task(
            task_id=task_id,
            user_id=current_user.user_id,
            reason=rejection_data.reason
        )
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task rejected", "task_id": task.task_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/assign")
async def assign_task(
    task_id: str,
    user_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign a task to a user"""
    try:
        service = HumanInLoopService(db)
        task = await service.assign_task(task_id, user_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task assigned successfully", "task_id": task.task_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


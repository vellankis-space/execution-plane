"""
Human-in-the-loop service
"""
import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from models.human_in_loop import ApprovalGate, HumanTask
from services.workflow_service import WorkflowService

logger = logging.getLogger(__name__)


class HumanInLoopService:
    """Service for managing human-in-the-loop tasks"""
    
    def __init__(self, db: Session):
        self.db = db
        self.workflow_service = WorkflowService(db)
    
    # Approval Gate Management
    
    async def create_approval_gate(
        self,
        workflow_id: str,
        name: str,
        approver_type: str,
        approver_ids: List[str],
        step_id: Optional[str] = None,
        description: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        is_active: bool = True
    ) -> ApprovalGate:
        """Create an approval gate"""
        gate_id = str(uuid.uuid4())
        
        gate = ApprovalGate(
            gate_id=gate_id,
            workflow_id=workflow_id,
            step_id=step_id,
            name=name,
            description=description,
            approver_type=approver_type,
            approver_ids=approver_ids,
            timeout_seconds=timeout_seconds,
            is_active=is_active
        )
        
        self.db.add(gate)
        self.db.commit()
        self.db.refresh(gate)
        
        return gate
    
    async def get_approval_gate(self, gate_id: str) -> Optional[ApprovalGate]:
        """Get an approval gate by ID"""
        return self.db.query(ApprovalGate).filter(
            ApprovalGate.gate_id == gate_id
        ).first()
    
    async def get_workflow_approval_gates(
        self,
        workflow_id: str,
        is_active: Optional[bool] = None
    ) -> List[ApprovalGate]:
        """Get approval gates for a workflow"""
        query = self.db.query(ApprovalGate).filter(
            ApprovalGate.workflow_id == workflow_id
        )
        
        if is_active is not None:
            query = query.filter(ApprovalGate.is_active == is_active)
        
        return query.all()
    
    # Human Task Management
    
    async def create_human_task(
        self,
        gate_id: str,
        workflow_id: str,
        execution_id: str,
        task_type: str,
        title: str,
        description: Optional[str] = None,
        step_id: Optional[str] = None,
        assigned_to: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> HumanTask:
        """Create a human task"""
        gate = await self.get_approval_gate(gate_id)
        if not gate:
            raise ValueError(f"Approval gate {gate_id} not found")
        
        task_id = str(uuid.uuid4())
        
        # Determine assignee if not provided
        if not assigned_to and gate.approver_type == "user" and gate.approver_ids:
            # Assign to first approver (could be enhanced with round-robin)
            assigned_to = gate.approver_ids[0]
        
        expires_at = None
        if timeout_seconds:
            expires_at = datetime.utcnow() + timedelta(seconds=timeout_seconds)
        elif gate.timeout_seconds:
            expires_at = datetime.utcnow() + timedelta(seconds=gate.timeout_seconds)
        
        task = HumanTask(
            task_id=task_id,
            gate_id=gate_id,
            workflow_id=workflow_id,
            execution_id=execution_id,
            step_id=step_id,
            task_type=task_type,
            title=title,
            description=description,
            assigned_to=assigned_to,
            input_data=input_data or {},
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    async def get_human_task(self, task_id: str) -> Optional[HumanTask]:
        """Get a human task by ID"""
        return self.db.query(HumanTask).filter(
            HumanTask.task_id == task_id
        ).first()
    
    async def get_user_tasks(
        self,
        user_id: str,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        limit: int = 100
    ) -> List[HumanTask]:
        """Get tasks assigned to a user"""
        query = self.db.query(HumanTask).filter(
            HumanTask.assigned_to == user_id
        )
        
        if status:
            query = query.filter(HumanTask.status == status)
        
        if task_type:
            query = query.filter(HumanTask.task_type == task_type)
        
        return query.order_by(desc(HumanTask.created_at)).limit(limit).all()
    
    async def get_execution_tasks(
        self,
        execution_id: str
    ) -> List[HumanTask]:
        """Get all tasks for a workflow execution"""
        return self.db.query(HumanTask).filter(
            HumanTask.execution_id == execution_id
        ).order_by(HumanTask.created_at).all()
    
    async def approve_task(
        self,
        task_id: str,
        user_id: str,
        response_data: Optional[Dict[str, Any]] = None,
        response_text: Optional[str] = None
    ) -> Optional[HumanTask]:
        """Approve a human task"""
        task = await self.get_human_task(task_id)
        if not task:
            return None
        
        # Check if user can approve
        gate = await self.get_approval_gate(task.gate_id)
        if not self._can_user_approve(gate, user_id):
            raise ValueError("User is not authorized to approve this task")
        
        if task.status not in ["pending", "in_progress"]:
            raise ValueError(f"Task cannot be approved in status: {task.status}")
        
        task.status = "approved"
        task.response_data = response_data
        task.response_text = response_text
        task.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        
        # Resume workflow execution
        await self._resume_workflow_execution(task)
        
        return task
    
    async def reject_task(
        self,
        task_id: str,
        user_id: str,
        reason: Optional[str] = None
    ) -> Optional[HumanTask]:
        """Reject a human task"""
        task = await self.get_human_task(task_id)
        if not task:
            return None
        
        # Check if user can reject
        gate = await self.get_approval_gate(task.gate_id)
        if not self._can_user_approve(gate, user_id):
            raise ValueError("User is not authorized to reject this task")
        
        if task.status not in ["pending", "in_progress"]:
            raise ValueError(f"Task cannot be rejected in status: {task.status}")
        
        task.status = "rejected"
        task.response_text = reason
        task.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        
        # Handle workflow execution failure
        await self._handle_workflow_rejection(task)
        
        return task
    
    async def assign_task(
        self,
        task_id: str,
        user_id: str
    ) -> Optional[HumanTask]:
        """Assign a task to a user"""
        task = await self.get_human_task(task_id)
        if not task:
            return None
        
        task.assigned_to = user_id
        task.assigned_at = datetime.utcnow()
        task.status = "in_progress"
        
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def _can_user_approve(self, gate: ApprovalGate, user_id: str) -> bool:
        """Check if user can approve a gate"""
        if gate.approver_type == "any":
            return True
        
        if gate.approver_type == "user":
            return user_id in (gate.approver_ids or [])
        
        if gate.approver_type == "role":
            # Check if user has one of the required roles
            # This would need user role lookup
            return True  # Simplified for now
        
        return False
    
    async def _resume_workflow_execution(self, task: HumanTask):
        """Resume workflow execution after approval"""
        try:
            # Get workflow execution
            execution = await self.workflow_service.get_workflow_execution(task.execution_id)
            if not execution:
                logger.warning(f"Workflow execution {task.execution_id} not found")
                return
            
            # If workflow is paused, resume it
            # This would integrate with workflow service to resume execution
            logger.info(f"Resuming workflow execution {task.execution_id} after approval")
        except Exception as e:
            logger.error(f"Error resuming workflow execution: {str(e)}")
    
    async def _handle_workflow_rejection(self, task: HumanTask):
        """Handle workflow rejection"""
        try:
            # Update workflow execution status
            execution = await self.workflow_service.get_workflow_execution(task.execution_id)
            if execution:
                # Mark execution as failed due to rejection
                await self.workflow_service.update_workflow_execution_status(
                    task.execution_id,
                    "failed",
                    error_message=f"Rejected by {task.assigned_to}: {task.response_text}"
                )
        except Exception as e:
            logger.error(f"Error handling workflow rejection: {str(e)}")
    
    async def check_expired_tasks(self):
        """Check and expire tasks that have timed out"""
        now = datetime.utcnow()
        expired_tasks = self.db.query(HumanTask).filter(
            and_(
                HumanTask.status.in_(["pending", "in_progress"]),
                HumanTask.expires_at.isnot(None),
                HumanTask.expires_at <= now
            )
        ).all()
        
        for task in expired_tasks:
            task.status = "expired"
            task.completed_at = now
            logger.info(f"Task {task.task_id} expired")
        
        self.db.commit()
        return len(expired_tasks)


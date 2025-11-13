"""
Queue management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from services.queue_service import QueueService
from core.database import get_db
from api.v1.auth import get_current_user

router = APIRouter()


# Request/Response models
class QueueCreate(BaseModel):
    name: str
    description: Optional[str] = None
    priority_levels: int = 5
    max_concurrent_executions: int = 10
    settings: Optional[Dict[str, Any]] = None


class EnqueueRequest(BaseModel):
    workflow_id: str
    input_data: Optional[Dict[str, Any]] = None
    priority: int = 3
    scheduled_at: Optional[datetime] = None
    max_retries: int = 3
    metadata: Optional[Dict[str, Any]] = None


# Queue Endpoints

@router.post("/queues")
async def create_queue(
    queue_data: QueueCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workflow queue"""
    try:
        queue_service = QueueService(db)
        queue = await queue_service.create_queue(
            name=queue_data.name,
            description=queue_data.description,
            priority_levels=queue_data.priority_levels,
            max_concurrent_executions=queue_data.max_concurrent_executions,
            settings=queue_data.settings
        )
        return {
            "queue_id": queue.queue_id,
            "name": queue.name,
            "is_active": queue.is_active
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queues")
async def get_queues(
    is_active: Optional[bool] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all queues"""
    try:
        queue_service = QueueService(db)
        queues = await queue_service.get_queues(is_active=is_active)
        return [
            {
                "queue_id": queue.queue_id,
                "name": queue.name,
                "description": queue.description,
                "priority_levels": queue.priority_levels,
                "max_concurrent_executions": queue.max_concurrent_executions,
                "is_active": queue.is_active
            }
            for queue in queues
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queues/{queue_id}/status")
async def get_queue_status(
    queue_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get queue status and statistics"""
    try:
        queue_service = QueueService(db)
        status = await queue_service.get_queue_status(queue_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/queues/{queue_id}/enqueue")
async def enqueue_workflow(
    queue_id: str,
    enqueue_data: EnqueueRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a workflow to the queue"""
    try:
        queue_service = QueueService(db)
        queued_item = await queue_service.enqueue_workflow(
            queue_id=queue_id,
            workflow_id=enqueue_data.workflow_id,
            input_data=enqueue_data.input_data,
            priority=enqueue_data.priority,
            scheduled_at=enqueue_data.scheduled_at,
            max_retries=enqueue_data.max_retries,
            metadata=enqueue_data.metadata
        )
        return {
            "queue_item_id": queued_item.queue_item_id,
            "execution_id": queued_item.execution_id,
            "status": queued_item.status,
            "priority": queued_item.priority
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queues/{queue_id}/items")
async def get_queue_items(
    queue_id: str,
    status: Optional[str] = None,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get items in a queue"""
    try:
        queue_service = QueueService(db)
        items = await queue_service.get_queue_items(
            queue_id=queue_id,
            status=status,
            limit=limit
        )
        return [
            {
                "queue_item_id": item.queue_item_id,
                "workflow_id": item.workflow_id,
                "execution_id": item.execution_id,
                "priority": item.priority,
                "status": item.status,
                "queued_at": item.queued_at.isoformat() if item.queued_at else None,
                "started_at": item.started_at.isoformat() if item.started_at else None,
                "completed_at": item.completed_at.isoformat() if item.completed_at else None,
                "retry_count": item.retry_count,
            }
            for item in items
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/queues/{queue_id}/items/{queue_item_id}/cancel")
async def cancel_queue_item(
    queue_id: str,
    queue_item_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a queued execution"""
    try:
        queue_service = QueueService(db)
        success = await queue_service.cancel_queue_item(queue_item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Queue item not found or cannot be cancelled")
        return {"message": "Queue item cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queues/{queue_id}/analytics")
async def get_queue_analytics(
    queue_id: str,
    days: int = 7,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get queue analytics"""
    try:
        queue_service = QueueService(db)
        analytics = await queue_service.get_queue_analytics(queue_id, days=days)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


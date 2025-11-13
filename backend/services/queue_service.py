"""
Queue management service for workflow execution queuing
"""
import uuid
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, asc
from collections import defaultdict

from models.queue import WorkflowQueue, QueuedExecution
from services.workflow_service import WorkflowService

logger = logging.getLogger(__name__)


class QueueService:
    """Service for managing workflow execution queues"""
    
    def __init__(self, db: Session):
        self.db = db
        self.workflow_service = WorkflowService(db)
        self.active_workers = {}  # Track active workers per queue
    
    # Queue Management
    
    async def create_queue(
        self,
        name: str,
        description: Optional[str] = None,
        priority_levels: int = 5,
        max_concurrent_executions: int = 10,
        settings: Optional[Dict[str, Any]] = None
    ) -> WorkflowQueue:
        """Create a new workflow queue"""
        queue_id = str(uuid.uuid4())
        
        queue = WorkflowQueue(
            queue_id=queue_id,
            name=name,
            description=description,
            priority_levels=priority_levels,
            max_concurrent_executions=max_concurrent_executions,
            settings=settings or {},
            is_active=True
        )
        
        self.db.add(queue)
        self.db.commit()
        self.db.refresh(queue)
        
        return queue
    
    async def get_queue(self, queue_id: str) -> Optional[WorkflowQueue]:
        """Get a queue by ID"""
        return self.db.query(WorkflowQueue).filter(
            WorkflowQueue.queue_id == queue_id
        ).first()
    
    async def get_queue_by_name(self, name: str) -> Optional[WorkflowQueue]:
        """Get a queue by name"""
        return self.db.query(WorkflowQueue).filter(
            WorkflowQueue.name == name
        ).first()
    
    async def get_queues(self, is_active: Optional[bool] = None) -> List[WorkflowQueue]:
        """Get all queues"""
        query = self.db.query(WorkflowQueue)
        if is_active is not None:
            query = query.filter(WorkflowQueue.is_active == is_active)
        return query.all()
    
    # Queue Item Management
    
    async def enqueue_workflow(
        self,
        queue_id: str,
        workflow_id: str,
        input_data: Optional[Dict[str, Any]] = None,
        priority: int = 3,
        scheduled_at: Optional[datetime] = None,
        max_retries: int = 3,
        metadata: Optional[Dict[str, Any]] = None
    ) -> QueuedExecution:
        """Add a workflow execution to the queue"""
        queue = await self.get_queue(queue_id)
        if not queue:
            raise ValueError(f"Queue {queue_id} not found")
        
        if not queue.is_active:
            raise ValueError(f"Queue {queue_id} is not active")
        
        # Validate priority
        if priority < 1 or priority > queue.priority_levels:
            raise ValueError(f"Priority must be between 1 and {queue.priority_levels}")
        
        queue_item_id = str(uuid.uuid4())
        execution_id = str(uuid.uuid4())
        
        queued_execution = QueuedExecution(
            queue_item_id=queue_item_id,
            queue_id=queue_id,
            workflow_id=workflow_id,
            execution_id=execution_id,
            priority=priority,
            status="pending",
            input_data=input_data or {},
            scheduled_at=scheduled_at,
            max_retries=max_retries,
            metadata=metadata or {}
        )
        
        self.db.add(queued_execution)
        self.db.commit()
        self.db.refresh(queued_execution)
        
        # Start processing if queue has capacity
        await self._process_queue(queue_id)
        
        return queued_execution
    
    async def dequeue_workflow(self, queue_id: str) -> Optional[QueuedExecution]:
        """Get the next workflow from the queue"""
        queue = await self.get_queue(queue_id)
        if not queue or not queue.is_active:
            return None
        
        # Check if queue has capacity
        running_count = self.db.query(QueuedExecution).filter(
            and_(
                QueuedExecution.queue_id == queue_id,
                QueuedExecution.status == "running"
            )
        ).count()
        
        if running_count >= queue.max_concurrent_executions:
            return None
        
        # Get next item: highest priority, oldest first, not scheduled for future
        now = datetime.utcnow()
        queued_item = self.db.query(QueuedExecution).filter(
            and_(
                QueuedExecution.queue_id == queue_id,
                QueuedExecution.status == "pending",
                or_(
                    QueuedExecution.scheduled_at.is_(None),
                    QueuedExecution.scheduled_at <= now
                )
            )
        ).order_by(
            asc(QueuedExecution.priority),  # Lower number = higher priority
            asc(QueuedExecution.queued_at)
        ).first()
        
        if queued_item:
            queued_item.status = "queued"
            self.db.commit()
            self.db.refresh(queued_item)
        
        return queued_item
    
    async def _process_queue(self, queue_id: str):
        """Process items in a queue"""
        queue = await self.get_queue(queue_id)
        if not queue or not queue.is_active:
            return
        
        # Get running count
        running_count = self.db.query(QueuedExecution).filter(
            and_(
                QueuedExecution.queue_id == queue_id,
                QueuedExecution.status == "running"
            )
        ).count()
        
        # Process items up to max concurrent
        while running_count < queue.max_concurrent_executions:
            item = await self.dequeue_workflow(queue_id)
            if not item:
                break
            
            # Execute in background
            asyncio.create_task(self._execute_queued_workflow(item))
            running_count += 1
    
    async def _execute_queued_workflow(self, queued_item: QueuedExecution):
        """Execute a queued workflow"""
        queued_item.status = "running"
        queued_item.started_at = datetime.utcnow()
        self.db.commit()
        
        try:
            # Execute the workflow
            workflow_execution = await self.workflow_service.execute_workflow(
                queued_item.workflow_id,
                input_data=queued_item.input_data
            )
            
            # Update queued execution
            queued_item.execution_id = workflow_execution.execution_id
            queued_item.status = "completed"
            queued_item.completed_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error executing queued workflow {queued_item.queue_item_id}: {str(e)}")
            
            # Retry logic
            if queued_item.retry_count < queued_item.max_retries:
                queued_item.retry_count += 1
                queued_item.status = "pending"
                queued_item.error_message = str(e)
                # Re-queue with lower priority
                queued_item.priority = min(queued_item.priority + 1, 5)
            else:
                queued_item.status = "failed"
                queued_item.error_message = str(e)
                queued_item.completed_at = datetime.utcnow()
        
        self.db.commit()
        
        # Process next item in queue
        await self._process_queue(queued_item.queue_id)
    
    async def get_queue_status(self, queue_id: str) -> Dict[str, Any]:
        """Get queue status and statistics"""
        queue = await self.get_queue(queue_id)
        if not queue:
            raise ValueError(f"Queue {queue_id} not found")
        
        # Count items by status
        status_counts = {}
        for status in ["pending", "queued", "running", "completed", "failed", "cancelled"]:
            count = self.db.query(QueuedExecution).filter(
                and_(
                    QueuedExecution.queue_id == queue_id,
                    QueuedExecution.status == status
                )
            ).count()
            status_counts[status] = count
        
        # Average wait time
        completed_items = self.db.query(QueuedExecution).filter(
            and_(
                QueuedExecution.queue_id == queue_id,
                QueuedExecution.status == "completed",
                QueuedExecution.started_at.isnot(None),
                QueuedExecution.queued_at.isnot(None)
            )
        ).all()
        
        avg_wait_time = 0
        if completed_items:
            total_wait = sum(
                (item.started_at - item.queued_at).total_seconds()
                for item in completed_items
                if item.started_at and item.queued_at
            )
            avg_wait_time = total_wait / len(completed_items)
        
        # Items by priority
        priority_counts = {}
        for priority in range(1, queue.priority_levels + 1):
            count = self.db.query(QueuedExecution).filter(
                and_(
                    QueuedExecution.queue_id == queue_id,
                    QueuedExecution.status.in_(["pending", "queued", "running"]),
                    QueuedExecution.priority == priority
                )
            ).count()
            priority_counts[priority] = count
        
        return {
            "queue_id": queue_id,
            "name": queue.name,
            "is_active": queue.is_active,
            "max_concurrent_executions": queue.max_concurrent_executions,
            "status_counts": status_counts,
            "average_wait_time_seconds": round(avg_wait_time, 2),
            "priority_counts": priority_counts,
            "current_running": status_counts.get("running", 0),
            "queue_length": status_counts.get("pending", 0) + status_counts.get("queued", 0)
        }
    
    async def get_queue_items(
        self,
        queue_id: str,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[QueuedExecution]:
        """Get items in a queue"""
        query = self.db.query(QueuedExecution).filter(
            QueuedExecution.queue_id == queue_id
        )
        
        if status:
            query = query.filter(QueuedExecution.status == status)
        
        return query.order_by(
            asc(QueuedExecution.priority),
            asc(QueuedExecution.queued_at)
        ).limit(limit).all()
    
    async def cancel_queue_item(self, queue_item_id: str) -> bool:
        """Cancel a queued execution"""
        item = self.db.query(QueuedExecution).filter(
            QueuedExecution.queue_item_id == queue_item_id
        ).first()
        
        if not item:
            return False
        
        if item.status in ["pending", "queued"]:
            item.status = "cancelled"
            item.completed_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False
    
    async def get_queue_analytics(
        self,
        queue_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get queue analytics"""
        from datetime import timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        items = self.db.query(QueuedExecution).filter(
            and_(
                QueuedExecution.queue_id == queue_id,
                QueuedExecution.created_at >= start_date
            )
        ).all()
        
        # Throughput (items per hour)
        completed_items = [item for item in items if item.status == "completed"]
        hours = days * 24
        throughput = len(completed_items) / hours if hours > 0 else 0
        
        # Success rate
        success_rate = (len(completed_items) / len(items) * 100) if items else 0
        
        # Average execution time
        avg_execution_time = 0
        if completed_items:
            execution_times = [
                (item.completed_at - item.started_at).total_seconds()
                for item in completed_items
                if item.completed_at and item.started_at
            ]
            if execution_times:
                avg_execution_time = sum(execution_times) / len(execution_times)
        
        return {
            "queue_id": queue_id,
            "period_days": days,
            "total_items": len(items),
            "completed_items": len(completed_items),
            "failed_items": len([item for item in items if item.status == "failed"]),
            "throughput_per_hour": round(throughput, 2),
            "success_rate": round(success_rate, 2),
            "average_execution_time_seconds": round(avg_execution_time, 2)
        }


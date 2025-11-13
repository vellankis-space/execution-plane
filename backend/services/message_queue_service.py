"""
Message queue service using Celery for async task processing
"""
import logging
from typing import Dict, Any, Optional
from celery import Celery
from core.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery with fallback to memory broker if Redis not available
try:
    redis_url = getattr(settings, 'REDIS_URL', None) or "redis://localhost:6379/0"
    celery_app = Celery(
        "execution_plane",
        broker=redis_url,
        backend=redis_url
    )
except Exception as e:
    logger.warning(f"Redis not available, using memory broker: {e}")
    # Fallback to memory broker for development
    celery_app = Celery(
        "execution_plane",
        broker="memory://",
        backend="cache+memory://"
    )

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
)


class MessageQueueService:
    """Service for managing async task processing"""
    
    def __init__(self):
        self.celery = celery_app
    
    async def enqueue_workflow_execution(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        priority: int = 3
    ) -> str:
        """Enqueue a workflow execution task"""
        task = self.celery.send_task(
            "execute_workflow",
            args=[workflow_id, input_data],
            priority=priority
        )
        return task.id
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a task"""
        task = self.celery.AsyncResult(task_id)
        return {
            "task_id": task_id,
            "status": task.status,
            "result": task.result if task.ready() else None,
            "error": str(task.info) if task.failed() else None
        }


# Celery tasks
@celery_app.task(name="execute_workflow", bind=True)
def execute_workflow_task(self, workflow_id: str, input_data: Dict[str, Any]):
    """Celery task for executing workflows"""
    import asyncio
    from services.workflow_service import WorkflowService
    from core.database import SessionLocal
    
    db = SessionLocal()
    try:
        workflow_service = WorkflowService(db)
        
        # Update task state
        self.update_state(state='PROGRESS', meta={'workflow_id': workflow_id, 'status': 'starting'})
        
        # Run async workflow execution in sync context
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # Create new event loop if none exists
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Execute workflow
        try:
            execution = loop.run_until_complete(
                workflow_service.execute_workflow(workflow_id, input_data)
            )
            
            if execution:
                execution_status = getattr(execution, 'status', 'unknown')
                execution_id = getattr(execution, 'execution_id', '')
                
                # Update task state with result
                self.update_state(
                    state='SUCCESS',
                    meta={
                        'workflow_id': workflow_id,
                        'execution_id': execution_id,
                        'status': execution_status,
                        'result': 'Workflow execution completed'
                    }
                )
                
                return {
                    'workflow_id': workflow_id,
                    'execution_id': execution_id,
                    'status': execution_status,
                    'success': True
                }
            else:
                raise Exception("Workflow execution returned None")
        
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id} in Celery task: {e}")
            self.update_state(
                state='FAILURE',
                meta={
                    'workflow_id': workflow_id,
                    'status': 'failed',
                    'error': str(e)
                }
            )
            raise
    
    except Exception as e:
        logger.error(f"Error in Celery workflow task: {e}")
        self.update_state(
            state='FAILURE',
            meta={
                'workflow_id': workflow_id,
                'status': 'failed',
                'error': str(e)
            }
        )
        raise
    
    finally:
        db.close()


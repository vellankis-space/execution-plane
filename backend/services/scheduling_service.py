"""
Workflow scheduling service
"""
import uuid
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from croniter import croniter

from models.scheduling import WorkflowSchedule, ScheduledExecution
from services.workflow_service import WorkflowService

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()


class SchedulingService:
    """Service for managing workflow schedules"""
    
    def __init__(self, db: Session):
        self.db = db
        self.workflow_service = WorkflowService(db)
        
        # Start scheduler if not already running
        if not scheduler.running:
            scheduler.start()
            logger.info("Workflow scheduler started")
    
    # Schedule Management
    
    async def create_schedule(
        self,
        workflow_id: str,
        name: str,
        cron_expression: str,
        timezone: str = "UTC",
        input_data: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
        description: Optional[str] = None,
        max_runs: Optional[int] = None,
        is_active: bool = True
    ) -> WorkflowSchedule:
        """Create a new workflow schedule"""
        # Validate cron expression
        if not self._validate_cron_expression(cron_expression):
            raise ValueError(f"Invalid cron expression: {cron_expression}")
        
        schedule_id = str(uuid.uuid4())
        
        # Calculate next run time
        next_run_at = self._calculate_next_run(cron_expression, timezone)
        
        schedule = WorkflowSchedule(
            schedule_id=schedule_id,
            workflow_id=workflow_id,
            name=name,
            description=description,
            cron_expression=cron_expression,
            timezone=timezone,
            input_data=input_data or {},
            created_by=created_by,
            max_runs=max_runs,
            is_active=is_active,
            next_run_at=next_run_at
        )
        
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        
        # Add to scheduler if active
        if is_active:
            await self._add_schedule_to_scheduler(schedule)
        
        return schedule
    
    async def get_schedule(self, schedule_id: str) -> Optional[WorkflowSchedule]:
        """Get a schedule by ID"""
        return self.db.query(WorkflowSchedule).filter(
            WorkflowSchedule.schedule_id == schedule_id
        ).first()
    
    async def get_schedules(
        self,
        workflow_id: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[WorkflowSchedule]:
        """Get schedules with optional filters"""
        query = self.db.query(WorkflowSchedule)
        
        if workflow_id:
            query = query.filter(WorkflowSchedule.workflow_id == workflow_id)
        
        if is_active is not None:
            query = query.filter(WorkflowSchedule.is_active == is_active)
        
        return query.all()
    
    async def update_schedule(
        self,
        schedule_id: str,
        updates: Dict[str, Any]
    ) -> Optional[WorkflowSchedule]:
        """Update a schedule"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return None
        
        # Validate cron expression if being updated
        if "cron_expression" in updates:
            if not self._validate_cron_expression(updates["cron_expression"]):
                raise ValueError(f"Invalid cron expression: {updates['cron_expression']}")
        
        # Remove from scheduler if currently scheduled
        if schedule.is_active:
            await self._remove_schedule_from_scheduler(schedule)
        
        # Update fields
        for key, value in updates.items():
            if hasattr(schedule, key):
                setattr(schedule, key, value)
        
        # Recalculate next run if cron expression or timezone changed
        if "cron_expression" in updates or "timezone" in updates:
            schedule.next_run_at = self._calculate_next_run(
                schedule.cron_expression,
                schedule.timezone
            )
        
        setattr(schedule, 'updated_at', datetime.utcnow())
        self.db.commit()
        self.db.refresh(schedule)
        
        # Re-add to scheduler if active
        if schedule.is_active:
            await self._add_schedule_to_scheduler(schedule)
        
        return schedule
    
    async def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a schedule"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return False
        
        # Remove from scheduler
        if schedule.is_active:
            await self._remove_schedule_from_scheduler(schedule)
        
        self.db.delete(schedule)
        self.db.commit()
        return True
    
    async def toggle_schedule(self, schedule_id: str) -> Optional[WorkflowSchedule]:
        """Toggle schedule active status"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return None
        
        schedule.is_active = not schedule.is_active
        
        if schedule.is_active:
            await self._add_schedule_to_scheduler(schedule)
        else:
            await self._remove_schedule_from_scheduler(schedule)
        
        self.db.commit()
        self.db.refresh(schedule)
        
        return schedule
    
    # Schedule Execution
    
    async def _execute_scheduled_workflow(self, schedule_id: str):
        """Execute a scheduled workflow"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule or not schedule.is_active:
            logger.warning(f"Schedule {schedule_id} not found or inactive")
            return
        
        # Check max runs
        if schedule.max_runs and schedule.run_count >= schedule.max_runs:
            logger.info(f"Schedule {schedule_id} has reached max runs ({schedule.max_runs})")
            schedule.is_active = False
            await self._remove_schedule_from_scheduler(schedule)
            self.db.commit()
            return
        
        execution_id = str(uuid.uuid4())
        
        # Create scheduled execution record
        scheduled_execution = ScheduledExecution(
            execution_id=execution_id,
            schedule_id=schedule_id,
            workflow_id=schedule.workflow_id,
            scheduled_at=schedule.next_run_at,
            status="pending"
        )
        
        self.db.add(scheduled_execution)
        self.db.commit()
        
        try:
            # Execute the workflow
            workflow_execution = await self.workflow_service.execute_workflow(
                schedule.workflow_id,
                input_data=schedule.input_data or {}
            )
            
            # Update scheduled execution
            scheduled_execution.workflow_execution_id = workflow_execution.execution_id
            scheduled_execution.executed_at = datetime.utcnow()
            scheduled_execution.status = "completed"
            
            # Update schedule
            schedule.last_run_at = datetime.utcnow()
            schedule.last_run_status = "success"
            schedule.run_count += 1
            schedule.next_run_at = self._calculate_next_run(
                schedule.cron_expression,
                schedule.timezone
            )
            
            # Re-add to scheduler with new next run time
            await self._remove_schedule_from_scheduler(schedule)
            if schedule.is_active:
                await self._add_schedule_to_scheduler(schedule)
            
        except Exception as e:
            logger.error(f"Error executing scheduled workflow {schedule_id}: {str(e)}")
            scheduled_execution.status = "failed"
            scheduled_execution.error_message = str(e)
            schedule.last_run_status = "failed"
        
        self.db.commit()
    
    # Scheduler Management
    
    async def _add_schedule_to_scheduler(self, schedule: WorkflowSchedule):
        """Add a schedule to the scheduler"""
        try:
            # Parse cron expression
            cron_parts = schedule.cron_expression.split()
            if len(cron_parts) != 5:
                raise ValueError(f"Invalid cron expression format: {schedule.cron_expression}")
            
            # Create cron trigger
            trigger = CronTrigger(
                minute=cron_parts[0],
                hour=cron_parts[1],
                day=cron_parts[2],
                month=cron_parts[3],
                day_of_week=cron_parts[4],
                timezone=schedule.timezone
            )
            
            # Add job to scheduler
            scheduler.add_job(
                self._execute_scheduled_workflow,
                trigger=trigger,
                id=schedule.schedule_id,
                args=[schedule.schedule_id],
                replace_existing=True
            )
            
            logger.info(f"Added schedule {schedule.schedule_id} to scheduler")
        except Exception as e:
            logger.error(f"Error adding schedule to scheduler: {str(e)}")
    
    async def _remove_schedule_from_scheduler(self, schedule: WorkflowSchedule):
        """Remove a schedule from the scheduler"""
        try:
            scheduler.remove_job(schedule.schedule_id)
            logger.info(f"Removed schedule {schedule.schedule_id} from scheduler")
        except Exception as e:
            logger.warning(f"Error removing schedule from scheduler: {str(e)}")
    
    async def load_all_schedules(self):
        """Load all active schedules into the scheduler"""
        schedules = await self.get_schedules(is_active=True)
        for schedule in schedules:
            await self._add_schedule_to_scheduler(schedule)
        logger.info(f"Loaded {len(schedules)} active schedules")
    
    # Utility Methods
    
    def _validate_cron_expression(self, cron_expression: str) -> bool:
        """Validate a cron expression"""
        try:
            croniter(cron_expression)
            return True
        except Exception:
            return False
    
    def _calculate_next_run(self, cron_expression: str, timezone: str) -> datetime:
        """Calculate the next run time for a cron expression"""
        try:
            cron = croniter(cron_expression, datetime.now())
            return cron.get_next(datetime)
        except Exception as e:
            logger.error(f"Error calculating next run time: {str(e)}")
            return datetime.utcnow() + timedelta(hours=1)
    
    # Scheduled Execution Management
    
    async def get_scheduled_executions(
        self,
        schedule_id: Optional[str] = None,
        limit: int = 100
    ) -> List[ScheduledExecution]:
        """Get scheduled executions"""
        query = self.db.query(ScheduledExecution)
        
        if schedule_id:
            query = query.filter(ScheduledExecution.schedule_id == schedule_id)
        
        return query.order_by(ScheduledExecution.scheduled_at.desc()).limit(limit).all()


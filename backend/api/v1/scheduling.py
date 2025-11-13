"""
Workflow scheduling API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from services.scheduling_service import SchedulingService
from core.database import get_db
from api.v1.auth import get_current_user

router = APIRouter()


# Request/Response models
class ScheduleCreate(BaseModel):
    workflow_id: str
    name: str
    cron_expression: str
    timezone: str = "UTC"
    input_data: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    max_runs: Optional[int] = None
    is_active: bool = True


class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    cron_expression: Optional[str] = None
    timezone: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    max_runs: Optional[int] = None
    is_active: Optional[bool] = None


class ScheduleResponse(BaseModel):
    schedule_id: str
    workflow_id: str
    name: str
    description: Optional[str]
    cron_expression: str
    timezone: str
    is_active: bool
    input_data: Dict[str, Any]
    next_run_at: Optional[str]
    last_run_at: Optional[str]
    last_run_status: Optional[str]
    run_count: int
    max_runs: Optional[int]
    created_by: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


# Schedule Endpoints

@router.post("/schedules", response_model=ScheduleResponse)
async def create_schedule(
    schedule_data: ScheduleCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workflow schedule"""
    try:
        scheduling_service = SchedulingService(db)
        schedule = await scheduling_service.create_schedule(
            workflow_id=schedule_data.workflow_id,
            name=schedule_data.name,
            cron_expression=schedule_data.cron_expression,
            timezone=schedule_data.timezone,
            input_data=schedule_data.input_data,
            description=schedule_data.description,
            max_runs=schedule_data.max_runs,
            is_active=schedule_data.is_active,
            created_by=current_user.user_id
        )
        
        return ScheduleResponse(
            schedule_id=schedule.schedule_id,
            workflow_id=schedule.workflow_id,
            name=schedule.name,
            description=schedule.description,
            cron_expression=schedule.cron_expression,
            timezone=schedule.timezone,
            is_active=schedule.is_active,
            input_data=schedule.input_data or {},
            next_run_at=schedule.next_run_at.isoformat() if schedule.next_run_at else None,
            last_run_at=schedule.last_run_at.isoformat() if schedule.last_run_at else None,
            last_run_status=schedule.last_run_status,
            run_count=schedule.run_count,
            max_runs=schedule.max_runs,
            created_by=schedule.created_by,
            created_at=schedule.created_at.isoformat() if schedule.created_at else ""
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedules", response_model=List[ScheduleResponse])
async def get_schedules(
    workflow_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get workflow schedules"""
    try:
        scheduling_service = SchedulingService(db)
        schedules = await scheduling_service.get_schedules(
            workflow_id=workflow_id,
            is_active=is_active
        )
        
        return [
            ScheduleResponse(
                schedule_id=schedule.schedule_id,
                workflow_id=schedule.workflow_id,
                name=schedule.name,
                description=schedule.description,
                cron_expression=schedule.cron_expression,
                timezone=schedule.timezone,
                is_active=schedule.is_active,
                input_data=schedule.input_data or {},
                next_run_at=schedule.next_run_at.isoformat() if schedule.next_run_at else None,
                last_run_at=schedule.last_run_at.isoformat() if schedule.last_run_at else None,
                last_run_status=schedule.last_run_status,
                run_count=schedule.run_count,
                max_runs=schedule.max_runs,
                created_by=schedule.created_by,
                created_at=schedule.created_at.isoformat() if schedule.created_at else ""
            )
            for schedule in schedules
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific schedule"""
    try:
        scheduling_service = SchedulingService(db)
        schedule = await scheduling_service.get_schedule(schedule_id)
        
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        return ScheduleResponse(
            schedule_id=schedule.schedule_id,
            workflow_id=schedule.workflow_id,
            name=schedule.name,
            description=schedule.description,
            cron_expression=schedule.cron_expression,
            timezone=schedule.timezone,
            is_active=schedule.is_active,
            input_data=schedule.input_data or {},
            next_run_at=schedule.next_run_at.isoformat() if schedule.next_run_at else None,
            last_run_at=schedule.last_run_at.isoformat() if schedule.last_run_at else None,
            last_run_status=schedule.last_run_status,
            run_count=schedule.run_count,
            max_runs=schedule.max_runs,
            created_by=schedule.created_by,
            created_at=schedule.created_at.isoformat() if schedule.created_at else ""
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: str,
    schedule_data: ScheduleUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a schedule"""
    try:
        scheduling_service = SchedulingService(db)
        updates = schedule_data.dict(exclude_unset=True)
        schedule = await scheduling_service.update_schedule(schedule_id, updates)
        
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        return ScheduleResponse(
            schedule_id=schedule.schedule_id,
            workflow_id=schedule.workflow_id,
            name=schedule.name,
            description=schedule.description,
            cron_expression=schedule.cron_expression,
            timezone=schedule.timezone,
            is_active=schedule.is_active,
            input_data=schedule.input_data or {},
            next_run_at=schedule.next_run_at.isoformat() if schedule.next_run_at else None,
            last_run_at=schedule.last_run_at.isoformat() if schedule.last_run_at else None,
            last_run_status=schedule.last_run_status,
            run_count=schedule.run_count,
            max_runs=schedule.max_runs,
            created_by=schedule.created_by,
            created_at=schedule.created_at.isoformat() if schedule.created_at else ""
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a schedule"""
    try:
        scheduling_service = SchedulingService(db)
        success = await scheduling_service.delete_schedule(schedule_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        return {"message": "Schedule deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedules/{schedule_id}/toggle")
async def toggle_schedule(
    schedule_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle schedule active status"""
    try:
        scheduling_service = SchedulingService(db)
        schedule = await scheduling_service.toggle_schedule(schedule_id)
        
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        return {
            "message": f"Schedule {'activated' if schedule.is_active else 'deactivated'}",
            "is_active": schedule.is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedules/{schedule_id}/executions")
async def get_schedule_executions(
    schedule_id: str,
    limit: int = 50,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get executions for a schedule"""
    try:
        scheduling_service = SchedulingService(db)
        executions = await scheduling_service.get_scheduled_executions(
            schedule_id=schedule_id,
            limit=limit
        )
        
        return [
            {
                "execution_id": exec.execution_id,
                "schedule_id": exec.schedule_id,
                "workflow_id": exec.workflow_id,
                "workflow_execution_id": exec.workflow_execution_id,
                "scheduled_at": exec.scheduled_at.isoformat() if exec.scheduled_at else None,
                "executed_at": exec.executed_at.isoformat() if exec.executed_at else None,
                "status": exec.status,
                "error_message": exec.error_message,
            }
            for exec in executions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


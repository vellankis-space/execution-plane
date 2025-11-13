from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime

from services.monitoring_service import MonitoringService
from core.database import get_db

router = APIRouter()

@router.get("/metrics/workflow-executions")
async def get_workflow_execution_metrics(
    workflow_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get metrics for workflow executions"""
    try:
        monitoring_service = MonitoringService(db)
        metrics = await monitoring_service.get_workflow_execution_metrics(
            workflow_id=workflow_id,
            start_time=start_time,
            end_time=end_time
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/metrics/step-executions")
async def get_step_execution_metrics(
    workflow_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get metrics for step executions"""
    try:
        monitoring_service = MonitoringService(db)
        metrics = await monitoring_service.get_step_execution_metrics(
            workflow_id=workflow_id,
            start_time=start_time,
            end_time=end_time
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/reports/workflow-performance/{workflow_id}")
async def get_workflow_performance_report(
    workflow_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get a comprehensive performance report for a workflow"""
    try:
        monitoring_service = MonitoringService(db)
        report = await monitoring_service.get_workflow_performance_report(
            workflow_id=workflow_id,
            days=days
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/health")
async def get_system_health_metrics(db: Session = Depends(get_db)):
    """Get overall system health metrics"""
    try:
        monitoring_service = MonitoringService(db)
        health_metrics = await monitoring_service.get_system_health_metrics()
        return health_metrics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/recent-executions")
async def get_recent_executions(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get recent workflow executions"""
    try:
        monitoring_service = MonitoringService(db)
        executions = await monitoring_service.get_recent_executions(limit=limit)
        return executions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
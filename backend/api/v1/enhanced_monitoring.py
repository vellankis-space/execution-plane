from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from datetime import datetime

from services.enhanced_monitoring_service import EnhancedMonitoringService
from core.database import get_db

router = APIRouter()

@router.get("/enhanced-metrics/workflow-executions")
async def get_enhanced_workflow_execution_metrics(
    workflow_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get enhanced metrics for workflow executions with resource usage data"""
    try:
        monitoring_service = EnhancedMonitoringService(db)
        metrics = await monitoring_service.get_enhanced_workflow_metrics(
            workflow_id=workflow_id,
            start_time=start_time,
            end_time=end_time
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/enhanced-metrics/step-executions")
async def get_enhanced_step_execution_metrics(
    workflow_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get enhanced metrics for step executions with resource usage data"""
    try:
        monitoring_service = EnhancedMonitoringService(db)
        metrics = await monitoring_service.get_enhanced_step_metrics(
            workflow_id=workflow_id,
            start_time=start_time,
            end_time=end_time
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analytics/bottlenecks/{workflow_id}")
async def get_performance_bottlenecks(
    workflow_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Identify performance bottlenecks in workflow executions"""
    try:
        monitoring_service = EnhancedMonitoringService(db)
        bottlenecks = await monitoring_service.get_performance_bottlenecks(
            workflow_id=workflow_id,
            days=days
        )
        return bottlenecks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/logs/{execution_id}")
async def get_execution_logs(
    execution_id: str,
    log_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get execution logs for a specific workflow execution"""
    try:
        monitoring_service = EnhancedMonitoringService(db)
        logs = await monitoring_service.get_execution_logs(
            execution_id=execution_id,
            log_level=log_level
        )
        return logs
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analytics/resource-trends/{workflow_id}")
async def get_resource_usage_trends(
    workflow_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get resource usage trends over time for a workflow"""
    try:
        monitoring_service = EnhancedMonitoringService(db)
        trends = await monitoring_service.get_resource_usage_trends(
            workflow_id=workflow_id,
            days=days
        )
        return trends
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analytics/failure-analysis/{workflow_id}")
async def get_failure_analysis(
    workflow_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Analyze workflow and step failures to identify patterns"""
    try:
        monitoring_service = EnhancedMonitoringService(db)
        analysis = await monitoring_service.get_failure_analysis(
            workflow_id=workflow_id,
            days=days
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analytics/predictive/{workflow_id}")
async def get_predictive_analytics(
    workflow_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Provide predictive analytics based on historical execution data"""
    try:
        monitoring_service = EnhancedMonitoringService(db)
        predictions = await monitoring_service.get_predictive_analytics(
            workflow_id=workflow_id,
            days=days
        )
        return predictions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
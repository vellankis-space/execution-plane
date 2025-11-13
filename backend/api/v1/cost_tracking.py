"""
API endpoints for cost tracking
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from services.cost_tracking_service import CostTrackingService
from core.database import get_db

router = APIRouter()


# Request/Response models
class CostBudgetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    budget_type: str  # daily, weekly, monthly, total
    amount: float
    alert_threshold: float = 0.8
    enabled: bool = True


class CostSummaryResponse(BaseModel):
    total_cost: float
    total_tokens: int
    total_calls: int
    by_provider: Dict[str, Any]
    by_model: Dict[str, Any]
    period: Dict[str, Optional[str]]


# Cost Tracking Endpoints

@router.get("/summary", response_model=CostSummaryResponse)
async def get_cost_summary(
    agent_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get cost summary for a time period"""
    try:
        if not start_date:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
        
        cost_service = CostTrackingService(db)
        summary = await cost_service.get_cost_summary(
            agent_id=agent_id,
            workflow_id=workflow_id,
            start_date=start_date,
            end_date=end_date
        )
        return CostSummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trends")
async def get_cost_trends(
    days: int = 30,
    agent_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get cost trends over time"""
    try:
        cost_service = CostTrackingService(db)
        trends = await cost_service.get_cost_trends(
            days=days,
            agent_id=agent_id,
            workflow_id=workflow_id
        )
        return trends
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api-calls")
async def get_api_calls(
    agent_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get recent API calls"""
    try:
        from models.cost_tracking import APICall
        from sqlalchemy import desc
        
        query = db.query(APICall)
        
        if agent_id:
            query = query.filter(APICall.agent_id == agent_id)
        
        if workflow_id:
            query = query.filter(APICall.workflow_id == workflow_id)
        
        calls = query.order_by(desc(APICall.created_at)).limit(limit).all()
        
        return [
            {
                "call_id": call.call_id,
                "agent_id": call.agent_id,
                "workflow_id": call.workflow_id,
                "execution_id": call.execution_id,
                "provider": call.provider,
                "model": call.model,
                "input_tokens": call.input_tokens,
                "output_tokens": call.output_tokens,
                "total_tokens": call.total_tokens,
                "cost": call.cost,
                "created_at": call.created_at.isoformat() if call.created_at else None,
            }
            for call in calls
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Budget Management Endpoints

@router.post("/budgets")
async def create_budget(
    budget_data: CostBudgetCreate,
    db: Session = Depends(get_db)
):
    """Create a cost budget"""
    try:
        cost_service = CostTrackingService(db)
        budget = await cost_service.create_budget(
            name=budget_data.name,
            description=budget_data.description,
            budget_type=budget_data.budget_type,
            amount=budget_data.amount,
            alert_threshold=budget_data.alert_threshold,
            enabled=budget_data.enabled
        )
        return {
            "budget_id": budget.budget_id,
            "name": budget.name,
            "budget_type": budget.budget_type,
            "amount": budget.amount,
            "enabled": budget.enabled,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/budgets")
async def get_budgets(db: Session = Depends(get_db)):
    """Get all budgets"""
    try:
        cost_service = CostTrackingService(db)
        budgets = await cost_service.get_budgets()
        return [
            {
                "budget_id": budget.budget_id,
                "name": budget.name,
                "description": budget.description,
                "budget_type": budget.budget_type,
                "amount": budget.amount,
                "alert_threshold": budget.alert_threshold,
                "enabled": budget.enabled,
                "period_start": budget.period_start.isoformat() if budget.period_start else None,
                "period_end": budget.period_end.isoformat() if budget.period_end else None,
            }
            for budget in budgets
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/budgets/{budget_id}/status")
async def get_budget_status(
    budget_id: str,
    db: Session = Depends(get_db)
):
    """Get current status of a budget"""
    try:
        cost_service = CostTrackingService(db)
        status = await cost_service.get_budget_status(budget_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/alerts")
async def get_cost_alerts(
    budget_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get cost-related alerts"""
    try:
        from models.cost_tracking import CostAlert
        from sqlalchemy import desc
        
        query = db.query(CostAlert)
        
        if budget_id:
            query = query.filter(CostAlert.budget_id == budget_id)
        
        if status:
            query = query.filter(CostAlert.status == status)
        
        alerts = query.order_by(desc(CostAlert.created_at)).limit(limit).all()
        
        return [
            {
                "alert_id": alert.alert_id,
                "budget_id": alert.budget_id,
                "alert_type": alert.alert_type,
                "message": alert.message,
                "current_cost": alert.current_cost,
                "budget_amount": alert.budget_amount,
                "percentage_used": alert.percentage_used,
                "status": alert.status,
                "created_at": alert.created_at.isoformat() if alert.created_at else None,
            }
            for alert in alerts
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


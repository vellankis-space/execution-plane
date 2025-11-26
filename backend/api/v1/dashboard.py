from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

from core.database import get_db
from middleware.tenant_middleware import get_current_tenant_id
from services.agent_service import AgentService
from services.workflow_service import WorkflowService

router = APIRouter()

class DashboardStats(BaseModel):
    total_agents: int
    active_workflows: int
    executions_today: int

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get real-time dashboard statistics"""
    try:
        tenant_id = get_current_tenant_id()
        
        agent_service = AgentService(db)
        workflow_service = WorkflowService(db)
        
        # Get total agents
        total_agents = await agent_service.count_agents(tenant_id=tenant_id)
        
        # Get active workflows
        active_workflows = await workflow_service.count_active_workflows(tenant_id=tenant_id)
        
        # Get executions today (UTC)
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        executions_today = await workflow_service.count_executions_in_time_range(
            start_time=start_of_day,
            end_time=end_of_day,
            tenant_id=tenant_id
        )
        
        return DashboardStats(
            total_agents=total_agents,
            active_workflows=active_workflows,
            executions_today=executions_today
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

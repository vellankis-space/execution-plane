"""
Langfuse analytics API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from services.langfuse_integration import LangfuseIntegration
from core.database import get_db
from api.v1.auth import get_current_user

router = APIRouter()


@router.get("/traces")
async def get_traces(
    agent_id: Optional[str] = Query(None),
    workflow_id: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, le=500),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get LLM traces from Langfuse"""
    try:
        langfuse = LangfuseIntegration()
        if not langfuse.enabled:
            raise HTTPException(status_code=503, detail="Langfuse not configured")
        
        # This would query Langfuse API for traces
        # Implementation depends on Langfuse API client
        return {
            "message": "Langfuse integration enabled",
            "note": "Use Langfuse dashboard for detailed trace viewing"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cost-analytics")
async def get_langfuse_cost_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get cost analytics from Langfuse"""
    try:
        langfuse = LangfuseIntegration()
        if not langfuse.enabled:
            raise HTTPException(status_code=503, detail="Langfuse not configured")
        
        analytics = langfuse.get_cost_analytics(
            start_date=start_date,
            end_date=end_date
        )
        
        return analytics or {
            "message": "Langfuse cost analytics available",
            "note": "Use Langfuse dashboard for detailed cost breakdown"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


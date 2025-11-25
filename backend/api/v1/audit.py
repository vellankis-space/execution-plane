"""
Audit logging API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, ConfigDict

from services.audit_service import AuditService
from core.database import get_db
from api.v1.auth import get_current_superuser

router = APIRouter()


# Response models
class AuditLogResponse(BaseModel):
    log_id: str
    user_id: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    resource_name: Optional[str]
    tenant_id: Optional[str]
    ip_address: Optional[str]
    request_method: Optional[str]
    request_path: Optional[str]
    status_code: Optional[int]
    success: int
    error_message: Optional[str]
    changes: dict
    metadata: dict
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# Audit Log Endpoints

@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    tenant_id: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    success_only: Optional[bool] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    current_user = Depends(get_current_superuser),  # Only superusers can view audit logs
    db: Session = Depends(get_db)
):
    """Get audit logs with filters (admin only)"""
    try:
        audit_service = AuditService(db)
        logs = await audit_service.get_audit_logs(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date,
            success_only=success_only,
            limit=limit,
            offset=offset
        )
        
        return [
            AuditLogResponse(
                log_id=log.log_id,
                user_id=log.user_id,
                action=log.action,
                resource_type=log.resource_type,
                resource_id=log.resource_id,
                resource_name=log.resource_name,
                tenant_id=log.tenant_id,
                ip_address=log.ip_address,
                request_method=log.request_method,
                request_path=log.request_path,
                status_code=log.status_code,
                success=log.success,
                error_message=log.error_message,
                changes=log.changes or {},
                metadata=log.audit_metadata or {},
                created_at=log.created_at.isoformat() if log.created_at else ""
            )
            for log in logs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_audit_summary(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    tenant_id: Optional[str] = Query(None),
    days: int = Query(30),
    current_user = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Get audit log summary statistics (admin only)"""
    try:
        if not start_date:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
        
        audit_service = AuditService(db)
        summary = await audit_service.get_audit_summary(
            start_date=start_date,
            end_date=end_date,
            tenant_id=tenant_id
        )
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline")
async def get_audit_timeline(
    days: int = Query(7, le=90),
    tenant_id: Optional[str] = Query(None),
    current_user = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Get audit log timeline (admin only)"""
    try:
        audit_service = AuditService(db)
        timeline = await audit_service.get_audit_timeline(
            days=days,
            tenant_id=tenant_id
        )
        
        return timeline
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_audit_logs(
    q: str = Query(..., min_length=1),
    limit: int = Query(100, le=500),
    current_user = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Search audit logs (admin only)"""
    try:
        audit_service = AuditService(db)
        logs = await audit_service.search_audit_logs(
            search_term=q,
            limit=limit
        )
        
        return [
            AuditLogResponse(
                log_id=log.log_id,
                user_id=log.user_id,
                action=log.action,
                resource_type=log.resource_type,
                resource_id=log.resource_id,
                resource_name=log.resource_name,
                tenant_id=log.tenant_id,
                ip_address=log.ip_address,
                request_method=log.request_method,
                request_path=log.request_path,
                status_code=log.status_code,
                success=log.success,
                error_message=log.error_message,
                changes=log.changes or {},
                metadata=log.audit_metadata or {},
                created_at=log.created_at.isoformat() if log.created_at else ""
            )
            for log in logs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


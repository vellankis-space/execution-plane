"""
Audit logging service
"""
import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.sql import text

from models.audit import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit logging"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_method: Optional[str] = None,
        request_path: Optional[str] = None,
        status_code: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log an audit event"""
        log_id = str(uuid.uuid4())
        
        audit_log = AuditLog(
            log_id=log_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            tenant_id=tenant_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_path=request_path,
            status_code=status_code,
            success=1 if success else 0,
            error_message=error_message,
            changes=changes or {},
            metadata=metadata or {}
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
    
    async def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        success_only: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Get audit logs with filters"""
        query = self.db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        
        if tenant_id:
            query = query.filter(AuditLog.tenant_id == tenant_id)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        if success_only is not None:
            query = query.filter(AuditLog.success == (1 if success_only else 0))
        
        return query.order_by(desc(AuditLog.created_at)).offset(offset).limit(limit).all()
    
    async def get_audit_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get audit log summary statistics"""
        query = self.db.query(AuditLog)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        if tenant_id:
            query = query.filter(AuditLog.tenant_id == tenant_id)
        
        # Total actions
        total_actions = query.count()
        
        # Success/failure counts
        success_count = query.filter(AuditLog.success == 1).count()
        failure_count = query.filter(AuditLog.success == 0).count()
        
        # Actions by type
        actions_by_type = {}
        action_counts = self.db.query(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        )
        
        if start_date:
            action_counts = action_counts.filter(AuditLog.created_at >= start_date)
        if end_date:
            action_counts = action_counts.filter(AuditLog.created_at <= end_date)
        if tenant_id:
            action_counts = action_counts.filter(AuditLog.tenant_id == tenant_id)
        
        action_counts = action_counts.group_by(AuditLog.action).all()
        for action, count in action_counts:
            actions_by_type[action] = count
        
        # Resources by type
        resources_by_type = {}
        resource_counts = self.db.query(
            AuditLog.resource_type,
            func.count(AuditLog.id).label('count')
        )
        
        if start_date:
            resource_counts = resource_counts.filter(AuditLog.created_at >= start_date)
        if end_date:
            resource_counts = resource_counts.filter(AuditLog.created_at <= end_date)
        if tenant_id:
            resource_counts = resource_counts.filter(AuditLog.tenant_id == tenant_id)
        
        resource_counts = resource_counts.group_by(AuditLog.resource_type).all()
        for resource_type, count in resource_counts:
            resources_by_type[resource_type] = count
        
        # Top users
        top_users = {}
        user_counts = self.db.query(
            AuditLog.user_id,
            func.count(AuditLog.id).label('count')
        )
        
        if start_date:
            user_counts = user_counts.filter(AuditLog.created_at >= start_date)
        if end_date:
            user_counts = user_counts.filter(AuditLog.created_at <= end_date)
        if tenant_id:
            user_counts = user_counts.filter(AuditLog.tenant_id == tenant_id)
        
        user_counts = user_counts.filter(AuditLog.user_id.isnot(None)).group_by(AuditLog.user_id).order_by(desc('count')).limit(10).all()
        for user_id, count in user_counts:
            top_users[user_id] = count
        
        return {
            "total_actions": total_actions,
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": (success_count / total_actions * 100) if total_actions > 0 else 0,
            "actions_by_type": actions_by_type,
            "resources_by_type": resources_by_type,
            "top_users": top_users,
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None,
            }
        }
    
    async def get_audit_timeline(
        self,
        days: int = 7,
        tenant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get audit log timeline grouped by day"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = self.db.query(
            func.date(AuditLog.created_at).label('date'),
            func.count(AuditLog.id).label('count'),
            func.sum(func.cast(AuditLog.success, Integer)).label('success_count')
        ).filter(
            and_(
                AuditLog.created_at >= start_date,
                AuditLog.created_at <= end_date
            )
        )
        
        if tenant_id:
            query = query.filter(AuditLog.tenant_id == tenant_id)
        
        results = query.group_by(func.date(AuditLog.created_at)).order_by('date').all()
        
        timeline = []
        for date, count, success_count in results:
            timeline.append({
                "date": date.isoformat() if date else None,
                "total": count,
                "success": success_count or 0,
                "failure": count - (success_count or 0)
            })
        
        return timeline
    
    async def search_audit_logs(
        self,
        search_term: str,
        limit: int = 100
    ) -> List[AuditLog]:
        """Search audit logs by resource name, user, or action"""
        query = self.db.query(AuditLog).filter(
            or_(
                AuditLog.resource_name.ilike(f"%{search_term}%"),
                AuditLog.user_id.ilike(f"%{search_term}%"),
                AuditLog.action.ilike(f"%{search_term}%"),
                AuditLog.resource_type.ilike(f"%{search_term}%")
            )
        )
        
        return query.order_by(desc(AuditLog.created_at)).limit(limit).all()


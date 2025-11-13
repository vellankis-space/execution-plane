"""
API endpoints for alerting management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from services.alerting_service import AlertingService
from core.database import get_db

router = APIRouter()


# Request/Response models
class AlertRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    workflow_id: Optional[str] = None
    condition_type: str  # execution_failure, performance_degradation, resource_threshold, custom
    condition_config: Dict[str, Any]
    notification_channels: List[Dict[str, Any]]
    severity: str = "medium"
    enabled: bool = True


class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    condition_config: Optional[Dict[str, Any]] = None
    notification_channels: Optional[List[Dict[str, Any]]] = None
    enabled: Optional[bool] = None
    severity: Optional[str] = None


class NotificationChannelCreate(BaseModel):
    name: str
    channel_type: str  # email, webhook, slack, in_app
    config: Dict[str, Any]
    enabled: bool = True


class AlertResponse(BaseModel):
    alert_id: str
    rule_id: str
    workflow_id: Optional[str]
    execution_id: Optional[str]
    severity: str
    message: str
    details: Optional[Dict[str, Any]]
    status: str
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[str]
    resolved_at: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


# Alert Rule Endpoints

@router.post("/rules")
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    db: Session = Depends(get_db)
):
    """Create a new alert rule"""
    try:
        alerting_service = AlertingService(db)
        rule = await alerting_service.create_alert_rule(
            name=rule_data.name,
            description=rule_data.description,
            workflow_id=rule_data.workflow_id,
            condition_type=rule_data.condition_type,
            condition_config=rule_data.condition_config,
            notification_channels=rule_data.notification_channels,
            severity=rule_data.severity,
            enabled=rule_data.enabled
        )
        return {
            "rule_id": rule.rule_id,
            "name": rule.name,
            "enabled": rule.enabled,
            "created_at": rule.created_at.isoformat() if rule.created_at else None
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rules")
async def get_alert_rules(
    workflow_id: Optional[str] = None,
    enabled_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get alert rules"""
    try:
        alerting_service = AlertingService(db)
        rules = await alerting_service.get_alert_rules(
            workflow_id=workflow_id,
            enabled_only=enabled_only
        )
        return [
            {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "description": rule.description,
                "workflow_id": rule.workflow_id,
                "condition_type": rule.condition_type,
                "condition_config": rule.condition_config,
                "notification_channels": rule.notification_channels,
                "enabled": rule.enabled,
                "severity": rule.severity,
                "created_at": rule.created_at.isoformat() if rule.created_at else None,
            }
            for rule in rules
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/rules/{rule_id}")
async def update_alert_rule(
    rule_id: str,
    rule_data: AlertRuleUpdate,
    db: Session = Depends(get_db)
):
    """Update an alert rule"""
    try:
        alerting_service = AlertingService(db)
        updates = rule_data.dict(exclude_unset=True)
        rule = await alerting_service.update_alert_rule(rule_id, updates)
        if not rule:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        return {
            "rule_id": rule.rule_id,
            "name": rule.name,
            "enabled": rule.enabled,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/rules/{rule_id}")
async def delete_alert_rule(
    rule_id: str,
    db: Session = Depends(get_db)
):
    """Delete an alert rule"""
    try:
        alerting_service = AlertingService(db)
        success = await alerting_service.delete_alert_rule(rule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        return {"message": "Alert rule deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Alert Endpoints

@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    rule_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get alerts with filters"""
    try:
        alerting_service = AlertingService(db)
        alerts = await alerting_service.get_alerts(
            rule_id=rule_id,
            workflow_id=workflow_id,
            status=status,
            severity=severity,
            limit=limit
        )
        return [
            AlertResponse(
                alert_id=alert.alert_id,
                rule_id=alert.rule_id,
                workflow_id=alert.workflow_id,
                execution_id=alert.execution_id,
                severity=alert.severity,
                message=alert.message,
                details=alert.details,
                status=alert.status,
                acknowledged_by=alert.acknowledged_by,
                acknowledged_at=alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                resolved_at=alert.resolved_at.isoformat() if alert.resolved_at else None,
                created_at=alert.created_at.isoformat() if alert.created_at else "",
            )
            for alert in alerts
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    acknowledged_by: str,
    db: Session = Depends(get_db)
):
    """Acknowledge an alert"""
    try:
        alerting_service = AlertingService(db)
        alert = await alerting_service.acknowledge_alert(alert_id, acknowledged_by)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"message": "Alert acknowledged", "alert_id": alert.alert_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    db: Session = Depends(get_db)
):
    """Resolve an alert"""
    try:
        alerting_service = AlertingService(db)
        alert = await alerting_service.resolve_alert(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"message": "Alert resolved", "alert_id": alert.alert_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Notification Channel Endpoints

@router.post("/channels")
async def create_notification_channel(
    channel_data: NotificationChannelCreate,
    db: Session = Depends(get_db)
):
    """Create a notification channel"""
    try:
        alerting_service = AlertingService(db)
        channel = await alerting_service.create_notification_channel(
            name=channel_data.name,
            channel_type=channel_data.channel_type,
            config=channel_data.config,
            enabled=channel_data.enabled
        )
        return {
            "channel_id": channel.channel_id,
            "name": channel.name,
            "channel_type": channel.channel_type,
            "enabled": channel.enabled
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/channels")
async def get_notification_channels(db: Session = Depends(get_db)):
    """Get all notification channels"""
    try:
        alerting_service = AlertingService(db)
        channels = await alerting_service.get_notification_channels()
        return [
            {
                "channel_id": channel.channel_id,
                "name": channel.name,
                "channel_type": channel.channel_type,
                "enabled": channel.enabled,
            }
            for channel in channels
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


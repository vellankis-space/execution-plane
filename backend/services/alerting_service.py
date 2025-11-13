"""
Alerting service for monitoring and notifications
"""
import uuid
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta

from models.alerting import AlertRule, Alert, NotificationChannel
from models.workflow import WorkflowExecution, StepExecution
from services.monitoring_service import MonitoringService

logger = logging.getLogger(__name__)


class AlertingService:
    """Service for managing alerts and notifications"""
    
    def __init__(self, db: Session):
        self.db = db
        self.monitoring_service = MonitoringService(db)
    
    # Alert Rule Management
    
    async def create_alert_rule(
        self,
        name: str,
        condition_type: str,
        condition_config: Dict[str, Any],
        notification_channels: List[Dict[str, Any]],
        workflow_id: Optional[str] = None,
        description: Optional[str] = None,
        severity: str = "medium",
        enabled: bool = True
    ) -> AlertRule:
        """Create a new alert rule"""
        rule_id = str(uuid.uuid4())
        
        alert_rule = AlertRule(
            rule_id=rule_id,
            name=name,
            description=description,
            workflow_id=workflow_id,
            condition_type=condition_type,
            condition_config=condition_config,
            notification_channels=notification_channels,
            enabled=enabled,
            severity=severity
        )
        
        self.db.add(alert_rule)
        self.db.commit()
        self.db.refresh(alert_rule)
        
        return alert_rule
    
    async def get_alert_rules(
        self,
        workflow_id: Optional[str] = None,
        enabled_only: bool = False
    ) -> List[AlertRule]:
        """Get alert rules"""
        query = self.db.query(AlertRule)
        
        if workflow_id:
            query = query.filter(
                or_(
                    AlertRule.workflow_id == workflow_id,
                    AlertRule.workflow_id.is_(None)
                )
            )
        
        if enabled_only:
            query = query.filter(AlertRule.enabled == True)
        
        return query.all()
    
    async def update_alert_rule(
        self,
        rule_id: str,
        updates: Dict[str, Any]
    ) -> Optional[AlertRule]:
        """Update an alert rule"""
        alert_rule = self.db.query(AlertRule).filter(
            AlertRule.rule_id == rule_id
        ).first()
        
        if not alert_rule:
            return None
        
        for key, value in updates.items():
            if hasattr(alert_rule, key):
                setattr(alert_rule, key, value)
        
        setattr(alert_rule, 'updated_at', datetime.utcnow())
        self.db.commit()
        self.db.refresh(alert_rule)
        
        return alert_rule
    
    async def delete_alert_rule(self, rule_id: str) -> bool:
        """Delete an alert rule"""
        alert_rule = self.db.query(AlertRule).filter(
            AlertRule.rule_id == rule_id
        ).first()
        
        if not alert_rule:
            return False
        
        self.db.delete(alert_rule)
        self.db.commit()
        return True
    
    # Alert Evaluation
    
    async def evaluate_alert_rules(self, execution: WorkflowExecution) -> List[Alert]:
        """Evaluate all alert rules for a workflow execution"""
        triggered_alerts = []
        
        # Get relevant alert rules
        rules = await self.get_alert_rules(
            workflow_id=execution.workflow_id,
            enabled_only=True
        )
        
        for rule in rules:
            try:
                if await self._evaluate_condition(rule, execution):
                    alert = await self._create_alert(rule, execution)
                    if alert:
                        triggered_alerts.append(alert)
            except Exception as e:
                logger.error(f"Error evaluating alert rule {rule.rule_id}: {str(e)}")
        
        return triggered_alerts
    
    async def _evaluate_condition(
        self,
        rule: AlertRule,
        execution: WorkflowExecution
    ) -> bool:
        """Evaluate if an alert condition is met"""
        condition_type = rule.condition_type
        config = rule.condition_config
        
        if condition_type == "execution_failure":
            return execution.status == "failed"
        
        elif condition_type == "performance_degradation":
            # Check if execution time exceeds threshold
            threshold = config.get("execution_time_threshold", 60)  # seconds
            if execution.execution_time and execution.execution_time > threshold:
                return True
            
            # Check if success rate is below threshold
            success_rate_threshold = config.get("success_rate_threshold", 90)  # percentage
            if execution.step_count and execution.success_count is not None:
                current_rate = (execution.success_count / execution.step_count) * 100
                if current_rate < success_rate_threshold:
                    return True
            
            return False
        
        elif condition_type == "resource_threshold":
            # Check resource usage thresholds
            if execution.resource_usage:
                memory_threshold = config.get("memory_threshold_mb", 1000)
                cpu_threshold = config.get("cpu_threshold_percent", 80)
                
                memory_change = execution.resource_usage.get("memory_change_mb", 0)
                cpu_change = execution.resource_usage.get("cpu_change_percent", 0)
                
                if memory_change > memory_threshold or cpu_change > cpu_threshold:
                    return True
            
            return False
        
        elif condition_type == "custom":
            # Custom condition evaluation (can be extended)
            # For now, return False
            return False
        
        return False
    
    async def _create_alert(
        self,
        rule: AlertRule,
        execution: WorkflowExecution
    ) -> Optional[Alert]:
        """Create an alert and send notifications"""
        alert_id = str(uuid.uuid4())
        
        # Generate alert message
        message = self._generate_alert_message(rule, execution)
        
        # Create alert record
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            workflow_id=execution.workflow_id,
            execution_id=execution.execution_id,
            severity=rule.severity,
            message=message,
            details={
                "condition_type": rule.condition_type,
                "condition_config": rule.condition_config,
                "execution_status": execution.status,
                "execution_time": execution.execution_time,
            }
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        # Send notifications
        await self._send_notifications(rule, alert)
        
        return alert
    
    def _generate_alert_message(
        self,
        rule: AlertRule,
        execution: WorkflowExecution
    ) -> str:
        """Generate alert message based on rule and execution"""
        if rule.condition_type == "execution_failure":
            return f"Workflow execution failed: {execution.workflow_id} (Execution: {execution.execution_id})"
        
        elif rule.condition_type == "performance_degradation":
            return f"Performance degradation detected: {execution.workflow_id} - Execution time: {execution.execution_time}s"
        
        elif rule.condition_type == "resource_threshold":
            return f"Resource threshold exceeded: {execution.workflow_id}"
        
        else:
            return f"Alert triggered: {rule.name} for workflow {execution.workflow_id}"
    
    async def _send_notifications(self, rule: AlertRule, alert: Alert):
        """Send notifications via configured channels"""
        for channel_config in rule.notification_channels:
            try:
                channel_id = channel_config.get("channel_id")
                if not channel_id:
                    continue
                
                # Get channel configuration
                channel = self.db.query(NotificationChannel).filter(
                    NotificationChannel.channel_id == channel_id,
                    NotificationChannel.enabled == True
                ).first()
                
                if not channel:
                    logger.warning(f"Notification channel {channel_id} not found or disabled")
                    continue
                
                # Send notification based on channel type
                await self._send_notification(channel, alert)
                
            except Exception as e:
                logger.error(f"Error sending notification: {str(e)}")
    
    async def _send_notification(self, channel: NotificationChannel, alert: Alert):
        """Send notification via a specific channel"""
        channel_type = channel.channel_type
        config = channel.config
        
        if channel_type == "in_app":
            # In-app notifications are already stored in the alerts table
            logger.info(f"In-app alert created: {alert.alert_id}")
            return
        
        elif channel_type == "webhook":
            # Send webhook notification
            import aiohttp
            webhook_url = config.get("url")
            if webhook_url:
                try:
                    async with aiohttp.ClientSession() as session:
                        await session.post(
                            webhook_url,
                            json={
                                "alert_id": alert.alert_id,
                                "severity": alert.severity,
                                "message": alert.message,
                                "details": alert.details,
                                "created_at": alert.created_at.isoformat() if alert.created_at else None,
                            },
                            headers=config.get("headers", {})
                        )
                        logger.info(f"Webhook notification sent: {alert.alert_id}")
                except Exception as e:
                    logger.error(f"Error sending webhook notification: {str(e)}")
        
        elif channel_type == "email":
            # Email notifications (requires email service setup)
            logger.info(f"Email notification would be sent for alert: {alert.alert_id}")
            # TODO: Implement email sending
        
        elif channel_type == "slack":
            # Slack notifications
            logger.info(f"Slack notification would be sent for alert: {alert.alert_id}")
            # TODO: Implement Slack webhook
    
    # Alert Management
    
    async def get_alerts(
        self,
        rule_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[Alert]:
        """Get alerts with filters"""
        query = self.db.query(Alert)
        
        if rule_id:
            query = query.filter(Alert.rule_id == rule_id)
        
        if workflow_id:
            query = query.filter(Alert.workflow_id == workflow_id)
        
        if status:
            query = query.filter(Alert.status == status)
        
        if severity:
            query = query.filter(Alert.severity == severity)
        
        return query.order_by(Alert.created_at.desc()).limit(limit).all()
    
    async def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str
    ) -> Optional[Alert]:
        """Acknowledge an alert"""
        alert = self.db.query(Alert).filter(Alert.alert_id == alert_id).first()
        
        if not alert:
            return None
        
        alert.status = "acknowledged"
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    async def resolve_alert(self, alert_id: str) -> Optional[Alert]:
        """Resolve an alert"""
        alert = self.db.query(Alert).filter(Alert.alert_id == alert_id).first()
        
        if not alert:
            return None
        
        alert.status = "resolved"
        alert.resolved_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    # Notification Channel Management
    
    async def create_notification_channel(
        self,
        name: str,
        channel_type: str,
        config: Dict[str, Any],
        enabled: bool = True
    ) -> NotificationChannel:
        """Create a notification channel"""
        channel_id = str(uuid.uuid4())
        
        channel = NotificationChannel(
            channel_id=channel_id,
            name=name,
            channel_type=channel_type,
            config=config,
            enabled=enabled
        )
        
        self.db.add(channel)
        self.db.commit()
        self.db.refresh(channel)
        
        return channel
    
    async def get_notification_channels(self) -> List[NotificationChannel]:
        """Get all notification channels"""
        return self.db.query(NotificationChannel).all()
    
    async def update_notification_channel(
        self,
        channel_id: str,
        updates: Dict[str, Any]
    ) -> Optional[NotificationChannel]:
        """Update a notification channel"""
        channel = self.db.query(NotificationChannel).filter(
            NotificationChannel.channel_id == channel_id
        ).first()
        
        if not channel:
            return None
        
        for key, value in updates.items():
            if hasattr(channel, key):
                setattr(channel, key, value)
        
        setattr(channel, 'updated_at', datetime.utcnow())
        self.db.commit()
        self.db.refresh(channel)
        
        return channel


"""
Alerting models for monitoring and notifications
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
from core.database import Base


class AlertRule(Base):
    """Alert rule configuration"""
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    workflow_id = Column(String, index=True)  # Optional: specific workflow, or None for all workflows
    condition_type = Column(String, nullable=False)  # execution_failure, performance_degradation, resource_threshold, custom
    condition_config = Column(JSON, nullable=False)  # Condition-specific configuration
    notification_channels = Column(JSON, nullable=False)  # List of notification channel configs
    enabled = Column(Boolean, default=True)
    severity = Column(String, default="medium")  # low, medium, high, critical
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Alert(Base):
    """Alert instances"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, unique=True, index=True)
    rule_id = Column(String, index=True)  # Foreign key to alert_rules
    workflow_id = Column(String, index=True)  # Workflow that triggered the alert
    execution_id = Column(String, index=True)  # Execution that triggered the alert (optional)
    severity = Column(String, nullable=False)  # low, medium, high, critical
    message = Column(Text, nullable=False)
    details = Column(JSON)  # Additional alert details
    status = Column(String, default="active")  # active, acknowledged, resolved
    acknowledged_by = Column(String)  # User who acknowledged
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class NotificationChannel(Base):
    """Notification channel configuration"""
    __tablename__ = "notification_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    channel_type = Column(String, nullable=False)  # email, webhook, slack, in_app
    config = Column(JSON, nullable=False)  # Channel-specific configuration
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


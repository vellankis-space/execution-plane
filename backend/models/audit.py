"""
Audit logging models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index
from sqlalchemy.sql import func
from core.database import Base


class AuditLog(Base):
    """Audit log entry for tracking all system activities"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)  # User who performed the action
    action = Column(String, nullable=False, index=True)  # Action type: create, update, delete, execute, etc.
    resource_type = Column(String, nullable=False, index=True)  # Resource type: agent, workflow, user, etc.
    resource_id = Column(String, index=True)  # ID of the resource affected
    resource_name = Column(String)  # Name of the resource for easier searching
    tenant_id = Column(String, index=True)  # Tenant context
    ip_address = Column(String)  # IP address of the request
    user_agent = Column(String)  # User agent string
    request_method = Column(String)  # HTTP method: GET, POST, PUT, DELETE
    request_path = Column(String)  # API endpoint path
    status_code = Column(Integer)  # HTTP status code
    success = Column(Integer, default=1)  # 1 for success, 0 for failure
    error_message = Column(Text)  # Error message if action failed
    changes = Column(JSON)  # Before/after changes for updates
    metadata = Column(JSON)  # Additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_tenant_time', 'tenant_id', 'created_at'),
    )


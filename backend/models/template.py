"""
Workflow template models
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class WorkflowTemplate(Base):
    """Workflow template for reusable workflow definitions"""
    __tablename__ = "workflow_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    category = Column(String, index=True)  # Category for organization
    tags = Column(JSON, default=list)  # List of tags
    workflow_definition = Column(JSON, nullable=False)  # Workflow definition
    is_public = Column(Boolean, default=False)  # Public templates can be shared
    is_featured = Column(Boolean, default=False)  # Featured templates
    created_by = Column(String, index=True)  # User ID who created the template
    usage_count = Column(Integer, default=0)  # Number of times template was used
    rating = Column(Integer)  # Average rating (1-5)
    rating_count = Column(Integer, default=0)  # Number of ratings
    metadata = Column(JSON, default=dict)  # Additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TemplateUsage(Base):
    """Track template usage"""
    __tablename__ = "template_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    usage_id = Column(String, unique=True, index=True)
    template_id = Column(String, ForeignKey("workflow_templates.template_id"), nullable=False)
    user_id = Column(String, index=True)
    workflow_id = Column(String)  # Workflow created from template
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    template = relationship("WorkflowTemplate", backref="usages")


class TemplateRating(Base):
    """Template ratings and reviews"""
    __tablename__ = "template_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    rating_id = Column(String, unique=True, index=True)
    template_id = Column(String, ForeignKey("workflow_templates.template_id"), nullable=False)
    user_id = Column(String, index=True)
    rating = Column(Integer, nullable=False)  # 1-5
    review = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    template = relationship("WorkflowTemplate", backref="ratings")


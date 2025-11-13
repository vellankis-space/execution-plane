"""
Cost tracking models for API usage and cost analytics
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from core.database import Base


class APICall(Base):
    """Track individual API calls for cost calculation"""
    __tablename__ = "api_calls"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String, unique=True, index=True)
    agent_id = Column(String, index=True)
    workflow_id = Column(String, index=True)
    execution_id = Column(String, index=True)
    provider = Column(String, nullable=False)  # openai, anthropic, groq, etc.
    model = Column(String, nullable=False)
    call_type = Column(String)  # chat, completion, embedding, etc.
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)  # Calculated cost in USD
    metadata = Column(JSON)  # Additional call metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CostBudget(Base):
    """Budget configuration for cost tracking"""
    __tablename__ = "cost_budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    budget_type = Column(String, nullable=False)  # daily, weekly, monthly, total
    amount = Column(Float, nullable=False)  # Budget amount in USD
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    alert_threshold = Column(Float, default=0.8)  # Alert at 80% of budget
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CostAlert(Base):
    """Cost-related alerts"""
    __tablename__ = "cost_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, unique=True, index=True)
    budget_id = Column(String, index=True)
    alert_type = Column(String, nullable=False)  # budget_threshold, budget_exceeded, unusual_spike
    message = Column(Text, nullable=False)
    current_cost = Column(Float, nullable=False)
    budget_amount = Column(Float, nullable=False)
    percentage_used = Column(Float, nullable=False)
    status = Column(String, default="active")  # active, acknowledged, resolved
    created_at = Column(DateTime(timezone=True), server_default=func.now())


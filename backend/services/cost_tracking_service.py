"""
Cost tracking service for API usage and cost analytics
"""
import uuid
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta

from models.cost_tracking import APICall, CostBudget, CostAlert
from models.agent import Agent as AgentModel

logger = logging.getLogger(__name__)


# Pricing per 1M tokens (as of 2024, approximate)
PRICING = {
    "openai": {
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
        "gpt-4o": {"input": 5.0, "output": 15.0},
    },
    "anthropic": {
        "claude-3-opus": {"input": 15.0, "output": 75.0},
        "claude-3-sonnet": {"input": 3.0, "output": 15.0},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
        "claude-sonnet-4-5": {"input": 3.0, "output": 15.0},
    },
    "groq": {
        "llama-3-70b": {"input": 0.59, "output": 0.79},
        "mixtral-8x7b": {"input": 0.24, "output": 0.24},
    },
}


class CostTrackingService:
    """Service for tracking API costs and usage"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost for an API call"""
        try:
            provider_pricing = PRICING.get(provider.lower(), {})
            model_pricing = provider_pricing.get(model.lower(), {})
            
            if not model_pricing:
                # Default pricing if model not found
                logger.warning(f"Pricing not found for {provider}/{model}, using defaults")
                input_price = 1.0  # $1 per 1M tokens
                output_price = 2.0  # $2 per 1M tokens
            else:
                input_price = model_pricing.get("input", 1.0)
                output_price = model_pricing.get("output", 2.0)
            
            # Calculate cost: (tokens / 1,000,000) * price_per_1M
            input_cost = (input_tokens / 1_000_000) * input_price
            output_cost = (output_tokens / 1_000_000) * output_price
            total_cost = input_cost + output_cost
            
            return round(total_cost, 6)  # Round to 6 decimal places
        except Exception as e:
            logger.error(f"Error calculating cost: {str(e)}")
            return 0.0
    
    async def track_api_call(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        agent_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        call_type: str = "chat",
        metadata: Optional[Dict[str, Any]] = None
    ) -> APICall:
        """Track an API call and calculate cost"""
        call_id = str(uuid.uuid4())
        total_tokens = input_tokens + output_tokens
        cost = self.calculate_cost(provider, model, input_tokens, output_tokens)
        
        
        api_call = APICall(
            call_id=call_id,
            agent_id=agent_id,
            workflow_id=workflow_id,
            execution_id=execution_id,
            provider=provider,
            model=model,
            call_type=call_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost=cost,
            call_metadata=metadata or {}
        )
        
        self.db.add(api_call)
        self.db.commit()
        self.db.refresh(api_call)
        
        # Check budgets and create alerts if needed
        await self._check_budgets(api_call)
        
        return api_call
    
    async def get_cost_summary(
        self,
        agent_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get cost summary for a time period"""
        query = self.db.query(APICall)
        
        if agent_id:
            query = query.filter(APICall.agent_id == agent_id)
        
        if workflow_id:
            query = query.filter(APICall.workflow_id == workflow_id)
        
        if start_date:
            query = query.filter(APICall.created_at >= start_date)
        
        if end_date:
            query = query.filter(APICall.created_at <= end_date)
        
        calls = query.all()
        
        total_cost = sum(call.cost for call in calls)
        total_tokens = sum(call.total_tokens for call in calls)
        total_calls = len(calls)
        
        # Group by provider
        by_provider = {}
        for call in calls:
            provider = call.provider
            if provider not in by_provider:
                by_provider[provider] = {
                    "cost": 0.0,
                    "tokens": 0,
                    "calls": 0
                }
            by_provider[provider]["cost"] += call.cost
            by_provider[provider]["tokens"] += call.total_tokens
            by_provider[provider]["calls"] += 1
        
        # Group by model
        by_model = {}
        for call in calls:
            model_key = f"{call.provider}/{call.model}"
            if model_key not in by_model:
                by_model[model_key] = {
                    "cost": 0.0,
                    "tokens": 0,
                    "calls": 0
                }
            by_model[model_key]["cost"] += call.cost
            by_model[model_key]["tokens"] += call.total_tokens
            by_model[model_key]["calls"] += 1
        
        return {
            "total_cost": round(total_cost, 2),
            "total_tokens": total_tokens,
            "total_calls": total_calls,
            "by_provider": by_provider,
            "by_model": by_model,
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None,
            }
        }
    
    async def get_cost_trends(
        self,
        days: int = 30,
        agent_id: Optional[str] = None,
        workflow_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get cost trends over time"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = self.db.query(APICall)
        
        if agent_id:
            query = query.filter(APICall.agent_id == agent_id)
        
        if workflow_id:
            query = query.filter(APICall.workflow_id == workflow_id)
        
        query = query.filter(
            and_(
                APICall.created_at >= start_date,
                APICall.created_at <= end_date
            )
        )
        
        calls = query.all()
        
        # Group by day
        daily_costs = {}
        for call in calls:
            day = call.created_at.date().isoformat()
            if day not in daily_costs:
                daily_costs[day] = {
                    "date": day,
                    "cost": 0.0,
                    "tokens": 0,
                    "calls": 0
                }
            daily_costs[day]["cost"] += call.cost
            daily_costs[day]["tokens"] += call.total_tokens
            daily_costs[day]["calls"] += 1
        
        return sorted(daily_costs.values(), key=lambda x: x["date"])
    
    async def _check_budgets(self, api_call: APICall):
        """Check if API call triggers any budget alerts"""
        # Get active budgets
        budgets = self.db.query(CostBudget).filter(
            CostBudget.enabled == True
        ).all()
        
        for budget in budgets:
            # Calculate current period cost
            period_start = budget.period_start or datetime.utcnow().replace(day=1)
            period_end = budget.period_end or datetime.utcnow()
            
            current_cost = self.db.query(func.sum(APICall.cost)).filter(
                and_(
                    APICall.created_at >= period_start,
                    APICall.created_at <= period_end
                )
            ).scalar() or 0.0
            
            percentage_used = (current_cost / budget.amount * 100) if budget.amount > 0 else 0
            
            # Check if threshold exceeded
            if percentage_used >= (budget.alert_threshold * 100):
                # Check if alert already exists
                existing_alert = self.db.query(CostAlert).filter(
                    and_(
                        CostAlert.budget_id == budget.budget_id,
                        CostAlert.status == "active",
                        CostAlert.alert_type == "budget_threshold"
                    )
                ).first()
                
                if not existing_alert:
                    # Create alert
                    alert = CostAlert(
                        alert_id=str(uuid.uuid4()),
                        budget_id=budget.budget_id,
                        alert_type="budget_threshold",
                        message=f"Budget threshold reached: {percentage_used:.1f}% of {budget.name}",
                        current_cost=current_cost,
                        budget_amount=budget.amount,
                        percentage_used=percentage_used
                    )
                    self.db.add(alert)
                    self.db.commit()
            
            # Check if budget exceeded
            if current_cost > budget.amount:
                existing_alert = self.db.query(CostAlert).filter(
                    and_(
                        CostAlert.budget_id == budget.budget_id,
                        CostAlert.status == "active",
                        CostAlert.alert_type == "budget_exceeded"
                    )
                ).first()
                
                if not existing_alert:
                    alert = CostAlert(
                        alert_id=str(uuid.uuid4()),
                        budget_id=budget.budget_id,
                        alert_type="budget_exceeded",
                        message=f"Budget exceeded: ${current_cost:.2f} of ${budget.amount:.2f} for {budget.name}",
                        current_cost=current_cost,
                        budget_amount=budget.amount,
                        percentage_used=percentage_used
                    )
                    self.db.add(alert)
                    self.db.commit()
    
    # Budget Management
    
    async def create_budget(
        self,
        name: str,
        budget_type: str,
        amount: float,
        alert_threshold: float = 0.8,
        description: Optional[str] = None,
        enabled: bool = True
    ) -> CostBudget:
        """Create a cost budget"""
        budget_id = str(uuid.uuid4())
        
        # Calculate period based on budget type
        now = datetime.utcnow()
        if budget_type == "daily":
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=1)
        elif budget_type == "weekly":
            period_start = now - timedelta(days=now.weekday())
            period_start = period_start.replace(hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + timedelta(days=7)
        elif budget_type == "monthly":
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if period_start.month == 12:
                period_end = period_start.replace(year=period_start.year + 1, month=1)
            else:
                period_end = period_start.replace(month=period_start.month + 1)
        else:  # total
            period_start = None
            period_end = None
        
        budget = CostBudget(
            budget_id=budget_id,
            name=name,
            description=description,
            budget_type=budget_type,
            amount=amount,
            period_start=period_start,
            period_end=period_end,
            alert_threshold=alert_threshold,
            enabled=enabled
        )
        
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        
        return budget
    
    async def get_budgets(self) -> List[CostBudget]:
        """Get all budgets"""
        return self.db.query(CostBudget).all()
    
    async def get_budget_status(self, budget_id: str) -> Dict[str, Any]:
        """Get current status of a budget"""
        budget = self.db.query(CostBudget).filter(
            CostBudget.budget_id == budget_id
        ).first()
        
        if not budget:
            raise ValueError("Budget not found")
        
        period_start = budget.period_start or datetime.utcnow().replace(day=1)
        period_end = budget.period_end or datetime.utcnow()
        
        current_cost = self.db.query(func.sum(APICall.cost)).filter(
            and_(
                APICall.created_at >= period_start,
                APICall.created_at <= period_end
            )
        ).scalar() or 0.0
        
        percentage_used = (current_cost / budget.amount * 100) if budget.amount > 0 else 0
        remaining = budget.amount - current_cost
        
        return {
            "budget_id": budget.budget_id,
            "name": budget.name,
            "budget_type": budget.budget_type,
            "amount": budget.amount,
            "current_cost": round(current_cost, 2),
            "remaining": round(remaining, 2),
            "percentage_used": round(percentage_used, 2),
            "period_start": period_start.isoformat() if period_start else None,
            "period_end": period_end.isoformat() if period_end else None,
        }


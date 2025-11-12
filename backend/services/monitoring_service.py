import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text
from collections import defaultdict

from models.workflow import WorkflowExecution, StepExecution
from schemas.workflow import WorkflowExecutionResponse

# Configure logging
logger = logging.getLogger(__name__)


class MonitoringService:
    def __init__(self, db: Session):
        self.db = db

    async def get_workflow_execution_metrics(self, workflow_id: Optional[str] = None, 
                                           start_time: Optional[datetime] = None,
                                           end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get metrics for workflow executions"""
        try:
            query = self.db.query(WorkflowExecution)
            
            # Filter by workflow ID if provided
            if workflow_id:
                query = query.filter(WorkflowExecution.workflow_id == workflow_id)
            
            # Filter by time range if provided
            if start_time:
                query = query.filter(WorkflowExecution.created_at >= start_time)
            if end_time:
                query = query.filter(WorkflowExecution.created_at <= end_time)
            
            executions = query.all()
            
            if not executions:
                return {
                    "total_executions": 0,
                    "success_rate": 0,
                    "average_duration": 0,
                    "executions_by_status": {},
                    "executions_by_day": []
                }
            
            # Calculate metrics
            total_executions = len(executions)
            completed_executions = [e for e in executions if e.status == "completed"]
            success_rate = len(completed_executions) / total_executions if total_executions > 0 else 0
            
            # Calculate average duration
            durations = []
            for execution in completed_executions:
                if execution.started_at and execution.completed_at:
                    duration = (execution.completed_at - execution.started_at).total_seconds()
                    durations.append(duration)
            
            average_duration = sum(durations) / len(durations) if durations else 0
            
            # Group by status
            status_counts = {}
            for execution in executions:
                status_counts[execution.status] = status_counts.get(execution.status, 0) + 1
            
            # Group by day for time series data
            executions_by_day = {}
            for execution in executions:
                day = execution.created_at.date().isoformat()
                executions_by_day[day] = executions_by_day.get(day, 0) + 1
            
            executions_by_day_list = [
                {"date": date, "count": count} 
                for date, count in sorted(executions_by_day.items())
            ]
            
            return {
                "total_executions": total_executions,
                "success_rate": round(success_rate * 100, 2),
                "average_duration": round(average_duration, 2),
                "executions_by_status": status_counts,
                "executions_by_day": executions_by_day_list
            }
        except Exception as e:
            logger.error(f"Error getting workflow execution metrics: {str(e)}")
            raise

    async def get_step_execution_metrics(self, workflow_id: Optional[str] = None,
                                       start_time: Optional[datetime] = None,
                                       end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get metrics for step executions"""
        try:
            # Join StepExecution with WorkflowExecution to filter by workflow_id if needed
            query = self.db.query(StepExecution)
            
            if workflow_id or start_time or end_time:
                query = query.join(WorkflowExecution)
            
            # Filter by workflow ID if provided
            if workflow_id:
                query = query.filter(WorkflowExecution.workflow_id == workflow_id)
            
            # Filter by time range if provided
            if start_time:
                query = query.filter(WorkflowExecution.created_at >= start_time)
            if end_time:
                query = query.filter(WorkflowExecution.created_at <= end_time)
            
            step_executions = query.all()
            
            if not step_executions:
                return {
                    "total_steps": 0,
                    "success_rate": 0,
                    "average_duration": 0,
                    "steps_by_status": {},
                    "steps_by_agent": {}
                }
            
            # Calculate metrics
            total_steps = len(step_executions)
            completed_steps = [s for s in step_executions if s.status == "completed"]
            success_rate = len(completed_steps) / total_steps if total_steps > 0 else 0
            
            # Calculate average duration
            durations = []
            for step in completed_steps:
                if step.started_at and step.completed_at:
                    duration = (step.completed_at - step.started_at).total_seconds()
                    durations.append(duration)
            
            average_duration = sum(durations) / len(durations) if durations else 0
            
            # Group by status
            status_counts = {}
            for step in step_executions:
                status_counts[step.status] = status_counts.get(step.status, 0) + 1
            
            # Group by agent
            agent_counts = {}
            for step in step_executions:
                agent_counts[step.agent_id] = agent_counts.get(step.agent_id, 0) + 1
            
            return {
                "total_steps": total_steps,
                "success_rate": round(success_rate * 100, 2),
                "average_duration": round(average_duration, 2),
                "steps_by_status": status_counts,
                "steps_by_agent": agent_counts
            }
        except Exception as e:
            logger.error(f"Error getting step execution metrics: {str(e)}")
            raise

    async def get_workflow_performance_report(self, workflow_id: str, 
                                            days: int = 30) -> Dict[str, Any]:
        """Get a comprehensive performance report for a workflow"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # Get workflow execution metrics
            workflow_metrics = await self.get_workflow_execution_metrics(
                workflow_id=workflow_id,
                start_time=start_time,
                end_time=end_time
            )
            
            # Get step execution metrics
            step_metrics = await self.get_step_execution_metrics(
                workflow_id=workflow_id,
                start_time=start_time,
                end_time=end_time
            )
            
            # Get recent executions for detailed view
            recent_executions = self.db.query(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.workflow_id == workflow_id,
                    WorkflowExecution.created_at >= start_time,
                    WorkflowExecution.created_at <= end_time
                )
            ).order_by(WorkflowExecution.created_at.desc()).limit(10).all()
            
            recent_execution_data = []
            for execution in recent_executions:
                # Load step executions
                execution.step_executions = self.db.query(StepExecution).filter(
                    StepExecution.execution_id == execution.execution_id
                ).all()
                
                recent_execution_data.append({
                    "execution_id": execution.execution_id,
                    "status": execution.status,
                    "started_at": execution.started_at.isoformat() if execution.started_at else None,
                    "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                    "duration": (execution.completed_at - execution.started_at).total_seconds() if execution.started_at and execution.completed_at else None,
                    "step_count": len(execution.step_executions),
                    "failed_steps": len([s for s in execution.step_executions if s.status == "failed"])
                })
            
            return {
                "workflow_id": workflow_id,
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "days": days
                },
                "workflow_metrics": workflow_metrics,
                "step_metrics": step_metrics,
                "recent_executions": recent_execution_data
            }
        except Exception as e:
            logger.error(f"Error generating workflow performance report: {str(e)}")
            raise

    async def get_system_health_metrics(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        try:
            # Get total counts
            total_workflows = self.db.query(func.count(WorkflowExecution.id)).scalar()
            total_executions = self.db.query(func.count(WorkflowExecution.id)).scalar()
            total_step_executions = self.db.query(func.count(StepExecution.id)).scalar()
            
            # Get recent failed executions (last 24 hours)
            twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
            recent_failed_executions = self.db.query(func.count(WorkflowExecution.id)).filter(
                and_(
                    WorkflowExecution.status == "failed",
                    WorkflowExecution.created_at >= twenty_four_hours_ago
                )
            ).scalar()
            
            # Get recent failed steps (last 24 hours)
            recent_failed_steps = self.db.query(func.count(StepExecution.id)).join(WorkflowExecution).filter(
                and_(
                    StepExecution.status == "failed",
                    WorkflowExecution.created_at >= twenty_four_hours_ago
                )
            ).scalar()
            
            return {
                "total_workflows": total_workflows,
                "total_executions": total_executions,
                "total_step_executions": total_step_executions,
                "recent_failed_executions_24h": recent_failed_executions,
                "recent_failed_steps_24h": recent_failed_steps,
                "health_status": "healthy" if recent_failed_executions < 5 and recent_failed_steps < 10 else "degraded"
            }
        except Exception as e:
            logger.error(f"Error getting system health metrics: {str(e)}")
            raise
    
    async def get_detailed_workflow_analytics(self, workflow_id: str, 
                                           days: int = 30) -> Dict[str, Any]:
        """Get detailed analytics for a specific workflow"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # Get all executions for this workflow in the time period
            executions = self.db.query(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.workflow_id == workflow_id,
                    WorkflowExecution.created_at >= start_time,
                    WorkflowExecution.created_at <= end_time
                )
            ).all()
            
            if not executions:
                return {
                    "workflow_id": workflow_id,
                    "period": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat(),
                        "days": days
                    },
                    "total_executions": 0,
                    "success_rate": 0,
                    "execution_trends": [],
                    "step_performance": [],
                    "bottlenecks": [],
                    "resource_usage": {}
                }
            
            # Calculate execution trends over time
            executions_by_day = defaultdict(int)
            success_by_day = defaultdict(int)
            
            for execution in executions:
                day = execution.created_at.date().isoformat()
                executions_by_day[day] += 1
                if execution.status == "completed":
                    success_by_day[day] += 1
            
            execution_trends = []
            for day in sorted(executions_by_day.keys()):
                total = executions_by_day[day]
                success = success_by_day[day]
                rate = (success / total * 100) if total > 0 else 0
                execution_trends.append({
                    "date": day,
                    "total_executions": total,
                    "success_rate": round(rate, 2)
                })
            
            # Get step performance data
            step_executions = self.db.query(StepExecution).join(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.workflow_id == workflow_id,
                    WorkflowExecution.created_at >= start_time,
                    WorkflowExecution.created_at <= end_time
                )
            ).all()
            
            # Analyze step performance
            step_durations = defaultdict(list)
            step_success_rates = defaultdict(lambda: {"total": 0, "success": 0})
            
            for step in step_executions:
                # Calculate duration if both start and end times are available
                if step.started_at and step.completed_at:
                    duration = (step.completed_at - step.started_at).total_seconds()
                    step_durations[step.step_id].append(duration)
                
                # Track success rates
                step_success_rates[step.step_id]["total"] += 1
                if step.status == "completed":
                    step_success_rates[step.step_id]["success"] += 1
            
            # Prepare step performance data
            step_performance = []
            for step_id, durations in step_durations.items():
                avg_duration = sum(durations) / len(durations) if durations else 0
                success_data = step_success_rates[step_id]
                success_rate = (success_data["success"] / success_data["total"] * 100) if success_data["total"] > 0 else 0
                
                step_performance.append({
                    "step_id": step_id,
                    "average_duration": round(avg_duration, 2),
                    "success_rate": round(success_rate, 2),
                    "execution_count": len(durations),
                    "min_duration": round(min(durations), 2) if durations else 0,
                    "max_duration": round(max(durations), 2) if durations else 0
                })
            
            # Identify bottlenecks (steps with high duration or low success rate)
            bottlenecks = []
            for step_perf in step_performance:
                if step_perf["average_duration"] > 30 or step_perf["success_rate"] < 90:
                    bottlenecks.append({
                        "step_id": step_perf["step_id"],
                        "issue": "high_duration" if step_perf["average_duration"] > 30 else "low_success_rate",
                        "value": step_perf["average_duration"] if step_perf["average_duration"] > 30 else step_perf["success_rate"]
                    })
            
            # Resource usage by agent
            agent_usage = defaultdict(int)
            for step in step_executions:
                agent_usage[step.agent_id] += 1
            
            return {
                "workflow_id": workflow_id,
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "days": days
                },
                "total_executions": len(executions),
                "success_rate": round(len([e for e in executions if e.status == "completed"]) / len(executions) * 100, 2) if executions else 0,
                "execution_trends": execution_trends,
                "step_performance": step_performance,
                "bottlenecks": bottlenecks,
                "resource_usage": dict(agent_usage)
            }
        except Exception as e:
            logger.error(f"Error getting detailed workflow analytics: {str(e)}")
            raise
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        try:
            # Get currently running executions
            running_executions = self.db.query(func.count(WorkflowExecution.id)).filter(
                WorkflowExecution.status == "running"
            ).scalar()
            
            # Get recently started executions (last 5 minutes)
            five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
            recent_executions = self.db.query(func.count(WorkflowExecution.id)).filter(
                WorkflowExecution.created_at >= five_minutes_ago
            ).scalar()
            
            # Get active step executions
            active_steps = self.db.query(func.count(StepExecution.id)).filter(
                StepExecution.status == "running"
            ).scalar()
            
            # Get system load indicators
            failed_executions_last_hour = self.db.query(func.count(WorkflowExecution.id)).filter(
                and_(
                    WorkflowExecution.status == "failed",
                    WorkflowExecution.created_at >= datetime.utcnow() - timedelta(hours=1)
                )
            ).scalar()
            
            return {
                "running_executions": running_executions,
                "recent_executions": recent_executions,
                "active_steps": active_steps,
                "failed_executions_last_hour": failed_executions_last_hour,
                "system_load": "high" if failed_executions_last_hour > 3 or running_executions > 10 else "normal"
            }
        except Exception as e:
            logger.error(f"Error getting real-time metrics: {str(e)}")
            raise
    
    async def get_workflow_comparison_metrics(self, workflow_ids: List[str], 
                                           days: int = 30) -> Dict[str, Any]:
        """Compare metrics across multiple workflows"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            comparison_data = []
            
            for workflow_id in workflow_ids:
                # Get execution metrics for each workflow
                executions = self.db.query(WorkflowExecution).filter(
                    and_(
                        WorkflowExecution.workflow_id == workflow_id,
                        WorkflowExecution.created_at >= start_time,
                        WorkflowExecution.created_at <= end_time
                    )
                ).all()
                
                if not executions:
                    comparison_data.append({
                        "workflow_id": workflow_id,
                        "total_executions": 0,
                        "success_rate": 0,
                        "average_duration": 0
                    })
                    continue
                
                # Calculate metrics
                total_executions = len(executions)
                completed_executions = [e for e in executions if e.status == "completed"]
                success_rate = len(completed_executions) / total_executions if total_executions > 0 else 0
                
                # Calculate average duration
                durations = []
                for execution in completed_executions:
                    if execution.started_at and execution.completed_at:
                        duration = (execution.completed_at - execution.started_at).total_seconds()
                        durations.append(duration)
                
                average_duration = sum(durations) / len(durations) if durations else 0
                
                comparison_data.append({
                    "workflow_id": workflow_id,
                    "total_executions": total_executions,
                    "success_rate": round(success_rate * 100, 2),
                    "average_duration": round(average_duration, 2)
                })
            
            return {
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "days": days
                },
                "workflows": comparison_data
            }
        except Exception as e:
            logger.error(f"Error getting workflow comparison metrics: {str(e)}")
            raise
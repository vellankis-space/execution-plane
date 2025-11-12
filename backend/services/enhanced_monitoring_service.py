import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text, desc
from collections import defaultdict
import json

from models.workflow import WorkflowExecution, StepExecution, ExecutionLog
from schemas.workflow import WorkflowExecutionResponse

# Configure logging
logger = logging.getLogger(__name__)


class EnhancedMonitoringService:
    def __init__(self, db: Session):
        self.db = db

    async def get_enhanced_workflow_metrics(self, workflow_id: Optional[str] = None, 
                                         start_time: Optional[datetime] = None,
                                         end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get enhanced metrics for workflow executions with resource usage and performance data"""
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
                    "average_step_count": 0,
                    "average_success_count": 0,
                    "average_failure_count": 0,
                    "resource_usage": {
                        "avg_memory_change_mb": 0,
                        "avg_cpu_change_percent": 0
                    },
                    "executions_by_status": {},
                    "executions_by_day": []
                }
            
            # Convert to dict objects for easier processing
            execution_dicts = []
            for e in executions:
                execution_dicts.append({
                    "id": e.id,
                    "execution_id": e.execution_id,
                    "workflow_id": e.workflow_id,
                    "status": e.status,
                    "input_data": e.input_data,
                    "output_data": e.output_data,
                    "error_message": e.error_message,
                    "started_at": e.started_at,
                    "completed_at": e.completed_at,
                    "created_at": e.created_at,
                    "execution_time": e.execution_time,
                    "step_count": e.step_count,
                    "success_count": e.success_count,
                    "failure_count": e.failure_count,
                    "retry_count": e.retry_count,
                    "resource_usage": e.resource_usage
                })
            
            # Calculate metrics
            total_executions = len(execution_dicts)
            completed_executions = [e for e in execution_dicts if e["status"] == "completed"]
            success_rate = len(completed_executions) / total_executions if total_executions > 0 else 0
            
            # Calculate average duration
            durations = []
            step_counts = []
            success_counts = []
            failure_counts = []
            memory_changes = []
            cpu_changes = []
            
            for execution in completed_executions:
                if execution["started_at"] is not None and execution["completed_at"] is not None:
                    duration = (execution["completed_at"] - execution["started_at"]).total_seconds()
                    durations.append(duration)
                
                if execution["step_count"] is not None:
                    step_counts.append(execution["step_count"])
                
                if execution["success_count"] is not None:
                    success_counts.append(execution["success_count"])
                
                if execution["failure_count"] is not None:
                    failure_counts.append(execution["failure_count"])
                
                if execution["resource_usage"] is not None:
                    try:
                        resource_data = execution["resource_usage"]
                        if isinstance(resource_data, str):
                            resource_data = json.loads(resource_data)
                        
                        if "memory_change_mb" in resource_data:
                            memory_changes.append(resource_data["memory_change_mb"])
                        
                        if "cpu_change_percent" in resource_data:
                            cpu_changes.append(resource_data["cpu_change_percent"])
                    except Exception as e:
                        logger.warning(f"Error parsing resource usage data: {str(e)}")
            
            average_duration = sum(durations) / len(durations) if durations else 0
            average_step_count = sum(step_counts) / len(step_counts) if step_counts else 0
            average_success_count = sum(success_counts) / len(success_counts) if success_counts else 0
            average_failure_count = sum(failure_counts) / len(failure_counts) if failure_counts else 0
            avg_memory_change = sum(memory_changes) / len(memory_changes) if memory_changes else 0
            avg_cpu_change = sum(cpu_changes) / len(cpu_changes) if cpu_changes else 0
            
            # Group by status
            status_counts = {}
            for execution in execution_dicts:
                status_counts[execution["status"]] = status_counts.get(execution["status"], 0) + 1
            
            # Group by day for time series data
            executions_by_day = {}
            for execution in execution_dicts:
                day = execution["created_at"].date().isoformat()
                executions_by_day[day] = executions_by_day.get(day, 0) + 1
            
            executions_by_day_list = [
                {"date": date, "count": count} 
                for date, count in sorted(executions_by_day.items())
            ]
            
            return {
                "total_executions": total_executions,
                "success_rate": round(success_rate * 100, 2),
                "average_duration": round(average_duration, 2),
                "average_step_count": round(average_step_count, 2),
                "average_success_count": round(average_success_count, 2),
                "average_failure_count": round(average_failure_count, 2),
                "resource_usage": {
                    "avg_memory_change_mb": round(avg_memory_change, 2),
                    "avg_cpu_change_percent": round(avg_cpu_change, 2)
                },
                "executions_by_status": status_counts,
                "executions_by_day": executions_by_day_list
            }
        except Exception as e:
            logger.error(f"Error getting enhanced workflow execution metrics: {str(e)}")
            raise

    async def get_enhanced_step_metrics(self, workflow_id: Optional[str] = None,
                                     start_time: Optional[datetime] = None,
                                     end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get enhanced metrics for step executions with resource usage data"""
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
                    "average_memory_usage": 0,
                    "average_cpu_usage": 0,
                    "average_io_operations": 0,
                    "average_network_requests": 0,
                    "steps_by_status": {},
                    "steps_by_agent": {}
                }
            
            # Convert to dict objects for easier processing
            step_dicts = []
            for s in step_executions:
                step_dicts.append({
                    "id": s.id,
                    "step_id": s.step_id,
                    "execution_id": s.execution_id,
                    "agent_id": s.agent_id,
                    "status": s.status,
                    "input_data": s.input_data,
                    "output_data": s.output_data,
                    "error_message": s.error_message,
                    "started_at": s.started_at,
                    "completed_at": s.completed_at,
                    "created_at": s.created_at,
                    "execution_time": s.execution_time,
                    "retry_count": s.retry_count,
                    "memory_usage": s.memory_usage,
                    "cpu_usage": s.cpu_usage,
                    "io_operations": s.io_operations,
                    "network_requests": s.network_requests
                })
            
            # Calculate metrics
            total_steps = len(step_dicts)
            completed_steps = [s for s in step_dicts if s["status"] == "completed"]
            success_rate = len(completed_steps) / total_steps if total_steps > 0 else 0
            
            # Calculate average duration
            durations = []
            memory_usages = []
            cpu_usages = []
            io_operations = []
            network_requests = []
            
            for step in completed_steps:
                if step["started_at"] is not None and step["completed_at"] is not None:
                    duration = (step["completed_at"] - step["started_at"]).total_seconds()
                    durations.append(duration)
                
                if step["memory_usage"] is not None:
                    memory_usages.append(step["memory_usage"])
                
                if step["cpu_usage"] is not None:
                    cpu_usages.append(step["cpu_usage"])
                
                if step["io_operations"] is not None:
                    io_operations.append(step["io_operations"])
                
                if step["network_requests"] is not None:
                    network_requests.append(step["network_requests"])
            
            average_duration = sum(durations) / len(durations) if durations else 0
            average_memory_usage = sum(memory_usages) / len(memory_usages) if memory_usages else 0
            average_cpu_usage = sum(cpu_usages) / len(cpu_usages) if cpu_usages else 0
            average_io_ops = sum(io_operations) / len(io_operations) if io_operations else 0
            average_network_reqs = sum(network_requests) / len(network_requests) if network_requests else 0
            
            # Group by status
            status_counts = {}
            for step in step_dicts:
                status_counts[step["status"]] = status_counts.get(step["status"], 0) + 1
            
            # Group by agent
            agent_counts = {}
            for step in step_dicts:
                agent_counts[step["agent_id"]] = agent_counts.get(step["agent_id"], 0) + 1
            
            return {
                "total_steps": total_steps,
                "success_rate": round(success_rate * 100, 2),
                "average_duration": round(average_duration, 2),
                "average_memory_usage": round(average_memory_usage, 2),
                "average_cpu_usage": round(average_cpu_usage, 2),
                "average_io_operations": round(average_io_ops, 2),
                "average_network_requests": round(average_network_reqs, 2),
                "steps_by_status": status_counts,
                "steps_by_agent": agent_counts
            }
        except Exception as e:
            logger.error(f"Error getting enhanced step execution metrics: {str(e)}")
            raise

    async def get_performance_bottlenecks(self, workflow_id: str, 
                                       days: int = 30) -> Dict[str, Any]:
        """Identify performance bottlenecks in workflow executions"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # Get step executions for this workflow
            step_executions = self.db.query(StepExecution).join(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.workflow_id == workflow_id,
                    WorkflowExecution.created_at >= start_time,
                    WorkflowExecution.created_at <= end_time
                )
            ).all()
            
            if not step_executions:
                return {
                    "workflow_id": workflow_id,
                    "bottlenecks": []
                }
            
            # Convert to dict objects for easier processing
            step_dicts = []
            for s in step_executions:
                step_dicts.append({
                    "id": s.id,
                    "step_id": s.step_id,
                    "execution_id": s.execution_id,
                    "agent_id": s.agent_id,
                    "status": s.status,
                    "input_data": s.input_data,
                    "output_data": s.output_data,
                    "error_message": s.error_message,
                    "started_at": s.started_at,
                    "completed_at": s.completed_at,
                    "created_at": s.created_at,
                    "execution_time": s.execution_time,
                    "retry_count": s.retry_count,
                    "memory_usage": s.memory_usage,
                    "cpu_usage": s.cpu_usage,
                    "io_operations": s.io_operations,
                    "network_requests": s.network_requests
                })
            
            # Analyze step performance
            step_metrics = defaultdict(list)
            
            for step in step_dicts:
                # Calculate duration if both start and end times are available
                if step["started_at"] is not None and step["completed_at"] is not None:
                    duration = (step["completed_at"] - step["started_at"]).total_seconds()
                    step_metrics[step["step_id"]].append({
                        "duration": duration,
                        "status": step["status"],
                        "memory_usage": step["memory_usage"],
                        "cpu_usage": step["cpu_usage"]
                    })
            
            # Identify bottlenecks
            bottlenecks = []
            for step_id, metrics in step_metrics.items():
                if not metrics:
                    continue
                
                # Calculate averages
                durations = [m["duration"] for m in metrics]
                memory_usages = [m["memory_usage"] for m in metrics if m["memory_usage"] is not None]
                cpu_usages = [m["cpu_usage"] for m in metrics if m["cpu_usage"] is not None]
                
                avg_duration = sum(durations) / len(durations) if durations else 0
                avg_memory = sum(memory_usages) / len(memory_usages) if memory_usages else 0
                avg_cpu = sum(cpu_usages) / len(cpu_usages) if cpu_usages else 0
                
                # Identify potential bottlenecks
                if avg_duration > 30:  # More than 30 seconds average
                    bottlenecks.append({
                        "step_id": step_id,
                        "issue_type": "high_duration",
                        "average_duration": round(avg_duration, 2),
                        "severity": "high" if avg_duration > 60 else "medium"
                    })
                
                if avg_memory > 100:  # More than 100 MB average
                    bottlenecks.append({
                        "step_id": step_id,
                        "issue_type": "high_memory_usage",
                        "average_memory_usage": round(avg_memory, 2),
                        "severity": "high" if avg_memory > 200 else "medium"
                    })
                
                if avg_cpu > 80:  # More than 80% CPU average
                    bottlenecks.append({
                        "step_id": step_id,
                        "issue_type": "high_cpu_usage",
                        "average_cpu_usage": round(avg_cpu, 2),
                        "severity": "high" if avg_cpu > 90 else "medium"
                    })
            
            return {
                "workflow_id": workflow_id,
                "bottlenecks": bottlenecks
            }
        except Exception as e:
            logger.error(f"Error identifying performance bottlenecks: {str(e)}")
            raise

    async def get_execution_logs(self, execution_id: str, 
                              log_level: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get execution logs for a specific workflow execution"""
        try:
            query = self.db.query(ExecutionLog).filter(
                ExecutionLog.execution_id == execution_id
            ).order_by(ExecutionLog.timestamp)
            
            if log_level:
                query = query.filter(ExecutionLog.log_level == log_level)
            
            logs = query.all()
            
            return [
                {
                    "id": log.id,
                    "log_level": log.log_level,
                    "message": log.message,
                    "timestamp": log.timestamp.isoformat() if log.timestamp is not None else None,
                    "metadata": log.log_metadata
                }
                for log in logs
            ]
        except Exception as e:
            logger.error(f"Error retrieving execution logs: {str(e)}")
            raise

    async def get_resource_usage_trends(self, workflow_id: str, 
                                     days: int = 30) -> Dict[str, Any]:
        """Get resource usage trends over time for a workflow"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # Get workflow executions with resource usage data
            executions = self.db.query(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.workflow_id == workflow_id,
                    WorkflowExecution.created_at >= start_time,
                    WorkflowExecution.created_at <= end_time,
                    WorkflowExecution.resource_usage.isnot(None)
                )
            ).order_by(WorkflowExecution.created_at).all()
            
            if not executions:
                return {
                    "workflow_id": workflow_id,
                    "memory_usage_trend": [],
                    "cpu_usage_trend": []
                }
            
            # Extract resource usage data over time
            memory_trend = []
            cpu_trend = []
            
            for execution in executions:
                try:
                    resource_data = execution.resource_usage
                    if isinstance(resource_data, str):
                        resource_data = json.loads(resource_data)
                    
                    timestamp = execution.created_at.isoformat()
                    
                    if "memory_change_mb" in resource_data:
                        memory_trend.append({
                            "timestamp": timestamp,
                            "memory_change_mb": resource_data["memory_change_mb"]
                        })
                    
                    if "cpu_change_percent" in resource_data:
                        cpu_trend.append({
                            "timestamp": timestamp,
                            "cpu_change_percent": resource_data["cpu_change_percent"]
                        })
                except Exception as e:
                    logger.warning(f"Error parsing resource usage data for execution {execution.execution_id}: {str(e)}")
                    continue
            
            return {
                "workflow_id": workflow_id,
                "memory_usage_trend": memory_trend,
                "cpu_usage_trend": cpu_trend
            }
        except Exception as e:
            logger.error(f"Error getting resource usage trends: {str(e)}")
            raise

    async def get_failure_analysis(self, workflow_id: str, 
                                days: int = 30) -> Dict[str, Any]:
        """Analyze workflow and step failures to identify patterns"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # Get failed executions
            failed_executions = self.db.query(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.workflow_id == workflow_id,
                    WorkflowExecution.status == "failed",
                    WorkflowExecution.created_at >= start_time,
                    WorkflowExecution.created_at <= end_time
                )
            ).all()
            
            # Get failed steps
            failed_steps = self.db.query(StepExecution).join(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.workflow_id == workflow_id,
                    StepExecution.status == "failed",
                    WorkflowExecution.created_at >= start_time,
                    WorkflowExecution.created_at <= end_time
                )
            ).all()
            
            # Convert to dict objects for easier processing
            failed_execution_dicts = []
            for e in failed_executions:
                failed_execution_dicts.append({
                    "id": e.id,
                    "execution_id": e.execution_id,
                    "workflow_id": e.workflow_id,
                    "status": e.status,
                    "input_data": e.input_data,
                    "output_data": e.output_data,
                    "error_message": e.error_message,
                    "started_at": e.started_at,
                    "completed_at": e.completed_at,
                    "created_at": e.created_at,
                    "execution_time": e.execution_time,
                    "step_count": e.step_count,
                    "success_count": e.success_count,
                    "failure_count": e.failure_count,
                    "retry_count": e.retry_count,
                    "resource_usage": e.resource_usage
                })
            
            # Analyze failure patterns
            failure_reasons = defaultdict(int)
            failure_by_step = defaultdict(int)
            failure_by_agent = defaultdict(int)
            
            # Analyze execution failures
            for execution in failed_execution_dicts:
                if execution["error_message"] is not None:
                    # Simple categorization of failure reasons
                    error_lower = execution["error_message"].lower()
                    if "timeout" in error_lower:
                        failure_reasons["timeout"] += 1
                    elif "memory" in error_lower:
                        failure_reasons["memory_exhaustion"] += 1
                    elif "network" in error_lower:
                        failure_reasons["network_error"] += 1
                    elif "api" in error_lower:
                        failure_reasons["api_error"] += 1
                    else:
                        failure_reasons["other"] += 1
            
            # Analyze step failures
            for step in failed_steps:
                failure_by_step[step.step_id] += 1
                failure_by_agent[step.agent_id] += 1
            
            # Get total executions for failure rate calculation
            total_executions = self.db.query(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.workflow_id == workflow_id,
                    WorkflowExecution.created_at >= start_time,
                    WorkflowExecution.created_at <= end_time
                )
            ).count()
            
            return {
                "workflow_id": workflow_id,
                "total_failures": len(failed_executions),
                "failure_reasons": dict(failure_reasons),
                "failures_by_step": dict(failure_by_step),
                "failures_by_agent": dict(failure_by_agent),
                "failure_rate": round(len(failed_executions) / max(total_executions, 1) * 100, 2)
            }
        except Exception as e:
            logger.error(f"Error performing failure analysis: {str(e)}")
            raise

    async def get_predictive_analytics(self, workflow_id: str, 
                                    days: int = 30) -> Dict[str, Any]:
        """Provide predictive analytics based on historical execution data"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # Get recent executions
            executions = self.db.query(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.workflow_id == workflow_id,
                    WorkflowExecution.created_at >= start_time,
                    WorkflowExecution.created_at <= end_time
                )
            ).order_by(WorkflowExecution.created_at.desc()).all()
            
            if len(executions) < 5:  # Need at least 5 executions for meaningful prediction
                return {
                    "workflow_id": workflow_id,
                    "predictions_available": False,
                    "message": "Insufficient data for predictive analytics"
                }
            
            # Convert to dict objects for easier processing
            execution_dicts = []
            for e in executions:
                execution_dicts.append({
                    "id": e.id,
                    "execution_id": e.execution_id,
                    "workflow_id": e.workflow_id,
                    "status": e.status,
                    "input_data": e.input_data,
                    "output_data": e.output_data,
                    "error_message": e.error_message,
                    "started_at": e.started_at,
                    "completed_at": e.completed_at,
                    "created_at": e.created_at,
                    "execution_time": e.execution_time,
                    "step_count": e.step_count,
                    "success_count": e.success_count,
                    "failure_count": e.failure_count,
                    "retry_count": e.retry_count,
                    "resource_usage": e.resource_usage
                })
            
            # Calculate recent trends
            recent_executions = execution_dicts[:10]  # Last 10 executions
            durations = []
            success_rates = []
            
            for execution in recent_executions:
                if (execution["started_at"] is not None and 
                    execution["completed_at"] is not None and 
                    execution["status"] == "completed"):
                    duration = (execution["completed_at"] - execution["started_at"]).total_seconds()
                    durations.append(duration)
            
            # Calculate average duration trend
            if len(durations) >= 2:
                # Simple linear trend calculation
                avg_duration = sum(durations) / len(durations)
                recent_avg = sum(durations[:5]) / min(5, len(durations))  # Average of last 5
                older_avg = sum(durations[5:]) / max(1, len(durations[5:])) if len(durations) > 5 else avg_duration
                
                duration_trend = "increasing" if recent_avg > older_avg * 1.1 else "decreasing" if recent_avg < older_avg * 0.9 else "stable"
                predicted_duration = recent_avg * 1.1 if duration_trend == "increasing" else recent_avg * 0.9 if duration_trend == "decreasing" else recent_avg
            else:
                avg_duration = sum(durations) / len(durations) if durations else 0
                duration_trend = "insufficient_data"
                predicted_duration = avg_duration
            
            # Success rate
            completed_count = len([e for e in recent_executions if e["status"] == "completed"])
            success_rate = completed_count / len(recent_executions) if recent_executions else 0
            
            return {
                "workflow_id": workflow_id,
                "predictions_available": True,
                "estimated_execution_time": round(predicted_duration, 2),
                "duration_trend": duration_trend,
                "success_rate": round(success_rate * 100, 2),
                "recommendations": self._generate_recommendations(execution_dicts)
            }
        except Exception as e:
            logger.error(f"Error generating predictive analytics: {str(e)}")
            raise

    def _generate_recommendations(self, executions: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on execution data"""
        recommendations = []
        
        # Analyze failure patterns
        failed_executions = [e for e in executions if e["status"] == "failed"]
        failure_rate = len(failed_executions) / len(executions) if executions else 0
        
        if failure_rate > 0.2:  # More than 20% failure rate
            recommendations.append("High failure rate detected. Review error logs and consider implementing retry mechanisms.")
        
        # Analyze duration patterns
        completed_executions = [e for e in executions if e["status"] == "completed" and e["started_at"] is not None and e["completed_at"] is not None]
        if completed_executions:
            durations = [(e["completed_at"] - e["started_at"]).total_seconds() for e in completed_executions]
            avg_duration = sum(durations) / len(durations)
            
            if avg_duration > 300:  # More than 5 minutes average
                recommendations.append("Long execution times detected. Consider optimizing workflow steps or implementing parallel processing.")
        
        # Check for resource usage patterns
        high_memory_executions = [e for e in completed_executions if e["resource_usage"] is not None and 
                                  isinstance(e["resource_usage"], dict) and 
                                  e["resource_usage"].get("memory_change_mb", 0) > 100]
        
        if len(high_memory_executions) / len(completed_executions) > 0.5:  # More than 50% use high memory
            recommendations.append("High memory usage detected in executions. Consider optimizing memory-intensive steps.")
        
        if not recommendations:
            recommendations.append("Workflow performance appears stable. Continue monitoring for any changes.")
        
        return recommendations
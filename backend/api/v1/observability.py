import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from services.telemetry_service import telemetry_service

logger = logging.getLogger(__name__)
from models.workflow import WorkflowExecution, StepExecution
from api.v1.auth import get_current_user
from core.database import get_db

router = APIRouter()


async def _get_workflow_execution_traces(db: Session, workflow_id: str, status: Optional[str], limit: int, offset: int):
    """
    Get workflow execution history as traces.
    
    This returns workflow executions from the database (not OpenTelemetry spans)
    to keep workflow traces separate from agent traces.
    """
    # Build query for workflow executions
    query = db.query(WorkflowExecution).filter(WorkflowExecution.workflow_id == workflow_id)
    
    # Filter by status if provided
    if status:
        db_status = "completed" if status == "success" else "failed" if status == "failed" else status
        query = query.filter(WorkflowExecution.status == db_status)
    
    # Order by created_at descending
    query = query.order_by(WorkflowExecution.created_at.desc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    executions = query.offset(offset).limit(limit).all()
    
    # Format as Jaeger-compatible traces
    result_traces = []
    for execution in executions:
        # Get step executions for this workflow execution
        steps = db.query(StepExecution).filter(
            StepExecution.execution_id == execution.execution_id
        ).order_by(StepExecution.created_at).all()
        
        # Calculate duration in microseconds
        duration_us = int((execution.execution_time or 0) * 1_000_000)
        
        # Calculate start time in microseconds - use actual DB timestamp
        start_time_us = 0
        if execution.started_at:
            start_time_us = int(execution.started_at.timestamp() * 1_000_000)
        elif execution.created_at:
            start_time_us = int(execution.created_at.timestamp() * 1_000_000)
        
        # Create root span for workflow
        root_span = {
            "traceID": execution.execution_id,
            "spanID": f"wf-{execution.execution_id[:8]}",
            "operationName": "workflow_execution",
            "references": [],
            "startTime": start_time_us,
            "duration": duration_us,
            "tags": [
                {"key": "workflow_id", "type": "string", "value": workflow_id},
                {"key": "execution_id", "type": "string", "value": execution.execution_id},
                {"key": "status", "type": "string", "value": execution.status or "unknown"},
                {"key": "step_count", "type": "int64", "value": len(steps)},
            ],
            "logs": [],
            "processID": "p1",
            "warnings": None
        }
        
        # Create child spans for each step with actual timestamps
        formatted_spans = [root_span]
        for step in steps:
            # Use actual step timestamps from DB
            step_start_us = start_time_us  # Default to workflow start
            if step.started_at:
                step_start_us = int(step.started_at.timestamp() * 1_000_000)
            elif step.created_at:
                step_start_us = int(step.created_at.timestamp() * 1_000_000)
            
            step_duration_us = int((step.execution_time or 0) * 1_000_000)
            
            step_span = {
                "traceID": execution.execution_id,
                "spanID": f"step-{step.step_id[:8] if step.step_id else step.id}",
                "operationName": f"step:{step.step_id or 'unknown'}",
                "references": [{"refType": "CHILD_OF", "traceID": execution.execution_id, "spanID": root_span["spanID"]}],
                "startTime": step_start_us,
                "duration": step_duration_us,
                "tags": [
                    {"key": "step_id", "type": "string", "value": step.step_id or ""},
                    {"key": "status", "type": "string", "value": step.status or "unknown"},
                    {"key": "agent_id", "type": "string", "value": step.agent_id or ""},
                ],
                "logs": [],
                "processID": "p1",
                "warnings": None
            }
            
            if step.error_message:
                step_span["tags"].append({"key": "error", "type": "bool", "value": True})
                step_span["tags"].append({"key": "error.message", "type": "string", "value": step.error_message})
            
            formatted_spans.append(step_span)
        
        result_traces.append({
            "traceID": execution.execution_id,
            "spans": formatted_spans,
            "processes": {
                "p1": {
                    "serviceName": "workflow-engine",
                    "tags": []
                }
            }
        })
    
    return {"data": result_traces, "total": total, "limit": limit, "offset": offset}


@router.get("/agents/{agent_id}/metrics")
async def get_agent_metrics(
    agent_id: str,
    time_range: str = Query("24h", description="Time range for metrics (e.g., 24h, 7d, 30d)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive observability metrics for a specific agent from OpenTelemetry data.
    """
    try:
        from models.telemetry import Trace, Span
        import json
        from collections import defaultdict
        import numpy as np
        
        # Calculate start time based on range
        now = datetime.now(timezone.utc)
        if time_range == "7d":
            start_time = now - timedelta(days=7)
        elif time_range == "30d":
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(hours=24)

        # Query StepExecution for basic metrics
        query = db.query(StepExecution).filter(
            StepExecution.agent_id == agent_id,
            StepExecution.created_at >= start_time
        )
        
        total_runs = query.count()
        success_runs = query.filter(StepExecution.status == "completed").count()
        failed_runs = query.filter(StepExecution.status == "failed").count()
        
        # Query spans for detailed metrics - value is stored as quoted string with space after colon
        spans_query = db.query(Span).join(Trace).filter(
            Span.attributes.like(f'%"agent_id": "{agent_id}"%'),
            Trace.start_time >= start_time.isoformat()
        )
        
        all_spans = spans_query.all()
        
        # Extract metrics from spans
        total_tokens = 0
        prompt_tokens = 0
        completion_tokens = 0
        total_cost = 0.0
        llm_calls = 0
        tool_calls = 0
        latencies = []
        model_costs = defaultdict(float)
        model_tokens = defaultdict(int)
        unique_users = set()
        requests_by_time = defaultdict(int)
        ttft_values =[]
        
        # Enhanced metrics
        tool_usage = defaultdict(int)  # tool_name -> count
        tool_latencies = defaultdict(list)  # tool_name -> [latencies]
        tool_failures = defaultdict(int)  # tool_name -> failure_count
        finish_reasons = defaultdict(int)  # finish_reason -> count
        recent_prompts = []  # Last 5 prompts
        recent_responses = []  # Last 5 responses
        mcp_servers_used = set()  # Set of MCP server IDs used
        
        # Model pricing (per 1M tokens)
        MODEL_PRICING = {
            "gpt-4": {"input": 30.0, "output": 60.0},
            "gpt-4-turbo": {"input": 10.0, "output": 30.0},
            "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
            "claude-3-opus": {"input": 15.0, "output": 75.0},
            "claude-3-sonnet": {"input": 3.0, "output": 15.0},
            "groq/llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},
            "groq/mixtral-8x7b": {"input": 0.24, "output": 0.24},
            "groq/llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
        }
        
        for span in all_spans:
            try:
                attrs = json.loads(span.attributes) if span.attributes else {}
                
                # Track unique users
                if "user_id" in attrs or "session_id" in attrs:
                    user_key = attrs.get("user_id") or attrs.get("session_id")
                    if user_key:
                        unique_users.add(user_key)
                
                # Track requests over time (hourly buckets)
                if span.start_time:
                    try:
                        hour_bucket = datetime.fromisoformat(span.start_time.replace('Z', '+00:00')).replace(minute=0, second=0, microsecond=0).isoformat()
                        requests_by_time[hour_bucket] += 1
                    except:
                        pass
                
                # Count LLM calls and extract comprehensive LLM metrics
                if "gen_ai.system" in attrs:
                    llm_calls += 1
                    
                    # Extract tokens
                    input_tok = attrs.get("gen_ai.usage.input_tokens") or attrs.get("gen_ai.usage.prompt_tokens") or 0
                    output_tok = attrs.get("gen_ai.usage.output_tokens") or attrs.get("gen_ai.usage.completion_tokens") or 0
                    
                    if input_tok:
                        prompt_tokens += int(input_tok)
                    if output_tok:
                        completion_tokens += int(output_tok)
                    
                    total_tokens += int(input_tok) + int(output_tok)
                    
                    # Calculate cost
                    model = attrs.get("gen_ai.request.model") or attrs.get("gen_ai.response.model") or "unknown"
                    pricing = MODEL_PRICING.get(model, {"input": 0.0, "output": 0.0})
                    
                    # Handle custom cost if set
                    custom_cost = attrs.get("cost_usd")
                    if custom_cost:
                        span_cost = float(custom_cost)
                    else:
                        span_cost = (int(input_tok) * pricing["input"] / 1_000_000) + (int(output_tok) * pricing["output"] / 1_000_000)
                    
                    total_cost += span_cost
                    model_costs[model] += span_cost
                    model_tokens[model] += int(input_tok) + int(output_tok)
                    
                    # Track latency
                    if span.duration_us:
                        latencies.append(span.duration_us / 1000)  # Convert to ms
                    
                    # Extract finish reason
                    finish_reason = attrs.get("finish_reason") or attrs.get("gen_ai.response.finish_reasons")
                    if finish_reason:
                        if isinstance(finish_reason, list):
                            for fr in finish_reason:
                                finish_reasons[fr] += 1
                        else:
                            finish_reasons[finish_reason] += 1
                    
                    # Extract prompt (limit to last 5)
                    prompt = attrs.get("agent_input") or attrs.get("gen_ai.prompt.0.content")
                    if prompt and len(recent_prompts) < 5:
                        recent_prompts.append({
                            "timestamp": span.start_time,
                            "prompt": str(prompt)[:200],  # Truncate for display
                            "model": model
                        })
                    
                    # Extract response (limit to last 5)
                    response = attrs.get("agent_output") or attrs.get("gen_ai.completion.0.content")
                    if response and len(recent_responses) < 5:
                        recent_responses.append({
                            "timestamp": span.end_time,
                            "response": str(response)[:200],  # Truncate for display
                            "model": model
                        })
                
                # Count tool calls and extract tool metrics
                if "tool.name" in attrs or span.name.startswith("tool:"):
                    tool_calls += 1
                    tool_name = attrs.get("tool.name") or span.name.replace("tool:", "")
                    
                    # Track tool usage
                    tool_usage[tool_name] += 1
                    
                    # Track tool latency
                    tool_latency = attrs.get("tool.execution_time_ms")
                    if tool_latency:
                        tool_latencies[tool_name].append(float(tool_latency))
                    elif span.duration_us:
                        tool_latencies[tool_name].append(span.duration_us / 1000)
                    
                    # Track tool failures
                    tool_success = attrs.get("tool.success")
                    if tool_success == "false" or tool_success == False or span.status == "error":
                        tool_failures[tool_name] += 1
                    
                    # Track MCP server usage
                    server_id = attrs.get("tool.server_id") or attrs.get("mcp.server_id")
                    if server_id:
                        mcp_servers_used.add(server_id)
                    
            except Exception as e:
                logger.debug(f"Error processing span: {e}")
                continue
        
        # Calculate latency percentiles
        avg_latency = np.mean(latencies) if latencies else 0
        p99_latency = np.percentile(latencies, 99) if latencies else 0
        ttft = np.mean(ttft_values) if ttft_values else avg_latency * 0.1  # Estimate TTFT as 10% of avg latency
        
        # Generate chart data
        chart_data = []
        for time_bucket in sorted(requests_by_time.keys()):
            chart_data.append({
                "time": time_bucket,
                "requests": requests_by_time[time_bucket]
            })
        
        # Model cost breakdown
        model_cost_list = [
            {"name": model, "cost": round(cost, 4), "tokens": model_tokens.get(model, 0)}
            for model, cost in sorted(model_costs.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # Tool usage breakdown
        tool_usage_list = [
            {
                "name": tool_name,
                "count": count,
                "avg_latency": round(np.mean(tool_latencies.get(tool_name, [0])), 2),
                "failures": tool_failures.get(tool_name, 0),
                "success_rate": round((count - tool_failures.get(tool_name, 0)) / count * 100, 2) if count > 0 else 100
            }
            for tool_name, count in sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return {
            # Basic metrics
            "total_runs": total_runs,
            "success_rate": (success_runs / total_runs * 100) if total_runs > 0 else 0,
            "error_rate": (failed_runs / total_runs * 100) if total_runs > 0 else 0,
            
            # LLM metrics
            "llm_calls": llm_calls,
            "avg_latency": round(avg_latency, 2),
            "p99_latency": round(p99_latency, 2),
            "ttft": round(ttft, 2),
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "model_costs": model_cost_list,
            "finish_reasons": dict(finish_reasons),
            
            # Tool metrics
            "tool_calls": tool_calls,
            "tool_usage": tool_usage_list,
            "mcp_servers_used": list(mcp_servers_used),
            
            # User analytics
            "active_users": len(unique_users),
            
            # Time series
            "chart_data": chart_data,
            
            # Samples for debugging
            "recent_prompts": recent_prompts,
            "recent_responses": recent_responses
        }
    except Exception as e:
        import traceback
        print(f"Error in get_agent_metrics: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflows/{workflow_id}/metrics")
async def get_workflow_metrics(
    workflow_id: str,
    time_range: str = Query("24h", description="Time range for metrics"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get workflow metrics from workflow_executions and step_executions tables.
    
    NOTE: Workflow metrics are separate from agent traces. Agent LLM/tool metrics
    are shown at the agent level. Workflow metrics show execution stats and timing.
    """
    try:
        from models.telemetry import Trace, Span
        import json
        from collections import defaultdict
        import numpy as np
        
        # Calculate start time based on range
        now = datetime.now(timezone.utc)
        if time_range == "7d":
            start_time = now - timedelta(days=7)
        elif time_range == "30d":
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(hours=24)

        # Query WorkflowExecution for metrics (primary source for workflow data)
        base_filter = [
            WorkflowExecution.workflow_id == workflow_id,
            WorkflowExecution.created_at >= start_time
        ]
        
        total_runs = db.query(WorkflowExecution).filter(*base_filter).count()
        success_runs = db.query(WorkflowExecution).filter(
            *base_filter, 
            WorkflowExecution.status == "completed"
        ).count()
        failed_runs = db.query(WorkflowExecution).filter(
            *base_filter,
            WorkflowExecution.status == "failed"
        ).count()
        
        # Calculate average duration from workflow executions
        avg_duration_seconds = db.query(func.avg(WorkflowExecution.execution_time)).filter(
            WorkflowExecution.workflow_id == workflow_id,
            WorkflowExecution.created_at >= start_time,
            WorkflowExecution.status == "completed"
        ).scalar() or 0
        
        # Get p95 duration from workflow executions
        all_durations = db.query(WorkflowExecution.execution_time).filter(
            WorkflowExecution.workflow_id == workflow_id,
            WorkflowExecution.created_at >= start_time,
            WorkflowExecution.status == "completed",
            WorkflowExecution.execution_time.isnot(None)
        ).all()
        durations = [d[0] for d in all_durations if d[0] is not None]
        p95_duration = np.percentile(durations, 95) * 1000 if durations else 0  # Convert to ms
        
        # Get step executions for this workflow to aggregate agent metrics
        workflow_executions = db.query(WorkflowExecution).filter(*base_filter).all()
        execution_ids = [we.execution_id for we in workflow_executions]
        
        # Aggregate metrics from step executions
        total_tokens = 0
        prompt_tokens = 0
        completion_tokens = 0
        total_cost = 0.0
        model_costs = defaultdict(float)
        
        # Get unique agent_ids from step executions to query their metrics
        step_agent_ids = set()
        for exec_id in execution_ids:
            steps = db.query(StepExecution).filter(
                StepExecution.execution_id == exec_id,
                StepExecution.agent_id.isnot(None)
            ).all()
            for step in steps:
                if step.agent_id:
                    step_agent_ids.add(step.agent_id)
        
        # For each agent that was part of workflow executions, aggregate LLM metrics
        # Query spans with agent_id that fall within the workflow execution timeframe
        if step_agent_ids:
            for agent_id in step_agent_ids:
                spans_query = db.query(Span).join(Trace).filter(
                    Span.attributes.like(f'%"agent_id": "{agent_id}"%'),
                    Trace.start_time >= start_time.isoformat()
                )
                
                # Model pricing (per 1M tokens)
                MODEL_PRICING = {
                    "gpt-4": {"input": 30.0, "output": 60.0},
                    "gpt-4-turbo": {"input": 10.0, "output": 30.0},
                    "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
                    "claude-3-opus": {"input": 15.0, "output": 75.0},
                    "claude-3-sonnet": {"input": 3.0, "output": 15.0},
                    "groq/llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},
                    "groq/mixtral-8x7b": {"input": 0.24, "output": 0.24},
                }
                
                for span in spans_query.all():
                    try:
                        attrs = json.loads(span.attributes) if span.attributes else {}
                        
                        # Only count LLM spans
                        if "gen_ai.system" in attrs:
                            input_tok = attrs.get("gen_ai.usage.input_tokens") or attrs.get("gen_ai.usage.prompt_tokens") or 0
                            output_tok = attrs.get("gen_ai.usage.output_tokens") or attrs.get("gen_ai.usage.completion_tokens") or 0
                            
                            if input_tok:
                                prompt_tokens += int(input_tok)
                            if output_tok:
                                completion_tokens += int(output_tok)
                            
                            total_tokens += int(input_tok) + int(output_tok)
                            
                            model = attrs.get("gen_ai.request.model") or attrs.get("gen_ai.response.model") or "unknown"
                            pricing = MODEL_PRICING.get(model, {"input": 0.0, "output": 0.0})
                            
                            span_cost = (int(input_tok) * pricing["input"] / 1_000_000) + (int(output_tok) * pricing["output"] / 1_000_000)
                            total_cost += span_cost
                            model_costs[model] += span_cost
                    except:
                        continue
        
        # Generate chart data from workflow executions (hourly buckets)
        executions_by_time = defaultdict(int)
        for we in workflow_executions:
            if we.created_at:
                try:
                    hour_bucket = we.created_at.replace(minute=0, second=0, microsecond=0).isoformat()
                    executions_by_time[hour_bucket] += 1
                except:
                    pass
        
        chart_data = [
            {"time": time_bucket, "executions": count}
            for time_bucket, count in sorted(executions_by_time.items())
        ]
        
        # Model cost breakdown
        model_cost_list = [
            {"name": model, "cost": cost}
            for model, cost in sorted(model_costs.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return {
            "total_runs": total_runs,
            "success_rate": (success_runs / total_runs * 100) if total_runs > 0 else 0,
            "avg_latency": avg_duration_seconds * 1000 if avg_duration_seconds else 0,  # Convert to ms
            "p95_latency": p95_duration,
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "error_rate": (failed_runs / total_runs * 100) if total_runs > 0 else 0,
            "model_costs": model_cost_list,
            "chart_data": chart_data
        }
    except Exception as e:
        import traceback
        print(f"Error in get_workflow_metrics: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/traces")
async def get_traces(
    agent_id: Optional[str] = Query(None, description="Filter traces by agent ID"),
    workflow_id: Optional[str] = Query(None, description="Filter traces by workflow ID"),
    status: Optional[str] = Query(None, description="Filter by status (success/failed)"),
    limit: int = Query(10, description="Maximum number of traces to return"),
    offset: int = Query(0, description="Offset for pagination"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get execution traces.
    
    - For agent_id: Returns OpenTelemetry traces showing LLM/tool execution details
    - For workflow_id: Returns workflow execution history from workflow_executions table
    """
    try:
        from models.telemetry import Trace, Span
        import json
        
        # WORKFLOW TRACES: Return workflow execution history, not OpenTelemetry spans
        if workflow_id and not agent_id:
            return await _get_workflow_execution_traces(db, workflow_id, status, limit, offset)
        
        # AGENT TRACES: Return OpenTelemetry traces filtered by agent_id
        # Build base query
        query = db.query(Trace)
        
        # Filter by status if provided
        if status:
            query = query.filter(Trace.status == status)
        
        # Filter by agent_id via spans' attributes
        if agent_id:
            # Join with spans to filter by attributes
            subquery = db.query(Span.trace_id).distinct()
            
            # SQLite JSON extract - value is stored as quoted string with space after colon
            subquery = subquery.filter(
                Span.attributes.like(f'%"agent_id": "{agent_id}"%')
            )
            
            trace_ids = [row[0] for row in subquery.all()]
            if trace_ids:
                query = query.filter(Trace.trace_id.in_(trace_ids))
            else:
                # No matching traces
                return {"data": [], "total": 0, "limit": limit, "offset": offset}
        
        # Order by start_time descending
        query = query.order_by(Trace.start_time.desc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        traces = query.offset(offset).limit(limit).all()
        
        # Format traces for frontend (Jaeger-compatible format)
        result_traces = []
        for trace in traces:
            # Get spans for this trace
            trace_spans = db.query(Span).filter(Span.trace_id == trace.trace_id).all()
            
            # Format spans in Jaeger-compatible format
            formatted_spans = []
            total_tokens = 0
            for span in trace_spans:
                # Parse attributes
                try:
                    attributes = json.loads(span.attributes) if span.attributes else {}
                except:
                    attributes = {}
                
                # Convert attributes to Jaeger tags format
                tags = [{"key": k, "type": "string", "value": str(v)} for k, v in attributes.items()]
                
                # Extract tokens if available - check all possible OpenLLMetry token attributes
                token_keys = [
                    "gen_ai.usage.total_tokens", "llm.usage.total_tokens",
                    "gen_ai.usage.input_tokens", "gen_ai.usage.output_tokens",
                    "gen_ai.usage.prompt_tokens", "gen_ai.usage.completion_tokens"
                ]
                for tag in tags:
                    if tag["key"] in token_keys:
                        try:
                            total_tokens += int(tag["value"])
                        except:
                            pass
                
                # Calculate start time in microseconds (Jaeger format)
                start_time_us = 0
                if span.start_time:
                    try:
                        start_time_us = int(datetime.fromisoformat(span.start_time.replace('Z', '+00:00')).timestamp() * 1_000_000)
                    except:
                        pass
                
                formatted_spans.append({
                    "traceID": span.trace_id,
                    "spanID": span.span_id,
                    "operationName": span.name,
                    "references": [{"refType": "CHILD_OF", "traceID": span.trace_id, "spanID": span.parent_span_id}] if span.parent_span_id else [],
                    "startTime": start_time_us,
                    "duration": span.duration_us or 0,
                    "tags": tags,
                    "logs": [],
                    "processID": "p1",
                    "warnings": None
                })
            
            result_traces.append({
                "traceID": trace.trace_id,
                "spans": formatted_spans,
                "processes": {
                    "p1": {
                        "serviceName": trace.service_name or "execution-plane",
                        "tags": []
                    }
                }
            })
        
        return {"data": result_traces, "total": total, "limit": limit, "offset": offset}
    except Exception as e:
        import traceback
        print(f"Error in get_traces: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/traces/{trace_id}")
async def get_trace_details(
    trace_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information for a specific trace.
    
    Handles two types of traces:
    - Workflow executions (trace_id starts with 'exec-') → from workflow_executions table
    - Agent traces (OpenTelemetry trace IDs) → from traces/spans tables
    """
    try:
        from models.telemetry import Trace, Span
        import json
        
        # Check if this is a workflow execution ID
        if trace_id.startswith("exec-"):
            return await _get_workflow_execution_detail(db, trace_id)
        
        # Otherwise, it's an OpenTelemetry trace
        trace = db.query(Trace).filter(Trace.trace_id == trace_id).first()
        if not trace:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        # Get all spans for this trace
        spans = db.query(Span).filter(Span.trace_id == trace_id).all()
        
        # Format spans in Jaeger-compatible format
        formatted_spans = []
        for span in spans:
            # Parse attributes
            try:
                attributes = json.loads(span.attributes) if span.attributes else {}
            except:
                attributes = {}
            
            # Convert attributes to Jaeger tags format
            tags = [{"key": k, "type": "string", "value": str(v)} for k, v in attributes.items()]
            
            # Calculate start time in microseconds (Jaeger format)
            start_time_us = 0
            if span.start_time:
                try:
                    start_time_us = int(datetime.fromisoformat(span.start_time.replace('Z', '+00:00')).timestamp() * 1_000_000)
                except:
                    pass
            
            formatted_spans.append({
                "traceID": span.trace_id,
                "spanID": span.span_id,
                "operationName": span.name,
                "references": [{"refType": "CHILD_OF", "traceID": span.trace_id, "spanID": span.parent_span_id}] if span.parent_span_id else [],
                "startTime": start_time_us,
                "duration": span.duration_us or 0,
                "tags": tags,
                "logs": [],
                "processID": "p1",
                "warnings": None
            })
        
        return {
            "traceID": trace.trace_id,
            "spans": formatted_spans,
            "processes": {
                "p1": {
                    "serviceName": trace.service_name or "execution-plane",
                    "tags": []
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in get_trace_details: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


async def _get_workflow_execution_detail(db: Session, execution_id: str):
    """Get detailed trace view for a workflow execution."""
    
    execution = db.query(WorkflowExecution).filter(
        WorkflowExecution.execution_id == execution_id
    ).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Workflow execution not found")
    
    # Get step executions
    steps = db.query(StepExecution).filter(
        StepExecution.execution_id == execution_id
    ).order_by(StepExecution.created_at).all()
    
    # Calculate timestamps - use actual timestamps from DB
    start_time_us = 0
    if execution.started_at:
        start_time_us = int(execution.started_at.timestamp() * 1_000_000)
    elif execution.created_at:
        start_time_us = int(execution.created_at.timestamp() * 1_000_000)
    
    duration_us = int((execution.execution_time or 0) * 1_000_000)
    
    # Create root span for workflow
    root_span = {
        "traceID": execution_id,
        "spanID": f"wf-root",
        "operationName": "workflow_execution",
        "references": [],
        "startTime": start_time_us,
        "duration": duration_us,
        "tags": [
            {"key": "workflow_id", "type": "string", "value": execution.workflow_id},
            {"key": "execution_id", "type": "string", "value": execution_id},
            {"key": "status", "type": "string", "value": execution.status or "unknown"},
            {"key": "step_count", "type": "int64", "value": len(steps)},
        ],
        "logs": [],
        "processID": "p1",
        "warnings": None
    }
    
    # Create child spans for each step with proper timing
    formatted_spans = [root_span]
    for step in steps:
        # Use actual step timestamps
        step_start_us = start_time_us
        if step.started_at:
            step_start_us = int(step.started_at.timestamp() * 1_000_000)
        elif step.created_at:
            step_start_us = int(step.created_at.timestamp() * 1_000_000)
        
        step_duration_us = int((step.execution_time or 0) * 1_000_000)
        
        step_tags = [
            {"key": "step_id", "type": "string", "value": step.step_id or ""},
            {"key": "status", "type": "string", "value": step.status or "unknown"},
        ]
        
        if step.agent_id:
            step_tags.append({"key": "agent_id", "type": "string", "value": step.agent_id})
        
        if step.error_message:
            step_tags.append({"key": "error", "type": "bool", "value": True})
            step_tags.append({"key": "error.message", "type": "string", "value": step.error_message})
        
        # Add input/output if available (truncated for display)
        if step.input_data:
            input_str = str(step.input_data)[:500]
            step_tags.append({"key": "input", "type": "string", "value": input_str})
        if step.output_data:
            output_str = str(step.output_data)[:500]
            step_tags.append({"key": "output", "type": "string", "value": output_str})
        
        step_span = {
            "traceID": execution_id,
            "spanID": f"step-{step.step_id or step.id}",
            "operationName": f"step:{step.step_id or 'unknown'}",
            "references": [{"refType": "CHILD_OF", "traceID": execution_id, "spanID": "wf-root"}],
            "startTime": step_start_us,
            "duration": step_duration_us,
            "tags": step_tags,
            "logs": [],
            "processID": "p1",
            "warnings": None
        }
        
        formatted_spans.append(step_span)
    
    return {
        "traceID": execution_id,
        "spans": formatted_spans,
        "processes": {
            "p1": {
                "serviceName": "workflow-engine",
                "tags": []
            }
        }
    }

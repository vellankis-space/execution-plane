"""
Real-time observability endpoints with WebSocket support
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import asyncio
import logging

from services.monitoring_service import MonitoringService
from services.enhanced_monitoring_service import EnhancedMonitoringService
from services.tracing_service import TracingService
from core.database import get_db
from utils.timezone_utils import now_ist, to_ist_isoformat

logger = logging.getLogger(__name__)

router = APIRouter()

# Store active WebSocket connections for real-time updates
active_connections: List[WebSocket] = []


async def broadcast_metrics_update(data: Dict[str, Any]):
    """Broadcast metrics update to all connected WebSocket clients"""
    message = json.dumps({
        "type": "metrics_update",
        "timestamp": to_ist_isoformat(now_ist()),
        "data": data
    })
    
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception as e:
            logger.warning(f"Error sending to WebSocket client: {e}")
            disconnected.append(connection)
    
    # Remove disconnected clients
    for conn in disconnected:
        if conn in active_connections:
            active_connections.remove(conn)


@router.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics streaming"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial metrics
        from core.database import SessionLocal
        db = SessionLocal()
        try:
            monitoring_service = MonitoringService(db)
            real_time_metrics = await monitoring_service.get_real_time_metrics()
            health_metrics = await monitoring_service.get_system_health_metrics()
            
            await websocket.send_text(json.dumps({
                "type": "initial",
                "data": {
                    "real_time": real_time_metrics,
                    "health": health_metrics
                }
            }))
        finally:
            db.close()
        
        # Keep connection alive and send periodic updates
        while True:
            try:
                # Wait for client message or timeout
                try:
                    message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                    # Handle client messages if needed
                    data = json.loads(message)
                    if data.get("type") == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                except asyncio.TimeoutError:
                    # Send periodic update
                    from core.database import SessionLocal
                    db = SessionLocal()
                    try:
                        monitoring_service = MonitoringService(db)
                        real_time_metrics = await monitoring_service.get_real_time_metrics()
                        
                        await websocket.send_text(json.dumps({
                            "type": "update",
                            "timestamp": to_ist_isoformat(now_ist()),
                            "data": real_time_metrics
                        }))
                    finally:
                        db.close()
                        
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        try:
            await websocket.close()
        except:
            pass


@router.websocket("/ws/executions/{execution_id}")
async def websocket_execution_updates(websocket: WebSocket, execution_id: str):
    """WebSocket endpoint for real-time execution updates"""
    await websocket.accept()
    
    try:
        from core.database import SessionLocal
        db = SessionLocal()
        try:
            from models.workflow import WorkflowExecution, StepExecution
            
            last_status = None
            while True:
                # Get current execution status
                execution = db.query(WorkflowExecution).filter(
                    WorkflowExecution.execution_id == execution_id
                ).first()
                
                if not execution:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"Execution {execution_id} not found"
                    }))
                    break
                
                # Get step executions
                steps = db.query(StepExecution).filter(
                    StepExecution.execution_id == execution_id
                ).order_by(StepExecution.created_at).all()
                
                current_status = execution.status
                
                # Send update if status changed
                if current_status != last_status:
                    await websocket.send_text(json.dumps({
                        "type": "status_update",
                        "execution_id": execution_id,
                        "status": current_status,
                        "started_at": to_ist_isoformat(execution.started_at),
                        "completed_at": to_ist_isoformat(execution.completed_at),
                        "execution_time": execution.execution_time,
                        "error_message": execution.error_message,
                        "steps": [
                            {
                                "step_id": step.step_id,
                                "agent_id": step.agent_id,
                                "status": step.status,
                                "started_at": to_ist_isoformat(step.started_at),
                                "completed_at": to_ist_isoformat(step.completed_at),
                                "error_message": step.error_message
                            }
                            for step in steps
                        ]
                    }))
                    last_status = current_status
                    
                    # If execution is complete, close connection
                    if current_status in ["completed", "failed", "cancelled"]:
                        break
                
                # Wait before next check
                await asyncio.sleep(1)
                
        finally:
            db.close()
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket execution updates error: {e}")
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": str(e)
            }))
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass


@router.get("/traces")
async def get_traces(
    workflow_id: Optional[str] = None,
    execution_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get distributed traces from OpenTelemetry"""
    try:
        # In production, this would query your trace backend (Jaeger, Tempo, etc.)
        # For now, return execution traces from database
        from models.workflow import WorkflowExecution, StepExecution
        
        query = db.query(WorkflowExecution)
        
        if workflow_id:
            query = query.filter(WorkflowExecution.workflow_id == workflow_id)
        if execution_id:
            query = query.filter(WorkflowExecution.execution_id == execution_id)
        if start_time:
            query = query.filter(WorkflowExecution.created_at >= start_time)
        if end_time:
            query = query.filter(WorkflowExecution.created_at <= end_time)
        
        executions = query.order_by(WorkflowExecution.created_at.desc()).limit(limit).all()
        
        traces = []
        for exec in executions:
            steps = db.query(StepExecution).filter(
                StepExecution.execution_id == exec.execution_id
            ).order_by(StepExecution.created_at).all()
            
            trace = {
                "trace_id": exec.execution_id,
                "workflow_id": exec.workflow_id,
                "status": exec.status,
                "start_time": to_ist_isoformat(exec.started_at),
                "end_time": to_ist_isoformat(exec.completed_at),
                "duration": exec.execution_time,
                "spans": [
                    {
                        "span_id": step.step_id,
                        "name": f"Step: {step.step_id}",
                        "agent_id": step.agent_id,
                        "status": step.status,
                        "start_time": to_ist_isoformat(step.started_at),
                        "end_time": to_ist_isoformat(step.completed_at),
                        "duration": step.execution_time,
                        "attributes": {
                            "error": step.error_message if step.status == "failed" else None
                        }
                    }
                    for step in steps
                ]
            }
            traces.append(trace)
        
        return {
            "traces": traces,
            "total": len(traces)
        }
    except Exception as e:
        logger.error(f"Error getting traces: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traces/{trace_id}")
async def get_trace_detail(
    trace_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed trace information"""
    try:
        from models.workflow import WorkflowExecution, StepExecution, ExecutionLog
        
        execution = db.query(WorkflowExecution).filter(
            WorkflowExecution.execution_id == trace_id
        ).first()
        
        if not execution:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        steps = db.query(StepExecution).filter(
            StepExecution.execution_id == trace_id
        ).order_by(StepExecution.created_at).all()
        
        logs = db.query(ExecutionLog).filter(
            ExecutionLog.execution_id == trace_id
        ).order_by(ExecutionLog.timestamp).all()
        
        return {
            "trace_id": trace_id,
            "workflow_id": execution.workflow_id,
            "status": execution.status,
            "start_time": to_ist_isoformat(execution.started_at),
            "end_time": to_ist_isoformat(execution.completed_at),
            "duration": execution.execution_time,
            "input_data": execution.input_data,
            "output_data": execution.output_data,
            "error_message": execution.error_message,
            "spans": [
                {
                    "span_id": step.step_id,
                    "name": f"Step: {step.step_id}",
                    "agent_id": step.agent_id,
                    "status": step.status,
                    "start_time": to_ist_isoformat(step.started_at),
                    "end_time": to_ist_isoformat(step.completed_at),
                    "duration": step.execution_time,
                    "input_data": step.input_data,
                    "output_data": step.output_data,
                    "error_message": step.error_message,
                    "resource_usage": {
                        "memory_usage": step.memory_usage,
                        "cpu_usage": step.cpu_usage,
                        "io_operations": step.io_operations,
                        "network_requests": step.network_requests
                    } if step.memory_usage or step.cpu_usage else None
                }
                for step in steps
            ],
            "logs": [
                {
                    "timestamp": to_ist_isoformat(log.timestamp),
                    "level": log.log_level,
                    "message": log.message,
                    "metadata": log.log_metadata
                }
                for log in logs
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trace detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/stream")
async def get_streaming_metrics(
    workflow_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get metrics in streaming format (SSE)"""
    from fastapi.responses import StreamingResponse
    import json
    
    async def generate():
        monitoring_service = MonitoringService(db)
        enhanced_service = EnhancedMonitoringService(db)
        
        while True:
            try:
                # Get real-time metrics
                real_time = await monitoring_service.get_real_time_metrics()
                health = await monitoring_service.get_system_health_metrics()
                
                if workflow_id:
                    workflow_metrics = await monitoring_service.get_workflow_execution_metrics(
                        workflow_id=workflow_id
                    )
                    enhanced_metrics = await enhanced_service.get_enhanced_workflow_metrics(
                        workflow_id=workflow_id
                    )
                else:
                    workflow_metrics = {}
                    enhanced_metrics = {}
                
                data = {
                    "timestamp": to_ist_isoformat(now_ist()),
                    "real_time": real_time,
                    "health": health,
                    "workflow_metrics": workflow_metrics,
                    "enhanced_metrics": enhanced_metrics
                }
                
                yield f"data: {json.dumps(data)}\n\n"
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in metrics stream: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                await asyncio.sleep(5)
    
    return StreamingResponse(generate(), media_type="text/event-stream")




@router.get("/observability/overview")
async def get_observability_overview(
    db: Session = Depends(get_db)
):
    """Get comprehensive observability overview"""
    try:
        monitoring_service = MonitoringService(db)
        enhanced_service = EnhancedMonitoringService(db)
        
        # Get all metrics
        health_metrics = await monitoring_service.get_system_health_metrics()
        real_time_metrics = await monitoring_service.get_real_time_metrics()
        
        # Get recent traces
        from models.workflow import WorkflowExecution
        recent_executions = db.query(WorkflowExecution).order_by(
            WorkflowExecution.created_at.desc()
        ).limit(10).all()
        
        return {
            "timestamp": to_ist_isoformat(now_ist()),
            "system_health": health_metrics,
            "real_time_metrics": real_time_metrics,
            "tracing_enabled": True,  # OpenTelemetry is always enabled
            "recent_traces": [
                {
                    "trace_id": exec.execution_id,
                    "workflow_id": exec.workflow_id,
                    "status": exec.status,
                    "started_at": to_ist_isoformat(exec.started_at)
                }
                for exec in recent_executions
            ],
            "capabilities": {
                "real_time_monitoring": True,
                "distributed_tracing": True,
                "cost_tracking": True,
                "performance_analytics": True,
                "resource_monitoring": True,
                "log_aggregation": True
            }
        }
    except Exception as e:
        logger.error(f"Error getting observability overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


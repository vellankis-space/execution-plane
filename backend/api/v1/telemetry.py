from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any
from sqlalchemy.orm import Session
from core.database import get_db
from models.telemetry import Trace, Span
import json
import logging
import gzip
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ingest")
@router.post("/ingest/v1/traces")
async def ingest_telemetry(request: Request, db: Session = Depends(get_db)):
    """
    Receive OTLP trace data from OTEL Collector.
    This endpoint receives traces in OTLP/JSON format and stores them in SQLite.
    Supports both /ingest and /ingest/v1/traces paths (OTLP HTTP exporter appends /v1/traces).
    Handles both plain JSON and gzip-compressed payloads.
    """
    try:
        # Get raw body
        body = await request.body()
        
        # Check if body is gzip-compressed (magic bytes: 0x1f 0x8b)
        if len(body) >= 2 and body[0] == 0x1f and body[1] == 0x8b:
            try:
                body = gzip.decompress(body)
                logger.debug("Decompressed gzip payload")
            except Exception as e:
                logger.error(f"Failed to decompress gzip payload: {e}")
                raise HTTPException(status_code=400, detail="Invalid gzip payload")
        
        # Parse JSON
        try:
            data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # OTLP format: { "resourceSpans": [ { "resource": {...}, "scopeSpans": [ { "spans": [...] } ] } ] }
        resource_spans = data.get("resourceSpans", [])
        
        traces_created = 0
        spans_created = 0
        
        for resource_span in resource_spans:
            # Extract service name from resource attributes
            service_name = "execution-plane"
            resource_attrs = resource_span.get("resource", {}).get("attributes", [])
            for attr in resource_attrs:
                if attr.get("key") == "service.name":
                    service_name = attr.get("value", {}).get("stringValue", service_name)
                    break
            
            # Process scope spans
            scope_spans = resource_span.get("scopeSpans", [])
            for scope_span in scope_spans:
                spans_data = scope_span.get("spans", [])
                
                # Group spans by trace_id
                traces_map = {}
                
                for span_data in spans_data:
                    trace_id = span_data.get("traceId", "")
                    span_id = span_data.get("spanId", "")
                    parent_span_id = span_data.get("parentSpanId")
                    name = span_data.get("name", "")
                    kind = span_data.get("kind", "")
                    
                    # Convert timestamps (nanoseconds to ISO8601)
                    start_time_ns = int(span_data.get("startTimeUnixNano", 0))
                    end_time_ns = int(span_data.get("endTimeUnixNano", 0))
                    start_time = datetime.fromtimestamp(start_time_ns / 1e9).isoformat()
                    end_time = datetime.fromtimestamp(end_time_ns / 1e9).isoformat() if end_time_ns else None
                    
                    # Calculate duration in microseconds
                    duration_us = int((end_time_ns - start_time_ns) / 1000) if end_time_ns else 0
                    
                    # Extract status
                    status_data = span_data.get("status", {})
                    status = "ok" if status_data.get("code") == 1 else "error" if status_data.get("code") == 2 else "unset"
                    
                    # Extract attributes
                    attributes = {}
                    for attr in span_data.get("attributes", []):
                        key = attr.get("key")
                        value_obj = attr.get("value", {})
                        # Get the actual value from the union type
                        value = (
                            value_obj.get("stringValue") or
                            value_obj.get("intValue") or
                            value_obj.get("doubleValue") or
                            value_obj.get("boolValue") or
                            value_obj.get("arrayValue") or
                            None
                        )
                        if value is not None:
                            attributes[key] = value
                    
                    # Extract events
                    events = []
                    for event in span_data.get("events", []):
                        event_time_ns = int(event.get("timeUnixNano", 0))
                        event_obj = {
                            "name": event.get("name"),
                            "timestamp": datetime.fromtimestamp(event_time_ns / 1e9).isoformat(),
                            "attributes": {}
                        }
                        for attr in event.get("attributes", []):
                            key = attr.get("key")
                            value_obj = attr.get("value", {})
                            value = (
                                value_obj.get("stringValue") or
                                value_obj.get("intValue") or
                                value_obj.get("doubleValue") or
                                value_obj.get("boolValue") or
                                None
                            )
                            if value is not None:
                                event_obj["attributes"][key] = value
                        events.append(event_obj)
                    
                    # Create or update trace entry
                    if trace_id not in traces_map:
                        traces_map[trace_id] = {
                            "service_name": service_name,
                            "start_time": start_time,
                            "end_time": end_time,
                            "root_span_name": name if not parent_span_id else None,
                            "status": status,
                            "spans": []
                        }
                    else:
                        # Update trace end time if this span ends later
                        if end_time and (not traces_map[trace_id]["end_time"] or end_time > traces_map[trace_id]["end_time"]):
                            traces_map[trace_id]["end_time"] = end_time
                        # Update root span name if this is the root
                        if not parent_span_id and not traces_map[trace_id]["root_span_name"]:
                            traces_map[trace_id]["root_span_name"] = name
                        # Update status to error if any span failed
                        if status == "error":
                            traces_map[trace_id]["status"] = "error"
                    
                    # Add span to trace
                    traces_map[trace_id]["spans"].append({
                        "span_id": span_id,
                        "parent_span_id": parent_span_id,
                        "name": name,
                        "span_kind": str(kind),
                        "start_time": start_time,
                        "end_time": end_time,
                        "duration_us": duration_us,
                        "status": status,
                        "attributes": json.dumps(attributes),
                        "events": json.dumps(events)
                    })
                
                # Store traces and spans in database
                for trace_id, trace_data in traces_map.items():
                    # Calculate duration
                    if trace_data["end_time"] and trace_data["start_time"]:
                        start_dt = datetime.fromisoformat(trace_data["start_time"])
                        end_dt = datetime.fromisoformat(trace_data["end_time"])
                        duration_ms = int((end_dt - start_dt).total_seconds() * 1000)
                    else:
                        duration_ms = 0
                    
                    # Check if trace already exists
                    existing_trace = db.query(Trace).filter(Trace.trace_id == trace_id).first()
                    
                    if not existing_trace:
                        # Create new trace
                        trace = Trace(
                            trace_id=trace_id,
                            service_name=trace_data["service_name"],
                            start_time=trace_data["start_time"],
                            end_time=trace_data["end_time"],
                            duration_ms=duration_ms,
                            status=trace_data["status"],
                            root_span_name=trace_data["root_span_name"] or "unknown"
                        )
                        db.add(trace)
                        traces_created += 1
                    
                    # Add spans
                    for span_dict in trace_data["spans"]:
                        # Check if span already exists
                        existing_span = db.query(Span).filter(Span.span_id == span_dict["span_id"]).first()
                        if not existing_span:
                            span = Span(
                                trace_id=trace_id,
                                **span_dict
                            )
                            db.add(span)
                            spans_created += 1
                
                db.commit()
        
        logger.info(f"Ingested {traces_created} traces and {spans_created} spans")
        return {"status": "success", "traces": traces_created, "spans": spans_created}
        
    except Exception as e:
        logger.error(f"Failed to ingest telemetry: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/stats")
async def get_telemetry_stats(db: Session = Depends(get_db)):
    """
    Debug endpoint to check telemetry database status.
    """
    try:
        trace_count = db.query(Trace).count()
        span_count = db.query(Span).count()
        
        # Get recent traces
        recent_traces = db.query(Trace).order_by(Trace.start_time.desc()).limit(5).all()
        
        # Get sample span attributes to check for agent_id
        sample_spans = db.query(Span).limit(10).all()
        spans_with_agent_id = 0
        for span in sample_spans:
            if span.attributes and '"agent_id"' in span.attributes:
                spans_with_agent_id += 1
        
        return {
            "status": "ok",
            "trace_count": trace_count,
            "span_count": span_count,
            "recent_traces": [
                {
                    "trace_id": t.trace_id,
                    "root_span_name": t.root_span_name,
                    "start_time": t.start_time,
                    "status": t.status
                }
                for t in recent_traces
            ],
            "spans_with_agent_id": f"{spans_with_agent_id}/{len(sample_spans)} sampled spans have agent_id"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

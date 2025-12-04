"""
Custom SQLite Span Exporter for OpenTelemetry
Saves traces and spans to local SQLite database for metrics calculation
"""
import json
import logging
from datetime import datetime, timezone
from typing import Sequence
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from sqlalchemy.orm import Session
from models.telemetry import Trace, Span
from core.database import SessionLocal

logger = logging.getLogger(__name__)


class SQLiteSpanExporter(SpanExporter):
    """
    Custom span exporter that writes OpenTelemetry spans to SQLite database.
    This enables local metrics calculation without relying solely on external collectors.
    """
    
    def __init__(self):
        self.db: Session = None
    
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """
        Export spans to SQLite database.
        """
        if not spans:
            return SpanExportResult.SUCCESS
        
        try:
            # Create a new database session for each export
            self.db = SessionLocal()
            
            # Group spans by trace_id
            traces_dict = {}
            spans_to_save = []
            
            for span in spans:
                try:
                    # Extract trace information
                    trace_id = format(span.context.trace_id, '032x')
                    span_id = format(span.context.span_id, '016x')
                    
                    # Track trace metadata
                    if trace_id not in traces_dict:
                        traces_dict[trace_id] = {
                            'start_time': span.start_time,
                            'end_time': span.end_time,
                            'service_name': span.resource.attributes.get('service.name', 'execution-plane') if span.resource else 'execution-plane',
                            'root_span_name': span.name,
                            'status': 'ok' if span.status.is_ok else 'error'
                        }
                    else:
                        # Update trace end time with latest span
                        if span.end_time and (not traces_dict[trace_id]['end_time'] or span.end_time > traces_dict[trace_id]['end_time']):
                            traces_dict[trace_id]['end_time'] = span.end_time
                        # Update status to error if any span failed
                        if not span.status.is_ok:
                            traces_dict[trace_id]['status'] = 'error'
                    
                    # Convert attributes to JSON
                    attributes = {}
                    if span.attributes:
                        for key, value in span.attributes.items():
                            # Convert to serializable types
                            if isinstance(value, (str, int, float, bool, type(None))):
                                attributes[key] = value
                            else:
                                attributes[key] = str(value)
                    
                    # CRITICAL: Enrich spans with agent_id/workflow_id from trace context
                    # This is how we get agent_id/workflow_id into all spans for metrics filtering
                    try:
                        from services.trace_context import trace_context_manager
                        
                        enriched = False
                        
                        # Strategy 1: Check thread-local context (fastest, most reliable)
                        current_context = trace_context_manager.get_current_context()
                        if current_context:
                            for key, value in current_context.items():
                                if value is not None:
                                    attributes[key] = str(value)
                            logger.info(f"✅ Enriched span {span_id} from thread-local context: {list(current_context.keys())}")
                            enriched = True
                        
                        # Strategy 2: Look up by trace_id (for spans created by Traceloop)
                        if not enriched:
                            trace_metadata = trace_context_manager.get_trace_context(trace_id)
                            if trace_metadata:
                                for key, value in trace_metadata.items():
                                    if key != '_timestamp' and value is not None:
                                        attributes[key] = str(value)
                                logger.info(f"✅ Enriched span {span_id} from trace_id lookup: {list(trace_metadata.keys())}")
                                enriched = True
                        
                        if not enriched:
                            logger.debug(f"No enrichment found for span {span_id} (trace_id: {trace_id})")
                            # DEBUG: Log to file
                            with open("telemetry_debug.log", "a") as f:
                                f.write(f"{datetime.now(timezone.utc)} - No enrichment for span {span_id} trace {trace_id}. Metadata keys: {list(trace_context_manager._trace_metadata.keys())}\n")
                            
                    except Exception as e:
                        logger.error(f"Could not enrich span with trace context: {e}", exc_info=True)
                        with open("telemetry_debug.log", "a") as f:
                            f.write(f"{datetime.now(timezone.utc)} - Error enriching span: {e}\n")
                    
                    # Convert events to JSON
                    events = []
                    if span.events:
                        for event in span.events:
                            event_data = {
                                'name': event.name,
                                'timestamp': event.timestamp,
                                'attributes': {}
                            }
                            if event.attributes:
                                for key, value in event.attributes.items():
                                    if isinstance(value, (str, int, float, bool, type(None))):
                                        event_data['attributes'][key] = value
                                    else:
                                        event_data['attributes'][key] = str(value)
                            events.append(event_data)
                    
                    # Get parent span ID if exists
                    parent_span_id = None
                    if span.parent and span.parent.span_id:
                        parent_span_id = format(span.parent.span_id, '016x')
                    
                    # Calculate duration
                    duration_us = None
                    if span.start_time and span.end_time:
                        duration_us = (span.end_time - span.start_time) // 1000  # Convert to microseconds
                    
                    # Convert timestamps to ISO format
                    start_time_iso = datetime.fromtimestamp(span.start_time / 1e9).isoformat() if span.start_time else None
                    end_time_iso = datetime.fromtimestamp(span.end_time / 1e9).isoformat() if span.end_time else None
                    
                    # Create span object
                    span_obj = Span(
                        span_id=span_id,
                        trace_id=trace_id,
                        parent_span_id=parent_span_id,
                        name=span.name,
                        span_kind=span.kind.name if span.kind else 'INTERNAL',
                        start_time=start_time_iso,
                        end_time=end_time_iso,
                        duration_us=duration_us,
                        status='ok' if span.status.is_ok else 'error',
                        attributes=json.dumps(attributes),
                        events=json.dumps(events),
                        created_at=datetime.now(timezone.utc).isoformat()
                    )
                    
                    spans_to_save.append(span_obj)
                    
                except Exception as e:
                    logger.error(f"Error processing span: {e}")
                    continue
            
            # Save traces first - use merge to handle duplicates gracefully
            # Must commit traces before spans due to foreign key constraint
            for trace_id, trace_data in traces_dict.items():
                try:
                    # Calculate duration
                    duration_ms = None
                    if trace_data['start_time'] and trace_data['end_time']:
                        duration_ms = (trace_data['end_time'] - trace_data['start_time']) // 1_000_000  # Convert to milliseconds
                    
                    # Convert timestamps
                    start_time_iso = datetime.fromtimestamp(trace_data['start_time'] / 1e9).isoformat() if trace_data['start_time'] else None
                    end_time_iso = datetime.fromtimestamp(trace_data['end_time'] / 1e9).isoformat() if trace_data['end_time'] else None
                    
                    trace_obj = Trace(
                        trace_id=trace_id,
                        service_name=trace_data['service_name'],
                        start_time=start_time_iso,
                        end_time=end_time_iso,
                        duration_ms=duration_ms,
                        status=trace_data['status'],
                        root_span_name=trace_data['root_span_name'],
                        created_at=datetime.now(timezone.utc).isoformat()
                    )
                    # Use merge to handle duplicates - updates if exists, inserts if not
                    self.db.merge(trace_obj)
                except Exception as e:
                    logger.debug(f"Trace {trace_id} merge: {e}")
                    continue
            
            # Commit traces first to satisfy foreign key constraints
            try:
                self.db.commit()
            except Exception as e:
                logger.debug(f"Trace commit: {e}")
                self.db.rollback()
            
            # Save all spans - use merge to handle duplicates gracefully
            for span_obj in spans_to_save:
                try:
                    # Ensure trace exists before adding span (foreign key constraint)
                    existing_trace = self.db.query(Trace).filter(Trace.trace_id == span_obj.trace_id).first()
                    if existing_trace:
                        # Use merge to handle duplicates - updates if exists, inserts if not
                        self.db.merge(span_obj)
                    else:
                        logger.debug(f"Skipping span {span_obj.span_id} - trace {span_obj.trace_id} not found")
                except Exception as e:
                    logger.debug(f"Span {span_obj.span_id} merge: {e}")
                    continue
            
            # Commit spans
            self.db.commit()
            logger.debug(f"Successfully exported {len(spans)} spans to SQLite")
            
            return SpanExportResult.SUCCESS
            
        except Exception as e:
            logger.error(f"Error exporting spans to SQLite: {e}")
            if self.db:
                self.db.rollback()
            return SpanExportResult.FAILURE
        finally:
            if self.db:
                self.db.close()
    
    def shutdown(self) -> None:
        """Called when the exporter is shut down."""
        if self.db:
            self.db.close()
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush any buffered spans."""
        return True

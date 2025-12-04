
import logging
from traceloop.sdk import Traceloop
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry import trace, baggage, context
from core.config import settings
from services.sqlite_span_exporter import SQLiteSpanExporter
from datetime import datetime

logger = logging.getLogger(__name__)

class TelemetryService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelemetryService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.enabled = False
        self._initialized = True

    def start(self):
        """
        Initialize Traceloop SDK for OpenLLMetry with traces, metrics, and local SQLite persistence.
        """
        try:
            # Traceloop auto-instruments popular libraries (LangChain, OpenAI, etc.)
            # We point it to our local OTEL Collector via OTLP
            # Use localhost when running locally, otel-collector when in Docker
            endpoint = settings.OTEL_EXPORTER_OTLP_ENDPOINT or "http://localhost:4317"
            
            logger.info(f"🚀 Initializing OpenLLMetry with endpoint: {endpoint}")
            
            # Initialize with both trace and metric exporters
            Traceloop.init(
                app_name="execution-plane",
                disable_batch=False,
                exporter=OTLPSpanExporter(endpoint=endpoint, insecure=True),
                metrics_exporter=OTLPMetricExporter(endpoint=endpoint, insecure=True),
            )
            
            # Add SQLite span exporter for local metrics calculation
            # This ensures traces/spans are persisted locally for the metrics endpoints
            try:
                sqlite_exporter = SQLiteSpanExporter()
                sqlite_processor = BatchSpanProcessor(sqlite_exporter)
                
                # Get the tracer provider and add our custom processor
                tracer_provider = trace.get_tracer_provider()
                if hasattr(tracer_provider, 'add_span_processor'):
                    tracer_provider.add_span_processor(sqlite_processor)
                    logger.info("✅ SQLite span exporter added for local metrics")
                else:
                    logger.warning("⚠️  Could not add SQLite span processor - tracer provider doesn't support it")
            except Exception as e:
                logger.warning(f"⚠️  Failed to add SQLite span exporter: {e}. Metrics will be limited.")
            
            self.enabled = True
            logger.info("✅ OpenLLMetry initialized successfully with traces and metrics")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenLLMetry: {e}")
            self.enabled = False

    async def get_traces(self, limit: int = 10, offset: int = 0, service: str = "execution-plane", tags: str = None):
        """
        Query traces from local SQLite database.
        """
        if not self.enabled:
            return {"data": [], "total": 0, "limit": limit, "offset": offset, "errors": ["Telemetry disabled"]}

        try:
            from core.database import SessionLocal
            from models.telemetry import Trace
            
            db = SessionLocal()
            try:
                query = db.query(Trace).order_by(Trace.start_time.desc())
                
                # Simple tag filtering (if tags provided in format "key=value")
                if tags:
                    # This is a basic implementation. For complex filtering, use the observability router.
                    pass
                
                total = query.count()
                traces = query.offset(offset).limit(limit).all()
                
                result = []
                for t in traces:
                    result.append({
                        "traceID": t.trace_id,
                        "spanID": t.trace_id, # Root span ID usually same or similar
                        "operationName": t.root_span_name,
                        "startTime": int(datetime.fromisoformat(t.start_time).timestamp() * 1000000) if t.start_time else 0,
                        "duration": (t.duration_ms or 0) * 1000, # Microseconds
                        "tags": [],
                        "services": [{"name": t.service_name}],
                    })
                
                return {
                    "data": result,
                    "total": total,
                    "limit": limit,
                    "offset": offset
                }
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to fetch traces from SQLite: {e}")
            return {"data": [], "total": 0, "limit": limit, "offset": offset, "errors": [str(e)]}

    async def get_trace_details(self, trace_id: str):
        """
        Get details of a specific trace from SQLite.
        """
        if not self.enabled:
            return None

        try:
            from core.database import SessionLocal
            from models.telemetry import Trace, Span
            import json
            
            db = SessionLocal()
            try:
                trace = db.query(Trace).filter(Trace.trace_id == trace_id).first()
                if not trace:
                    return None
                
                spans = db.query(Span).filter(Span.trace_id == trace_id).all()
                
                # Format as Jaeger-like response for compatibility
                spans_data = []
                for span in spans:
                    attributes = []
                    if span.attributes:
                        try:
                            attrs = json.loads(span.attributes)
                            for k, v in attrs.items():
                                attributes.append({"key": k, "type": "string", "value": str(v)})
                        except:
                            pass
                            
                    spans_data.append({
                        "traceID": span.trace_id,
                        "spanID": span.span_id,
                        "operationName": span.name,
                        "references": [{"refType": "CHILD_OF", "traceID": span.trace_id, "spanID": span.parent_span_id}] if span.parent_span_id else [],
                        "startTime": int(datetime.fromisoformat(span.start_time).timestamp() * 1000000) if span.start_time else 0,
                        "duration": (span.duration_us or 0),
                        "tags": attributes,
                        "logs": [],
                        "processID": "p1",
                        "warnings": None
                    })
                
                return {
                    "traceID": trace.trace_id,
                    "spans": spans_data,
                    "processes": {
                        "p1": {
                            "serviceName": trace.service_name,
                            "tags": []
                        }
                    }
                }
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to fetch trace details from SQLite: {e}")
            return None

    def set_span_attributes(self, **attributes):
        """
        Set custom attributes on the current active span AND propagate via baggage.
        This ensures agent_id/workflow_id are available in all child spans.
        Usage: telemetry_service.set_span_attributes(agent_id="123", workflow_id="456")
        """
        if not self.enabled:
            return
            
        try:
            # Set attributes on current span
            span = trace.get_current_span()
            if span and span.is_recording():
                for key, value in attributes.items():
                    if value is not None:
                        span.set_attribute(key, str(value))
            
            # CRITICAL: Also set in baggage for propagation to ALL child spans
            # This is the key to making agent_id/workflow_id available in LLM spans
            ctx = context.get_current()
            for key, value in attributes.items():
                if value is not None:
                    ctx = baggage.set_baggage(key, str(value), context=ctx)
            context.attach(ctx)
            
        except Exception as e:
            logger.debug(f"Failed to set span attributes: {e}")
    
    def get_baggage(self, key: str):
        """
        Get a value from baggage (context propagation).
        """
        try:
            return baggage.get_baggage(key)
        except Exception:
            return None
    
    def get_current_span(self):
        """
        Get the current active span for manual instrumentation.
        """
        if not self.enabled:
            return None
            
        try:
            from opentelemetry import trace
            return trace.get_current_span()
        except Exception as e:
            logger.debug(f"Failed to get current span: {e}")
            return None

telemetry_service = TelemetryService()

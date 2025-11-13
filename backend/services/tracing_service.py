"""
Distributed tracing service using OpenTelemetry
"""
import logging
from typing import Optional, Dict, Any
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

logger = logging.getLogger(__name__)

# Initialize tracing
tracer_provider = TracerProvider(
    resource=Resource.create({"service.name": "execution-plane"})
)

# Add console exporter (can be replaced with OTLP exporter for production)
tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer(__name__)


class TracingService:
    """Service for distributed tracing"""
    
    @staticmethod
    def get_tracer():
        """Get the tracer instance"""
        return tracer
    
    @staticmethod
    def start_span(name: str, attributes: Optional[Dict[str, Any]] = None):
        """Start a new span"""
        span = tracer.start_span(name)
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
        return span
    
    @staticmethod
    def instrument_fastapi(app):
        """Instrument FastAPI application"""
        try:
            FastAPIInstrumentor.instrument_app(app)
            logger.info("FastAPI instrumentation enabled")
        except Exception as e:
            logger.warning(f"Could not instrument FastAPI: {e}")
    
    @staticmethod
    def instrument_sqlalchemy(engine):
        """Instrument SQLAlchemy engine"""
        try:
            SQLAlchemyInstrumentor().instrument(engine=engine)
            logger.info("SQLAlchemy instrumentation enabled")
        except Exception as e:
            logger.warning(f"Could not instrument SQLAlchemy: {e}")


def setup_tracing(app, engine):
    """Setup tracing for the application"""
    tracing_service = TracingService()
    tracing_service.instrument_fastapi(app)
    tracing_service.instrument_sqlalchemy(engine)
    return tracing_service


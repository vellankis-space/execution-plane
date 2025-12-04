from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
import json


class Trace(Base):
    __tablename__ = "traces"
    
    trace_id = Column(String(32), primary_key=True, index=True)
    service_name = Column(String(255))
    start_time = Column(String(255))  # ISO8601
    end_time = Column(String(255))
    duration_ms = Column(Integer)
    status = Column(String(20))
    root_span_name = Column(String(255))
    created_at = Column(String(255))
    
    # Relationship to spans
    spans = relationship("Span", back_populates="trace", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "trace_id": self.trace_id,
            "service_name": self.service_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "root_span_name": self.root_span_name,
            "created_at": self.created_at
        }


class Span(Base):
    __tablename__ = "spans"
    
    span_id = Column(String(16), primary_key=True, index=True)
    trace_id = Column(String(32), ForeignKey("traces.trace_id"), nullable=False, index=True)
    parent_span_id = Column(String(16))
    name = Column(String(255), index=True)
    span_kind = Column(String(50))
    start_time = Column(String(255))  # ISO8601
    end_time = Column(String(255))
    duration_us = Column(Integer)
    status = Column(String(20))
    attributes = Column(Text)  # JSON string
    events = Column(Text)  # JSON string
    created_at = Column(String(255))
    
    # Relationship to trace
    trace = relationship("Trace", back_populates="spans")
    
    def to_dict(self):
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "span_kind": self.span_kind,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_us": self.duration_us,
            "status": self.status,
            "attributes": json.loads(self.attributes) if self.attributes else {},
            "events": json.loads(self.events) if self.events else [],
            "created_at": self.created_at
        }

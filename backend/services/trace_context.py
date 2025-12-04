"""
Trace Context Manager for Agent/Workflow Identification
Stores trace_id -> metadata mapping for span enrichment
"""
import contextvars
import threading
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

class TraceContextManager:
    """
    Singleton that maintains a mapping of trace_id to execution metadata.
    This allows the SQLite exporter to enrich spans with agent_id/workflow_id.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._trace_metadata: Dict[str, Dict] = {}
        self._context_var = contextvars.ContextVar("trace_context", default={})
        self._initialized = True
        self._cleanup_interval = timedelta(hours=1)
        self._last_cleanup = datetime.now(timezone.utc)
    
    def set_trace_context(self, trace_id: str, **metadata):
        """
        Store metadata for a trace_id.
        Usage: set_trace_context(trace_id, agent_id="123", workflow_id="456")
        """
        with self._lock:
            self._trace_metadata[trace_id] = {
                **metadata,
                '_timestamp': datetime.now(timezone.utc)
            }
            self._cleanup_old_traces()
    
    def get_trace_context(self, trace_id: str) -> Optional[Dict]:
        """Get metadata for a trace_id."""
        return self._trace_metadata.get(trace_id)
    
    def set_current_context(self, **metadata):
        """Set context for the current task/thread."""
        self._context_var.set(metadata)
    
    def get_current_context(self) -> Optional[Dict]:
        """Get context for the current task/thread."""
        return self._context_var.get()
    
    def clear_current_context(self):
        """Clear context for the current task/thread."""
        self._context_var.set({})
    
    def _cleanup_old_traces(self):
        """Remove trace metadata older than 1 hour to prevent memory leaks."""
        now = datetime.now(timezone.utc)
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        self._last_cleanup = now
        cutoff = now - timedelta(hours=1)
        
        traces_to_remove = [
            trace_id for trace_id, metadata in self._trace_metadata.items()
            if metadata.get('_timestamp', now) < cutoff
        ]
        
        for trace_id in traces_to_remove:
            del self._trace_metadata[trace_id]

# Global instance
trace_context_manager = TraceContextManager()

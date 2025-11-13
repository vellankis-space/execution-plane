"""
Langfuse integration for enhanced observability and cost tracking
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from langfuse import Langfuse
    from langfuse.decorators import langfuse_context, observe
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False

import os
from core.config import settings

logger = logging.getLogger(__name__)


class LangfuseIntegration:
    """Integration with Langfuse for LLM observability"""
    
    def __init__(self):
        self.client = None
        self.enabled = False
        
        if LANGFUSE_AVAILABLE:
            try:
                langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
                langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
                langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
                
                if langfuse_public_key and langfuse_secret_key:
                    self.client = Langfuse(
                        public_key=langfuse_public_key,
                        secret_key=langfuse_secret_key,
                        host=langfuse_host
                    )
                    self.enabled = True
                    logger.info("Langfuse integration enabled")
                else:
                    logger.info("Langfuse keys not configured, integration disabled")
            except Exception as e:
                logger.warning(f"Could not initialize Langfuse: {e}")
    
    def trace_agent_execution(
        self,
        agent_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Create a trace for agent execution"""
        if not self.enabled or not self.client:
            return None
        
        try:
            trace = self.client.trace(
                name=f"agent_execution",
                id=f"agent_{agent_id}_{datetime.utcnow().isoformat()}",
                user_id=user_id,
                metadata={
                    "agent_id": agent_id,
                    **(metadata or {})
                }
            )
            return trace
        except Exception as e:
            logger.warning(f"Error creating Langfuse trace: {e}")
            return None
    
    def trace_workflow_execution(
        self,
        workflow_id: str,
        execution_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Create a trace for workflow execution"""
        if not self.enabled or not self.client:
            return None
        
        try:
            trace = self.client.trace(
                name=f"workflow_execution",
                id=execution_id,
                user_id=user_id,
                metadata={
                    "workflow_id": workflow_id,
                    "execution_id": execution_id,
                    **(metadata or {})
                }
            )
            return trace
        except Exception as e:
            logger.warning(f"Error creating Langfuse trace: {e}")
            return None
    
    def get_cost_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        project_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get cost analytics from Langfuse"""
        if not self.enabled or not self.client:
            return None
        
        try:
            # Langfuse provides cost tracking through their API
            # This would need to be implemented based on Langfuse API
            # For now, return None as placeholder
            return None
        except Exception as e:
            logger.warning(f"Error getting Langfuse cost analytics: {e}")
            return None


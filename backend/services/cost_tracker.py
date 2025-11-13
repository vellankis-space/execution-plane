"""
Cost tracker callback for LangChain to track API usage
"""
import logging
from typing import Any, Dict, Optional
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from services.cost_tracking_service import CostTrackingService

logger = logging.getLogger(__name__)


class CostTrackingCallback(BaseCallbackHandler):
    """Callback handler to track API costs"""
    
    def __init__(self, cost_service: CostTrackingService, agent_id: Optional[str] = None, 
                 workflow_id: Optional[str] = None, execution_id: Optional[str] = None):
        super().__init__()
        self.cost_service = cost_service
        self.agent_id = agent_id
        self.workflow_id = workflow_id
        self.execution_id = execution_id
        self.api_calls = []
    
    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Called when LLM finishes"""
        try:
            # Extract token usage from response
            llm_output = response.llm_output or {}
            token_usage = llm_output.get("token_usage", {})
            
            # Get provider and model from kwargs
            provider = kwargs.get("provider", "unknown")
            model = kwargs.get("model", "unknown")
            
            input_tokens = token_usage.get("prompt_tokens", 0) or token_usage.get("input_tokens", 0)
            output_tokens = token_usage.get("completion_tokens", 0) or token_usage.get("output_tokens", 0)
            
            # If no token usage info, estimate based on response
            if input_tokens == 0 and output_tokens == 0:
                # Rough estimation: ~4 characters per token
                if response.generations and len(response.generations) > 0:
                    total_chars = sum(len(str(gen)) for gen in response.generations)
                    output_tokens = int(total_chars / 4)
                    input_tokens = 100  # Default estimate for input
            
            # Track the API call
            if input_tokens > 0 or output_tokens > 0:
                api_call = await self.cost_service.track_api_call(
                    provider=provider,
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    agent_id=self.agent_id,
                    workflow_id=self.workflow_id,
                    execution_id=self.execution_id,
                    call_type="chat",
                    metadata={
                        "llm_output": llm_output,
                        "generation_count": len(response.generations) if response.generations else 0
                    }
                )
                self.api_calls.append(api_call)
        except Exception as e:
            logger.warning(f"Error tracking cost in callback: {str(e)}")


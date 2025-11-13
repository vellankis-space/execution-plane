"""
LLM service using LiteLLM for unified provider management
"""
import os
import logging
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq

try:
    from litellm import completion, stream_completion
    from litellm.integrations.langfuse import LangfuseLogger
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    logging.warning("LiteLLM not available, using direct provider initialization")

try:
    from langfuse import Langfuse
    from langfuse.decorators import langfuse_context, observe
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    logging.warning("Langfuse not available")

from core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for managing LLM interactions with LiteLLM and Langfuse"""
    
    def __init__(self):
        self.langfuse_client = None
        self.langfuse_logger = None
        
        if LANGFUSE_AVAILABLE:
            try:
                langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
                langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
                langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
                
                if langfuse_public_key and langfuse_secret_key:
                    self.langfuse_client = Langfuse(
                        public_key=langfuse_public_key,
                        secret_key=langfuse_secret_key,
                        host=langfuse_host
                    )
                    logger.info("Langfuse client initialized")
                    
                    # Setup LiteLLM callback for Langfuse
                    if LITELLM_AVAILABLE:
                        self.langfuse_logger = LangfuseLogger(
                            public_key=langfuse_public_key,
                            secret_key=langfuse_secret_key,
                            host=langfuse_host
                        )
            except Exception as e:
                logger.warning(f"Could not initialize Langfuse: {e}")
    
    def initialize_llm(
        self,
        provider: str,
        model: str,
        temperature: float = 0.7,
        user_api_key: Optional[str] = None,
        use_litellm: bool = True
    ):
        """Initialize LLM with optional LiteLLM and Langfuse integration"""
        
        # Use LiteLLM if available and enabled
        if use_litellm and LITELLM_AVAILABLE:
            return self._initialize_with_litellm(provider, model, temperature, user_api_key)
        
        # Fallback to direct provider initialization
        return self._initialize_direct(provider, model, temperature, user_api_key)
    
    def _initialize_with_litellm(
        self,
        provider: str,
        model: str,
        temperature: float,
        user_api_key: Optional[str]
    ):
        """Initialize LLM using LiteLLM"""
        try:
            from langchain_community.chat_models import ChatLiteLLM
        except ImportError:
            logger.warning("langchain_community not available, falling back to direct")
            return self._initialize_direct(provider, model, temperature, user_api_key)
        
        # Map provider to LiteLLM model name
        litellm_model = self._get_litellm_model_name(provider, model)
        
        # Configure LiteLLM
        litellm_kwargs = {
            "model": litellm_model,
            "temperature": temperature,
        }
        
        # Add API key if provided
        if user_api_key:
            if provider.lower() == "openai":
                litellm_kwargs["api_key"] = user_api_key
            elif provider.lower() == "anthropic":
                litellm_kwargs["anthropic_api_key"] = user_api_key
            elif provider.lower() == "groq":
                litellm_kwargs["groq_api_key"] = user_api_key
        
        # Add Langfuse callback if available
        if self.langfuse_logger:
            litellm_kwargs["callbacks"] = [self.langfuse_logger]
        
        try:
            # Use ChatLiteLLM from langchain_community
            return ChatLiteLLM(**litellm_kwargs)
        except Exception as e:
            logger.warning(f"Error initializing LiteLLM, falling back to direct: {e}")
            return self._initialize_direct(provider, model, temperature, user_api_key)
    
    def _initialize_direct(
        self,
        provider: str,
        model: str,
        temperature: float,
        user_api_key: Optional[str]
    ):
        """Initialize LLM directly (fallback)"""
        from langchain_openai import ChatOpenAI
        from langchain_anthropic import ChatAnthropic
        from langchain_groq import ChatGroq
        
        api_key = user_api_key or self._get_default_api_key(provider)
        
        if provider.lower() == "openai":
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=api_key
            )
        elif provider.lower() == "anthropic":
            return ChatAnthropic(
                model=model,
                temperature=temperature,
                api_key=api_key
            )
        elif provider.lower() == "groq":
            return ChatGroq(
                model=model,
                temperature=temperature,
                api_key=api_key
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _get_litellm_model_name(self, provider: str, model: str) -> str:
        """Convert provider+model to LiteLLM model name"""
        provider_lower = provider.lower()
        
        if provider_lower == "openai":
            return f"openai/{model}"
        elif provider_lower == "anthropic":
            return f"anthropic/{model}"
        elif provider_lower == "groq":
            return f"groq/{model}"
        else:
            return model
    
    def _get_default_api_key(self, provider: str) -> Optional[str]:
        """Get default API key from settings"""
        provider_lower = provider.lower()
        if provider_lower == "openai":
            return settings.OPENAI_API_KEY
        elif provider_lower == "anthropic":
            return settings.ANTHROPIC_API_KEY
        elif provider_lower == "groq":
            return settings.GROQ_API_KEY
        return None
    
    def trace_agent_execution(
        self,
        agent_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Create a Langfuse trace for agent execution"""
        if not self.langfuse_client:
            return None
        
        trace = self.langfuse_client.trace(
            name=f"agent_execution_{agent_id}",
            user_id=user_id,
            metadata=metadata or {}
        )
        return trace
    
    def trace_workflow_execution(
        self,
        workflow_id: str,
        execution_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Create a Langfuse trace for workflow execution"""
        if not self.langfuse_client:
            return None
        
        trace = self.langfuse_client.trace(
            name=f"workflow_execution_{workflow_id}",
            id=execution_id,
            user_id=user_id,
            metadata=metadata or {}
        )
        return trace


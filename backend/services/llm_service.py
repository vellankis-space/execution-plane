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
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    logging.warning("LiteLLM not available, using direct provider initialization")

from core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for managing LLM interactions with LiteLLM"""
    
    def __init__(self):
        pass
    
    def initialize_llm(
        self,
        provider: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        user_api_key: Optional[str] = None,
        use_litellm: bool = True
    ):
        """Initialize LLM with optional LiteLLM integration"""
        
        # Use LiteLLM if available and enabled
        if use_litellm and LITELLM_AVAILABLE:
            return self._initialize_with_litellm(provider, model, temperature, max_tokens, user_api_key)
        
        # Fallback to direct provider initialization
        return self._initialize_direct(provider, model, temperature, max_tokens, user_api_key)
    
    def _initialize_with_litellm(
        self,
        provider: str,
        model: str,
        temperature: float,
        max_tokens: int,
        user_api_key: Optional[str]
    ):
        """Initialize LLM using LiteLLM"""
        try:
            from langchain_community.chat_models import ChatLiteLLM
        except ImportError:
            logger.warning("langchain_community not available, falling back to direct")
            return self._initialize_direct(provider, model, temperature, max_tokens, user_api_key)
        
        # Map provider to LiteLLM model name
        litellm_model = self._get_litellm_model_name(provider, model)
        
        # Configure LiteLLM
        litellm_kwargs = {
            "model": litellm_model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # Add API key if provided
        if user_api_key:
            provider_lower = provider.lower()
            if provider_lower == "openai":
                litellm_kwargs["api_key"] = user_api_key
            elif provider_lower == "anthropic":
                litellm_kwargs["anthropic_api_key"] = user_api_key
            elif provider_lower == "groq":
                litellm_kwargs["groq_api_key"] = user_api_key
            elif provider_lower == "openrouter":
                litellm_kwargs["openrouter_api_key"] = user_api_key
        
        try:
            # Use ChatLiteLLM from langchain_community
            return ChatLiteLLM(**litellm_kwargs)
        except Exception as e:
            logger.warning(f"Error initializing LiteLLM, falling back to direct: {e}")
            return self._initialize_direct(provider, model, temperature, max_tokens, user_api_key)
    
    def _initialize_direct(
        self,
        provider: str,
        model: str,
        temperature: float,
        max_tokens: int,
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
                max_tokens=max_tokens,
                api_key=api_key
            )
        elif provider.lower() == "anthropic":
            return ChatAnthropic(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key
            )
        elif provider.lower() == "groq":
            return ChatGroq(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key
            )
        elif provider.lower() == "openrouter":
            # OpenRouter uses OpenAI-compatible API with custom base_url
            # For tool use, we need to ensure routing to tool-capable providers
            # Use extra_body to pass OpenRouter-specific fields in the JSON request body
            # This avoids the TypeError from passing unknown kwargs to OpenAI SDK
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://execution-plane.local",
                    "X-Title": "Execution Plane Agent"
                },
                extra_body={
                    "provider": {
                        "order": [
                            "OpenAI",
                            "Anthropic",
                            "Google",
                            "Cohere",
                            "Fireworks"
                        ],
                        "allow_fallbacks": True
                    }
                }
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
        elif provider_lower == "openrouter":
            return f"openrouter/{model}"
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
    


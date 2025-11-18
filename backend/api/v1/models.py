from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel
import httpx
import os

router = APIRouter()

class ModelResponse(BaseModel):
    provider: str
    models: List[str]

# Provider API endpoints for fetching models
PROVIDER_ENDPOINTS = {
    "openai": {
        "url": "https://api.openai.com/v1/models",
        "requires_key": True,
        "env_key": "OPENAI_API_KEY"
    },
    "anthropic": {
        "url": "https://api.anthropic.com/v1/models",
        "requires_key": True,
        "env_key": "ANTHROPIC_API_KEY"
    },
    "groq": {
        "url": "https://api.groq.com/openai/v1/models",
        "requires_key": True,
        "env_key": "GROQ_API_KEY"
    },
    "google": {
        "url": "https://generativelanguage.googleapis.com/v1/models",
        "requires_key": True,
        "env_key": "GOOGLE_API_KEY"
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/models",
        "requires_key": False,
        "env_key": None
    },
    "together": {
        "url": "https://api.together.xyz/v1/models",
        "requires_key": True,
        "env_key": "TOGETHER_API_KEY"
    },
    "fireworks": {
        "url": "https://api.fireworks.ai/inference/v1/models",
        "requires_key": True,
        "env_key": "FIREWORKS_API_KEY"
    },
    "cohere": {
        "url": "https://api.cohere.ai/v1/models",
        "requires_key": True,
        "env_key": "COHERE_API_KEY"
    },
    "mistral": {
        "url": "https://api.mistral.ai/v1/models",
        "requires_key": True,
        "env_key": "MISTRAL_API_KEY"
    },
}

# Fallback models when API is unavailable or doesn't have a models endpoint
FALLBACK_MODELS = {
    "openai": [
        "gpt-4o",
        "gpt-4o-mini", 
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "o1-preview",
        "o1-mini"
    ],
    "anthropic": [
        "claude-sonnet-4-5",
        "claude-opus-4-1",
        "claude-3-7-sonnet",
        "claude-3-5-sonnet",
        "claude-3-5-haiku",
        "claude-3-opus",
        "claude-3-sonnet",
        "claude-3-haiku"
    ],
    "google": [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b"
    ],
    "groq": [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma-2-9b-it",
        "llama-guard-3-8b"
    ],
    "openrouter": [
        "anthropic/claude-sonnet-4-5",
        "openai/gpt-4o",
        "google/gemini-2.5-pro",
        "meta-llama/llama-3.3-70b-instruct",
        "anthropic/claude-3-5-haiku",
        "deepseek/deepseek-chat",
        "qwen/qwen-2.5-72b-instruct",
        "mistralai/mistral-large"
    ],
    "together": [
        "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
        "mistralai/Mixtral-8x22B-Instruct-v0.1",
        "deepseek-ai/DeepSeek-V3",
        "Qwen/Qwen2.5-72B-Instruct-Turbo"
    ],
    "fireworks": [
        "accounts/fireworks/models/llama-v3p3-70b-instruct",
        "accounts/fireworks/models/llama-v3p1-405b-instruct",
        "accounts/fireworks/models/mixtral-8x22b-instruct",
        "accounts/fireworks/models/qwen2p5-72b-instruct",
        "accounts/fireworks/models/deepseek-v3"
    ],
    "cohere": [
        "command-r-plus",
        "command-r",
        "command",
        "command-light",
        "command-r-08-2024",
        "command-r-plus-08-2024"
    ],
    "meta": [
        "llama-3.3-70b",
        "llama-3.2-90b-vision",
        "llama-3.1-405b",
        "llama-3.1-70b",
        "llama-3.1-8b"
    ],
    "mistral": [
        "mistral-large-2411",
        "mistral-large-2407",
        "mistral-medium",
        "mistral-small",
        "mixtral-8x7b",
        "pixtral-large-2411"
    ],
}

async def fetch_models_from_provider(provider: str, api_key: Optional[str] = None) -> List[str]:
    """
    Fetch models from provider's API if possible, otherwise return static list.
    This function always returns models - API keys are optional for real-time updates.
    """
    
    # Always have fallback models available
    fallback_models = FALLBACK_MODELS.get(provider, [])
    
    # Check if provider has API endpoint
    if provider not in PROVIDER_ENDPOINTS:
        # Return fallback models for providers without API endpoint
        return fallback_models
    
    endpoint_config = PROVIDER_ENDPOINTS[provider]
    
    # Get API key from environment if required
    if endpoint_config["requires_key"]:
        if not api_key:
            api_key = os.getenv(endpoint_config["env_key"])
        if not api_key:
            # No API key available - return static fallback list
            # Users can still see all models without needing keys
            return fallback_models
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {}
            request_url = endpoint_config["url"]
            
            # Set authentication headers based on provider
            if provider == "openai":
                headers["Authorization"] = f"Bearer {api_key}"
            elif provider == "anthropic":
                headers["x-api-key"] = api_key
                headers["anthropic-version"] = "2023-06-01"
            elif provider == "groq":
                headers["Authorization"] = f"Bearer {api_key}"
            elif provider == "google":
                # Google uses query parameter for API key
                request_url = f"{endpoint_config['url']}?key={api_key}"
            elif provider == "together":
                headers["Authorization"] = f"Bearer {api_key}"
            elif provider == "fireworks":
                headers["Authorization"] = f"Bearer {api_key}"
            elif provider == "cohere":
                headers["Authorization"] = f"Bearer {api_key}"
            elif provider == "mistral":
                headers["Authorization"] = f"Bearer {api_key}"
            
            response = await client.get(request_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse response based on provider format
                if provider == "openai" or provider == "groq":
                    # OpenAI-compatible format
                    models = [model["id"] for model in data.get("data", [])]
                    # Filter for chat models
                    if provider == "openai":
                        models = [m for m in models if any(x in m for x in ["gpt-", "o1-"])]
                    return models if models else fallback_models
                
                elif provider == "anthropic":
                    # Anthropic format
                    models = [model["id"] for model in data.get("data", [])]
                    return models if models else fallback_models
                
                elif provider == "google":
                    # Google format - models have "name" field like "models/gemini-pro"
                    models = [model.get("name", "").replace("models/", "") for model in data.get("models", [])]
                    # Filter for generation models (not embedding models)
                    models = [m for m in models if "gemini" in m.lower() and m]
                    return models if models else fallback_models
                
                elif provider == "openrouter":
                    # OpenRouter format
                    models = [model["id"] for model in data.get("data", [])]
                    # Get top models
                    return models[:20] if models else fallback_models
                
                elif provider == "together":
                    # Together AI format
                    models = [model["id"] for model in data.get("data", [])]
                    # Filter for instruction-tuned models
                    models = [m for m in models if "instruct" in m.lower() or "turbo" in m.lower()]
                    return models[:15] if models else fallback_models
                
                elif provider == "fireworks":
                    # Fireworks AI format (OpenAI-compatible)
                    models = [model["id"] for model in data.get("data", [])]
                    # Filter for text generation models
                    models = [m for m in models if not any(x in m.lower() for x in ["embed", "whisper", "vision"])]
                    return models[:20] if models else fallback_models
                
                elif provider == "cohere":
                    # Cohere format
                    models = [model["name"] for model in data.get("models", [])]
                    return models if models else fallback_models
                
                elif provider == "mistral":
                    # Mistral format (OpenAI-compatible)
                    models = [model["id"] for model in data.get("data", [])]
                    return models if models else fallback_models
            
            # Fallback on any error or non-200 response
            return fallback_models
            
    except Exception as e:
        print(f"Error fetching models from {provider}: {e}")
        # Always return fallback models on error - users can still see available models
        return fallback_models

@router.get("/providers", response_model=List[str])
async def get_providers():
    """Get list of available LLM providers"""
    return list(FALLBACK_MODELS.keys())

@router.get("/{provider}", response_model=ModelResponse)
async def get_models_by_provider(provider: str, api_key: Optional[str] = None):
    """
    Get available models for a specific provider.
    
    Returns models from the provider's API if API key is available (for real-time updates),
    otherwise returns a comprehensive static list. No API key required to view models.
    """
    if provider not in FALLBACK_MODELS:
        raise HTTPException(
            status_code=404, 
            detail=f"Provider '{provider}' not found. Available providers: {', '.join(FALLBACK_MODELS.keys())}"
        )
    
    # Fetch models (will use API if key available, otherwise returns static list)
    models = await fetch_models_from_provider(provider, api_key)
    
    return ModelResponse(
        provider=provider,
        models=models
    )

@router.get("/", response_model=Dict[str, List[str]])
async def get_all_models():
    """
    Get all available models for all providers.
    
    Returns models from each provider's API if API keys are configured,
    otherwise returns comprehensive static lists. No API keys required.
    """
    all_models = {}
    
    # Fetch models for each provider
    for provider in FALLBACK_MODELS.keys():
        try:
            models = await fetch_models_from_provider(provider)
            all_models[provider] = models
        except Exception as e:
            print(f"Error fetching models for {provider}: {e}")
            # Always return fallback models - users can still see all models
            all_models[provider] = FALLBACK_MODELS.get(provider, [])
    
    return all_models

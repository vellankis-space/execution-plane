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
        "requires_key": True,
        "env_key": "OPENROUTER_API_KEY"
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

# Known deprecated/decommissioned models to filter out from API responses
DEPRECATED_MODELS = {
    "groq": [
        "llama-3.3-70b-specdec",        # Decommissioned - use llama-3.3-70b-versatile
        "llama-3.2-90b-text-preview",   # Decommissioned
        "llama-3.2-90b-vision-preview", # Decommissioned
    ],
    "openai": [],
    "anthropic": [],
    "google": [],
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
        # Active models only - decommissioned models removed
        "llama-3.3-70b-versatile",  # Recommended for most tasks
        "llama-3.1-8b-instant",
        "llama3-70b-8192",  # Legacy but stable
        "llama3-8b-8192",   # Legacy but stable
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "gemma-7b-it",
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

def filter_deprecated_models(provider: str, models: List[str]) -> List[str]:
    """
    Filter out known deprecated/decommissioned models from a model list.
    
    Args:
        provider: Provider name (e.g., 'groq', 'openai')
        models: List of model IDs
    
    Returns:
        Filtered list with deprecated models removed
    """
    deprecated = DEPRECATED_MODELS.get(provider, [])
    if not deprecated:
        return models
    
    original_count = len(models)
    filtered_models = [m for m in models if m not in deprecated]
    removed_count = original_count - len(filtered_models)
    
    if removed_count > 0:
        print(f"Filtered out {removed_count} deprecated {provider} model(s): {[m for m in models if m in deprecated]}")
    
    return filtered_models


def apply_search_filter(models: List[str], search: Optional[str]) -> List[str]:
    """Filter models by case-insensitive substring match."""
    if not search:
        return models
    query = search.strip().lower()
    if not query:
        return models
    return [model for model in models if query in model.lower()]

async def fetch_models_from_provider(provider: str, api_key: Optional[str] = None) -> List[str]:
    """
    Fetch models from provider's API if possible, otherwise return static list.
    This function always returns models - API keys are optional for real-time updates.
    Automatically filters out known deprecated/decommissioned models.
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
            elif provider == "openrouter":
                headers["Authorization"] = f"Bearer {api_key}"
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
                    
                    # Filter for chat models (OpenAI)
                    if provider == "openai":
                        models = [m for m in models if any(x in m for x in ["gpt-", "o1-"])]
                    
                    # Filter out deprecated models only (do not restrict to fallback list)
                    models = filter_deprecated_models(provider, models)
                    return models if models else fallback_models
                
                elif provider == "anthropic":
                    # Anthropic format
                    models = [model["id"] for model in data.get("data", [])]
                    models = filter_deprecated_models(provider, models)
                    return models if models else fallback_models
                
                elif provider == "google":
                    # Google format - models have "name" field like "models/gemini-pro"
                    models = [model.get("name", "").replace("models/", "") for model in data.get("models", [])]
                    # Filter for generation models (not embedding models)
                    models = [m for m in models if "gemini" in m.lower() and m]
                    models = filter_deprecated_models(provider, models)
                    return models if models else fallback_models
                
                elif provider == "openrouter":
                    # OpenRouter format - return all text-capable models
                    models = []
                    for model_info in data.get("data", []):
                        model_id = model_info.get("id")
                        if not model_id:
                            continue
                        architecture = model_info.get("architecture", {}) or {}
                        output_modalities = architecture.get("output_modalities") or []
                        # Keep models that can generate text (default to True if unspecified)
                        supports_text = (not output_modalities) or any(
                            isinstance(modality, str) and modality.lower() == "text"
                            for modality in output_modalities
                        )
                        if supports_text:
                            models.append(model_id)
                    models = filter_deprecated_models(provider, models)
                    return models if models else fallback_models
                
                elif provider == "together":
                    # Together AI format
                    models = [model["id"] for model in data.get("data", [])]
                    # Filter for instruction-tuned models
                    models = [m for m in models if "instruct" in m.lower() or "turbo" in m.lower()]
                    models = filter_deprecated_models(provider, models)
                    return models[:15] if models else fallback_models
                
                elif provider == "fireworks":
                    # Fireworks AI format (OpenAI-compatible)
                    models = [model["id"] for model in data.get("data", [])]
                    # Filter for text generation models
                    models = [m for m in models if not any(x in m.lower() for x in ["embed", "whisper", "vision"])]
                    models = filter_deprecated_models(provider, models)
                    return models[:20] if models else fallback_models
                
                elif provider == "cohere":
                    # Cohere format
                    models = [model["name"] for model in data.get("models", [])]
                    models = filter_deprecated_models(provider, models)
                    return models if models else fallback_models
                
                elif provider == "mistral":
                    # Mistral format (OpenAI-compatible)
                    models = [model["id"] for model in data.get("data", [])]
                    models = filter_deprecated_models(provider, models)
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
async def get_models_by_provider(
    provider: str,
    api_key: Optional[str] = None,
    search: Optional[str] = None
):
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
    models = apply_search_filter(models, search)
    
    return ModelResponse(
        provider=provider,
        models=models
    )

@router.get("/", response_model=Dict[str, List[str]])
async def get_all_models(search: Optional[str] = None):
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
            filtered = apply_search_filter(models, search)
            if search:
                if filtered:
                    all_models[provider] = filtered
            else:
                all_models[provider] = filtered
        except Exception as e:
            print(f"Error fetching models for {provider}: {e}")
            # Always return fallback models - users can still see all models
            fallback = FALLBACK_MODELS.get(provider, [])
            filtered_fallback = apply_search_filter(fallback, search)
            if not search or filtered_fallback:
                all_models[provider] = filtered_fallback

    # If search query supplied, omit providers with no matches
    if search:
        return all_models
    return all_models

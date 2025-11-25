"""
Rate Limit Handler Service
Handles rate limiting errors from LLM providers and automatically falls back to alternative models
"""
import time
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimitHandler:
    """
    Handles rate limiting errors and provides fallback strategies
    """
    
    # Fallback model configurations per provider (in priority order - most capable to fastest/cheapest)
    FALLBACK_MODELS = {
        "groq": [
            # Llama 3.3 models (newest, most capable)
            "llama-3.3-70b-versatile",
            # Note: llama-3.3-70b-specdec has been DECOMMISSIONED
            # Note: llama-3.1-70b-versatile has been DECOMMISSIONED
            
            # Llama 3.1 models (very capable)
            "llama-3.1-8b-instant",
            
            # Llama 3.2 models (newer variants with vision support)
            # Note: llama-3.2-90b-text-preview has been DECOMMISSIONED
            "llama-3.2-11b-text-preview",
            "llama-3.2-11b-vision-preview",
            "llama-3.2-3b-preview",
            "llama-3.2-1b-preview",
            
            # Llama 3.0 models (legacy but stable)
            "llama3-70b-8192",
            "llama3-8b-8192",
            
            # Mixtral models (excellent for complex tasks)
            "mixtral-8x7b-32768",
            
            # Gemma models (efficient, good for simple tasks)
            "gemma2-9b-it",
            "gemma-7b-it"
        ],
        "openai": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ],
        "anthropic": [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
    }
    
    # Alternative providers to try when primary fails
    PROVIDER_FALLBACKS = {
        "groq": ["openai", "anthropic"],
        "openai": ["anthropic", "groq"],
        "anthropic": ["openai", "groq"]
    }
    
    # Track rate limit hits to avoid repeated failures
    _rate_limit_cache: Dict[str, datetime] = {}
    
    @staticmethod
    def is_rate_limit_error(error_msg: str) -> bool:
        """Check if error is a rate limit error"""
        rate_limit_indicators = [
            "429",
            "rate limit",
            "rate_limit",
            "too many requests",
            "quota exceeded",
            "tokens per day",
            "TPD"
        ]
        error_lower = error_msg.lower()
        return any(indicator in error_lower for indicator in rate_limit_indicators)
    
    @staticmethod
    def extract_wait_time(error_msg: str) -> Optional[int]:
        """Extract wait time from rate limit error message (in seconds)"""
        try:
            # Pattern 1: "try again in 22m46.848s"
            match = re.search(r'try again in (\d+)m(\d+(?:\.\d+)?)?s', error_msg, re.IGNORECASE)
            if match:
                minutes = int(match.group(1))
                seconds = float(match.group(2)) if match.group(2) else 0
                return int(minutes * 60 + seconds)
            
            # Pattern 2: "retry after 120 seconds"
            match = re.search(r'retry after (\d+) seconds?', error_msg, re.IGNORECASE)
            if match:
                return int(match.group(1))
            
            # Pattern 3: "wait 5 minutes"
            match = re.search(r'wait (\d+) minutes?', error_msg, re.IGNORECASE)
            if match:
                return int(match.group(1)) * 60
            
        except Exception as e:
            logger.error(f"Error extracting wait time: {e}")
        
        return None
    
    @staticmethod
    def extract_provider(error_msg: str) -> Optional[str]:
        """Extract the provider from error message"""
        error_lower = error_msg.lower()
        if "groq" in error_lower:
            return "groq"
        elif "openai" in error_lower:
            return "openai"
        elif "anthropic" in error_lower or "claude" in error_lower:
            return "anthropic"
        return None
    
    @staticmethod
    def get_all_available_models(provider: str, exclude_model: Optional[str] = None) -> List[str]:
        """
        Get all models for a provider that are NOT currently rate-limited in cache
        Returns list of available models (excluding the specified model)
        """
        if provider not in RateLimitHandler.FALLBACK_MODELS:
            return []
        
        all_models = RateLimitHandler.FALLBACK_MODELS[provider]
        available_models = []
        
        for model in all_models:
            # Skip the excluded model
            if model == exclude_model:
                continue
            
            # Check if this model is rate-limited
            if not RateLimitHandler.is_cached_rate_limited(provider, model):
                available_models.append(model)
        
        return available_models
    
    @staticmethod
    def get_fallback_model(provider: str, current_model: str) -> Optional[str]:
        """
        Get next fallback model for the same provider that is NOT rate-limited
        Returns None if no fallback available
        """
        if provider not in RateLimitHandler.FALLBACK_MODELS:
            return None
        
        models = RateLimitHandler.FALLBACK_MODELS[provider]
        
        # Find current model index
        try:
            current_index = models.index(current_model)
        except ValueError:
            # Current model not in list, start from beginning
            current_index = -1
        
        # Look for next available model (not rate-limited)
        for i in range(current_index + 1, len(models)):
            candidate_model = models[i]
            if not RateLimitHandler.is_cached_rate_limited(provider, candidate_model):
                return candidate_model
        
        # If no model found after current, check models before current (circular search)
        for i in range(0, current_index):
            candidate_model = models[i]
            if not RateLimitHandler.is_cached_rate_limited(provider, candidate_model):
                return candidate_model
        
        return None
    
    @staticmethod
    def get_alternative_provider(current_provider: str) -> Optional[str]:
        """Get alternative provider to try"""
        if current_provider in RateLimitHandler.PROVIDER_FALLBACKS:
            alternatives = RateLimitHandler.PROVIDER_FALLBACKS[current_provider]
            # Check cache to avoid recently rate-limited providers
            for provider in alternatives:
                cache_key = f"provider_{provider}"
                if cache_key not in RateLimitHandler._rate_limit_cache:
                    return provider
                
                # Check if cooldown has expired
                cooldown_time = RateLimitHandler._rate_limit_cache[cache_key]
                if datetime.now() > cooldown_time:
                    del RateLimitHandler._rate_limit_cache[cache_key]
                    return provider
            
            # If all are rate limited, return first alternative anyway
            return alternatives[0] if alternatives else None
        
        return None
    
    @staticmethod
    def cache_rate_limit(provider: str, model: str, wait_seconds: Optional[int] = None):
        """Cache rate limit information to avoid repeated hits"""
        cache_key = f"{provider}_{model}"
        if wait_seconds:
            cooldown_time = datetime.now() + timedelta(seconds=wait_seconds)
        else:
            # Default 5 minute cooldown
            cooldown_time = datetime.now() + timedelta(minutes=5)
        
        RateLimitHandler._rate_limit_cache[cache_key] = cooldown_time
        logger.info(f"Cached rate limit for {cache_key} until {cooldown_time}")
    
    @staticmethod
    def is_cached_rate_limited(provider: str, model: str) -> bool:
        """Check if a provider/model is known to be rate limited"""
        cache_key = f"{provider}_{model}"
        if cache_key in RateLimitHandler._rate_limit_cache:
            cooldown_time = RateLimitHandler._rate_limit_cache[cache_key]
            if datetime.now() < cooldown_time:
                remaining = (cooldown_time - datetime.now()).total_seconds()
                logger.debug(f"Model {provider}/{model} is cached as rate-limited. {int(remaining)}s remaining.")
                return True
            else:
                # Cooldown expired, remove from cache
                logger.info(f"Rate limit cooldown expired for {provider}/{model}")
                del RateLimitHandler._rate_limit_cache[cache_key]
        return False
    
    @staticmethod
    def clear_expired_cache():
        """Clear all expired entries from the rate limit cache"""
        now = datetime.now()
        expired_keys = [
            key for key, cooldown_time in RateLimitHandler._rate_limit_cache.items()
            if now >= cooldown_time
        ]
        for key in expired_keys:
            del RateLimitHandler._rate_limit_cache[key]
            logger.info(f"Cleared expired cache entry: {key}")
        
        return len(expired_keys)
    
    @staticmethod
    def get_cache_status() -> Dict[str, Any]:
        """Get current status of rate limit cache"""
        now = datetime.now()
        status = {
            "total_cached": len(RateLimitHandler._rate_limit_cache),
            "by_provider": {},
            "entries": []
        }
        
        for key, cooldown_time in RateLimitHandler._rate_limit_cache.items():
            remaining_seconds = (cooldown_time - now).total_seconds()
            if remaining_seconds > 0:
                provider_model = key.replace("provider_", "")
                parts = provider_model.split("_", 1)
                provider = parts[0] if parts else "unknown"
                
                status["entries"].append({
                    "key": key,
                    "cooldown_until": cooldown_time.isoformat(),
                    "remaining_seconds": int(remaining_seconds),
                    "provider": provider
                })
                
                if provider not in status["by_provider"]:
                    status["by_provider"][provider] = 0
                status["by_provider"][provider] += 1
        
        return status
    
    @staticmethod
    def create_user_friendly_message(error_msg: str, provider: str, model: str) -> str:
        """Create a user-friendly error message with suggestions"""
        wait_time = RateLimitHandler.extract_wait_time(error_msg)
        
        message_parts = [
            f"⚠️ Rate limit reached for {provider.upper()} ({model})."
        ]
        
        if wait_time:
            if wait_time < 60:
                time_str = f"{wait_time} seconds"
            elif wait_time < 3600:
                time_str = f"{wait_time // 60} minutes"
            else:
                time_str = f"{wait_time // 3600} hours"
            message_parts.append(f"The provider requests waiting {time_str}.")
        
        message_parts.append("✅ Automatically trying alternative model/provider...")
        
        return " ".join(message_parts)
    
    @staticmethod
    def get_fallback_strategy(provider: str, model: str, error_msg: str) -> Dict[str, Any]:
        """
        Get comprehensive fallback strategy
        Returns dict with fallback options and recommendations
        """
        strategy = {
            "original_provider": provider,
            "original_model": model,
            "wait_time_seconds": RateLimitHandler.extract_wait_time(error_msg),
            "fallback_model": None,
            "alternative_provider": None,
            "user_message": "",
            "should_retry": True
        }
        
        # Try same provider with different model first
        fallback_model = RateLimitHandler.get_fallback_model(provider, model)
        if fallback_model and not RateLimitHandler.is_cached_rate_limited(provider, fallback_model):
            strategy["fallback_model"] = fallback_model
            strategy["user_message"] = f"Switching to {provider.upper()} {fallback_model}..."
            return strategy
        
        # Try alternative provider
        alt_provider = RateLimitHandler.get_alternative_provider(provider)
        if alt_provider:
            alt_models = RateLimitHandler.FALLBACK_MODELS.get(alt_provider, [])
            if alt_models:
                strategy["alternative_provider"] = alt_provider
                strategy["fallback_model"] = alt_models[0]  # Use first model of alternative provider
                strategy["user_message"] = f"Switching to {alt_provider.upper()} {alt_models[0]}..."
                return strategy
        
        # No fallback available
        strategy["should_retry"] = False
        wait_str = f"Please try again in {strategy['wait_time_seconds'] // 60} minutes" if strategy['wait_time_seconds'] else "Please try again later"
        strategy["user_message"] = f"All alternative providers are rate limited. {wait_str}."
        
        return strategy


class RateLimitError(Exception):
    """Custom exception for rate limit errors"""
    def __init__(self, message: str, provider: str, model: str, wait_time: Optional[int] = None):
        super().__init__(message)
        self.provider = provider
        self.model = model
        self.wait_time = wait_time

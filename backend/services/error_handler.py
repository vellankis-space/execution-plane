"""
Enhanced Error Handling Service
Provides retry mechanisms, error categorization, and better error messages
"""
import asyncio
import logging
from typing import Dict, Any, Optional, Callable, Type
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Error categories for better error handling"""
    API_KEY_ERROR = "api_key_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    VALIDATION_ERROR = "validation_error"
    TOOL_ERROR = "tool_error"
    LLM_ERROR = "llm_error"
    WORKFLOW_ERROR = "workflow_error"
    UNKNOWN_ERROR = "unknown_error"


class RetryPolicy:
    """Retry policy configuration"""
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        retryable_errors: Optional[list[ErrorCategory]] = None
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retryable_errors = retryable_errors or [
            ErrorCategory.RATE_LIMIT_ERROR,
            ErrorCategory.NETWORK_ERROR,
            ErrorCategory.TIMEOUT_ERROR,
            ErrorCategory.TOOL_ERROR,
        ]


class ErrorHandler:
    """Enhanced error handler with categorization and retry logic"""
    
    @staticmethod
    def categorize_error(error: Exception) -> tuple[ErrorCategory, str]:
        """
        Categorize an error and return a user-friendly message
        
        Returns:
            Tuple of (ErrorCategory, user_friendly_message)
        """
        error_msg = str(error).lower()
        error_type = type(error).__name__
        
        # API Key errors
        if any(keyword in error_msg for keyword in ["api key", "401", "unauthorized", "authentication"]):
            return (
                ErrorCategory.API_KEY_ERROR,
                "Invalid API key. Please check your API key configuration."
            )
        
        # Rate limit errors
        if any(keyword in error_msg for keyword in ["429", "rate limit", "too many requests", "quota"]):
            return (
                ErrorCategory.RATE_LIMIT_ERROR,
                "Rate limit exceeded. Please try again later or upgrade your plan."
            )
        
        # Network errors
        if any(keyword in error_msg for keyword in ["connection", "network", "timeout", "unreachable", "dns"]):
            if "timeout" in error_msg:
                return (
                    ErrorCategory.TIMEOUT_ERROR,
                    "Request timed out. The service may be slow or unreachable. Please try again."
                )
            return (
                ErrorCategory.NETWORK_ERROR,
                "Network error occurred. Please check your internet connection and try again."
            )
        
        # Validation errors
        if any(keyword in error_msg for keyword in ["validation", "invalid", "missing", "required"]):
            return (
                ErrorCategory.VALIDATION_ERROR,
                f"Validation error: {str(error)}"
            )
        
        # Tool errors
        if any(keyword in error_msg for keyword in ["tool", "function", "tool_use_failed"]):
            return (
                ErrorCategory.TOOL_ERROR,
                "Tool execution failed. This may be due to rate limiting, network issues, or missing API keys."
            )
        
        # LLM errors
        if any(keyword in error_msg for keyword in ["llm", "model", "openai", "anthropic", "groq"]):
            return (
                ErrorCategory.LLM_ERROR,
                f"LLM service error: {str(error)}"
            )
        
        # Workflow errors
        if any(keyword in error_msg for keyword in ["workflow", "step", "dependency", "circular"]):
            return (
                ErrorCategory.WORKFLOW_ERROR,
                f"Workflow error: {str(error)}"
            )
        
        # Unknown error
        return (
            ErrorCategory.UNKNOWN_ERROR,
            f"An unexpected error occurred: {str(error)}"
        )
    
    @staticmethod
    def is_retryable(category: ErrorCategory, retry_policy: RetryPolicy) -> bool:
        """Check if an error category is retryable based on the retry policy"""
        return category in retry_policy.retryable_errors
    
    @staticmethod
    async def retry_with_backoff(
        func: Callable,
        retry_policy: RetryPolicy,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a function with retry logic and exponential backoff
        
        Args:
            func: Async function to execute
            retry_policy: Retry policy configuration
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        
        Returns:
            Result of the function call
        
        Raises:
            Exception: The last exception if all retries fail
        """
        last_exception = None
        delay = retry_policy.initial_delay
        
        for attempt in range(retry_policy.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                category, message = ErrorHandler.categorize_error(e)
                
                # Check if error is retryable
                if not ErrorHandler.is_retryable(category, retry_policy):
                    logger.warning(
                        f"Non-retryable error ({category.value}): {message}. Not retrying."
                    )
                    raise e
                
                # Check if we have retries left
                if attempt < retry_policy.max_retries:
                    logger.warning(
                        f"Attempt {attempt + 1}/{retry_policy.max_retries + 1} failed "
                        f"({category.value}): {message}. Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                    delay = min(delay * retry_policy.exponential_base, retry_policy.max_delay)
                else:
                    logger.error(
                        f"All {retry_policy.max_retries + 1} attempts failed. "
                        f"Last error ({category.value}): {message}"
                    )
        
        # All retries exhausted
        category, message = ErrorHandler.categorize_error(last_exception)
        raise Exception(f"{message} (Failed after {retry_policy.max_retries + 1} attempts)")
    
    @staticmethod
    def get_error_details(error: Exception) -> Dict[str, Any]:
        """
        Get detailed error information for logging and debugging
        
        Returns:
            Dictionary with error details
        """
        category, message = ErrorHandler.categorize_error(error)
        
        return {
            "category": category.value,
            "message": message,
            "error_type": type(error).__name__,
            "error_str": str(error),
            "timestamp": datetime.utcnow().isoformat(),
        }


# Default retry policies for different scenarios
DEFAULT_RETRY_POLICY = RetryPolicy(
    max_retries=3,
    initial_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0
)

AGGRESSIVE_RETRY_POLICY = RetryPolicy(
    max_retries=5,
    initial_delay=0.5,
    max_delay=120.0,
    exponential_base=2.0
)

CONSERVATIVE_RETRY_POLICY = RetryPolicy(
    max_retries=1,
    initial_delay=2.0,
    max_delay=30.0,
    exponential_base=1.5
)

NO_RETRY_POLICY = RetryPolicy(
    max_retries=0,
    initial_delay=0.0,
    max_delay=0.0,
    exponential_base=1.0,
    retryable_errors=[]
)


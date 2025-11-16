# Intelligent Rate Limit Handling System

## Overview
Implemented a comprehensive rate limit handling system that automatically detects rate limit errors from LLM providers and intelligently falls back to alternative models or providers without user intervention.

## Problem Statement

**Original Issue:**
```
Error code: 429 - Rate limit reached for model `llama-3.3-70b-versatile` 
in organization `org_01jw6q299dfqv93hk50p3yd6jj` service tier `on_demand` 
on tokens per day (TPD): Limit 100000, Used 99901, Requested 1681. 
Please try again in 22m46.848s.
```

**Impact:**
- ❌ Agent execution fails completely
- ❌ Poor user experience
- ❌ No automatic recovery
- ❌ User must manually retry or change settings

## Solution: Automatic Fallback System

### Key Features

1. **✅ Automatic Detection**: Identifies rate limit errors (429, quota exceeded, etc.)
2. **✅ Smart Fallback**: Tries alternative models/providers automatically
3. **✅ User-Friendly Messages**: Clear communication about what's happening
4. **✅ Rate Limit Caching**: Avoids repeatedly hitting rate-limited endpoints
5. **✅ Multiple Retry Strategies**: 3 levels of fallback

## Architecture

### Components Created

#### 1. **RateLimitHandler Service** (`rate_limit_handler.py`)

**Purpose**: Central service for rate limit detection and fallback strategy

**Key Methods:**
- `is_rate_limit_error()`: Detects rate limit errors
- `extract_wait_time()`: Parses wait time from error messages  
- `get_fallback_model()`: Returns next model to try (same provider)
- `get_alternative_provider()`: Returns different provider to try
- `get_fallback_strategy()`: Complete fallback recommendation
- `cache_rate_limit()`: Remember rate-limited endpoints
- `create_user_friendly_message()`: Generate helpful error messages

#### 2. **Modified Agent Service** (`agent_service.py`)

**Changes:**
- Added retry loop (max 3 attempts)
- Integrated RateLimitHandler
- Automatic model/provider switching
- Improved error messages

## Fallback Strategy

### Level 1: Same Provider, Different Model

```
Groq llama-3.3-70b-versatile (RATE LIMITED)
    ↓
Groq llama-3.1-70b-versatile
    ↓
Groq llama-3.1-8b-instant
    ↓
Groq mixtral-8x7b-32768
    ↓
Groq gemma2-9b-it
```

### Level 2: Alternative Provider

```
Groq (All models rate limited)
    ↓
Try OpenAI (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
    ↓
Try Anthropic (claude-3-5-sonnet, claude-3-5-haiku)
```

### Level 3: Inform User

```
All providers rate limited
    ↓
Return friendly error message with wait time
```

## Fallback Model Configurations

### Groq Models (Priority Order)
1. `llama-3.3-70b-versatile` (Primary)
2. `llama-3.1-70b-versatile` (Fallback 1)
3. `llama-3.1-8b-instant` (Fallback 2 - Faster)
4. `mixtral-8x7b-32768` (Fallback 3)
5. `gemma2-9b-it` (Fallback 4 - Smallest)

### OpenAI Models (Priority Order)
1. `gpt-4o` (Primary)
2. `gpt-4o-mini` (Fallback 1 - Cost-effective)
3. `gpt-4-turbo` (Fallback 2)
4. `gpt-3.5-turbo` (Fallback 3 - Fastest)

### Anthropic Models (Priority Order)
1. `claude-3-5-sonnet-20241022` (Primary)
2. `claude-3-5-haiku-20241022` (Fallback 1 - Faster)
3. `claude-3-haiku-20240307` (Fallback 2 - Legacy)

## Provider Fallback Chain

### From Groq
```
Groq → OpenAI → Anthropic
```

### From OpenAI
```
OpenAI → Anthropic → Groq
```

### From Anthropic
```
Anthropic → OpenAI → Groq
```

## Execution Flow

### Standard Execution (No Rate Limit)
```
┌─────────────────────────────────────┐
│ 1. Agent executes with primary      │
│    model (e.g., Groq llama-3.3-70b) │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 2. Success! Return response         │
└─────────────────────────────────────┘
```

### Rate Limit Hit - Successful Fallback
```
┌─────────────────────────────────────┐
│ 1. Execute with Groq llama-3.3-70b  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 2. ❌ 429 Rate Limit Error           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 3. Detect rate limit + extract info │
│    - Provider: Groq                 │
│    - Model: llama-3.3-70b           │
│    - Wait time: 22m46s              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 4. Get fallback strategy            │
│    → Try llama-3.1-70b-versatile    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 5. Cache rate limit (22m46s)        │
│    groq_llama-3.3-70b → cooldown    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 6. Print: "🔄 Switching to Groq     │
│    llama-3.1-70b-versatile..."      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 7. Retry with new model             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 8. ✅ Success! Return response       │
└─────────────────────────────────────┘
```

### Rate Limit - Provider Switch
```
┌─────────────────────────────────────┐
│ 1. Execute with Groq (rate limited) │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 2. All Groq models cached as        │
│    rate limited                     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 3. Get alternative provider         │
│    → OpenAI                         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 4. Print: "🔄 Switching to OpenAI   │
│    gpt-4o..."                       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 5. Retry with OpenAI                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 6. ✅ Success! Return response       │
└─────────────────────────────────────┘
```

## Rate Limit Cache

### Purpose
Prevents repeatedly hitting rate-limited endpoints by caching failures.

### Cache Structure
```python
{
    "groq_llama-3.3-70b-versatile": datetime(2024, 11, 14, 15, 52, 46),
    "openai_gpt-4o": datetime(2024, 11, 14, 15, 30, 0),
    "provider_groq": datetime(2024, 11, 14, 15, 45, 0)
}
```

### Cache Behavior
- **Key Format**: `{provider}_{model}` or `provider_{provider}`
- **Cooldown**: Extracted wait time or default 5 minutes
- **Auto-Cleanup**: Expired entries removed on next check
- **Skip Logic**: Cached entries skipped during fallback selection

## Error Messages

### Before (Original)
```
Error communicating with the agent: An unexpected error occurred 
while processing your request: Error code: 429 - {'error': 
{'message': 'Rate limit reached for model `llama-3.3-70b-versatile` 
in organization `org_01jw6q299dfqv93hk50p3yd6jj` service tier 
`on_demand` on tokens per day (TPD): Limit 100000, Used 99901, 
Requested 1681. Please try again in 22m46.848s. Need more tokens? 
Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 
'type': 'tokens', 'code': 'rate_limit_exceeded'}}
```

### After (User-Friendly)
```
🔄 Switching to GROQ llama-3.1-70b-versatile...
```

or if all fallbacks exhausted:
```
⚠️ Rate limit reached for GROQ (llama-3.3-70b-versatile). 
The provider requests waiting 22 minutes. 
✅ Automatically trying alternative model/provider...
```

or if no alternatives:
```
⚠️ Rate limit reached for GROQ (llama-3.3-70b-versatile). 
All alternative providers are rate limited. 
Please try again in 22 minutes.
```

## Code Examples

### Using the Rate Limit Handler

```python
from services.rate_limit_handler import RateLimitHandler

# Check if an error is rate-related
if RateLimitHandler.is_rate_limit_error(error_msg):
    # Get wait time
    wait_seconds = RateLimitHandler.extract_wait_time(error_msg)
    print(f"Need to wait {wait_seconds} seconds")
    
    # Get fallback strategy
    strategy = RateLimitHandler.get_fallback_strategy(
        provider="groq",
        model="llama-3.3-70b-versatile",
        error_msg=error_msg
    )
    
    if strategy['should_retry']:
        # Cache the rate limit
        RateLimitHandler.cache_rate_limit(
            "groq",
            "llama-3.3-70b-versatile",
            wait_seconds
        )
        
        # Use fallback
        new_provider = strategy['alternative_provider'] or "groq"
        new_model = strategy['fallback_model']
        print(strategy['user_message'])
```

### Agent Execution with Auto-Fallback

```python
# In agent_service.py
max_retries = 3
retry_count = 0

while retry_count < max_retries:
    try:
        return await self._execute_agent_with_fallback(...)
    except Exception as e:
        if RateLimitHandler.is_rate_limit_error(str(e)):
            retry_count += 1
            strategy = RateLimitHandler.get_fallback_strategy(...)
            
            if strategy['should_retry'] and retry_count < max_retries:
                # Update agent config
                agent.llm_provider = strategy['alternative_provider']
                agent.llm_model = strategy['fallback_model']
                continue
            else:
                raise ValueError(f"No more fallbacks available")
        else:
            raise  # Not a rate limit error
```

## Configuration

### Adding New Models

To add new fallback models, update `rate_limit_handler.py`:

```python
FALLBACK_MODELS = {
    "groq": [
        "llama-3.3-70b-versatile",
        "your-new-model-here",  # Add here
        "llama-3.1-70b-versatile",
        # ...
    ]
}
```

### Adding New Providers

```python
PROVIDER_FALLBACKS = {
    "groq": ["openai", "anthropic"],
    "new_provider": ["groq", "openai"],  # Add here
}
```

## Benefits

### For Users
✅ **Seamless Experience**: No manual intervention needed
✅ **Clear Communication**: Know what's happening behind the scenes
✅ **Faster Resolution**: Automatic fallback vs. manual retry
✅ **Cost Optimization**: Uses cheaper models when primary is unavailable

### For System
✅ **Higher Availability**: Multiple fallback options
✅ **Better Resilience**: Handles provider outages
✅ **Smart Resource Usage**: Avoids repeatedly hitting rate limits
✅ **Logging & Monitoring**: Clear visibility into fallback behavior

## Testing

### Test Scenarios

#### 1. Single Model Fallback
```python
# Simulate Groq rate limit
# Expected: Switch to llama-3.1-70b-versatile
```

#### 2. Provider Fallback
```python
# Simulate all Groq models rate limited
# Expected: Switch to OpenAI gpt-4o
```

#### 3. Cache Effectiveness
```python
# Hit rate limit, cache it
# Try again immediately
# Expected: Skip cached model, go to next fallback
```

#### 4. Wait Time Extraction
```python
error = "try again in 22m46.848s"
wait_time = RateLimitHandler.extract_wait_time(error)
# Expected: 1366 seconds
```

#### 5. All Providers Exhausted
```python
# Simulate all providers rate limited
# Expected: User-friendly message with wait time
```

## Monitoring

### Log Messages to Watch

**Success Fallback:**
```
🔄 Switching to GROQ llama-3.1-70b-versatile...
Switching to groq with model llama-3.1-70b-versatile
```

**Provider Switch:**
```
🔄 Switching to OPENAI gpt-4o...
Switching to openai with model gpt-4o
```

**Cache Hit:**
```
Cached rate limit for groq_llama-3.3-70b-versatile until 2024-11-14 15:52:46
```

**Exhausted Retries:**
```
Failed to execute agent after 3 attempts with different models/providers.
```

## Performance Impact

### Minimal Overhead
- **Detection**: < 1ms (string pattern matching)
- **Strategy Calculation**: < 1ms (dictionary lookups)
- **Cache Operations**: < 1ms (in-memory)

### Improved UX
- **Before**: User waits 22+ minutes, manually retries
- **After**: Automatic fallback in < 2 seconds

## Error Handling

### Non-Rate Limit Errors
- ❌ 401 Unauthorized → Immediate failure (Invalid API key)
- ❌ 403 Forbidden → Immediate failure (Permission issue)
- ❌ Tool execution failures → Immediate failure
- ❌ Other errors → Immediate failure

### Rate Limit Errors
- ✅ 429 Too Many Requests → Retry with fallback
- ✅ "rate limit" in message → Retry with fallback
- ✅ "quota exceeded" → Retry with fallback

## Future Enhancements

### Potential Improvements
- [ ] **Adaptive Fallback**: Learn which models work best for specific queries
- [ ] **Cost-Aware Selection**: Prefer cheaper models when appropriate
- [ ] **Load Balancing**: Distribute across multiple API keys
- [ ] **Predictive Caching**: Anticipate rate limits based on usage patterns
- [ ] **User Preferences**: Let users configure fallback order
- [ ] **Historical Analytics**: Track fallback success rates
- [ ] **Dynamic Timeout**: Adjust based on provider response times

## Troubleshooting

### Issue: Fallback Not Triggering

**Diagnosis:**
- Check error message format
- Verify `is_rate_limit_error()` detection
- Review log output

**Solution:**
- Add error pattern to detection regex
- Update `rate_limit_indicators` list

### Issue: Wrong Provider Selected

**Diagnosis:**
- Check `PROVIDER_FALLBACKS` configuration
- Verify cache is not interfering

**Solution:**
- Clear rate limit cache
- Update provider fallback order

### Issue: Still Getting Rate Limit Errors

**Diagnosis:**
- All fallbacks may be exhausted
- Check cache expiry times
- Verify multiple API keys if available

**Solution:**
- Wait for cooldown period
- Add more fallback models
- Configure additional providers

## Summary

The intelligent rate limit handling system provides:

✅ **Automatic Detection** of rate limit errors
✅ **Smart Fallback** to alternative models/providers
✅ **User-Friendly Messages** explaining what's happening
✅ **Rate Limit Caching** to avoid repeated failures
✅ **3-Level Fallback Strategy** for maximum resilience
✅ **Zero User Intervention** required
✅ **Clear Logging** for monitoring
✅ **Minimal Performance Impact**

**Result**: Users experience seamless agent execution even when primary models hit rate limits! 🎉

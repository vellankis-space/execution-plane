# LiteLLM & Langfuse Integration Guide

## Overview

This platform now supports **LiteLLM** and **Langfuse** for enhanced LLM management, observability, and cost tracking.

## Benefits

### LiteLLM
- ✅ **Unified Interface**: Single API for 100+ LLM providers
- ✅ **Automatic Retries**: Built-in retry logic with exponential backoff
- ✅ **Fallbacks**: Automatic failover between providers/models
- ✅ **Rate Limiting**: Prevent API quota exhaustion
- ✅ **Caching**: Reduce costs with response caching
- ✅ **Cost Tracking**: Built-in usage and cost tracking
- ✅ **Streaming**: Better streaming support

### Langfuse
- ✅ **LLM Observability**: Comprehensive tracing and logging
- ✅ **Cost Analytics**: Detailed cost breakdowns per model/provider
- ✅ **Prompt Management**: Version and manage prompts
- ✅ **Performance Monitoring**: Latency, token usage, success rates
- ✅ **Analytics Dashboard**: Built-in analytics UI
- ✅ **Token Usage Tracking**: Accurate token counting
- ✅ **Error Tracking**: Detailed error analysis

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install litellm langfuse langchain-community
```

### 2. Configure Environment Variables

Add to your `.env` file:

```env
# LiteLLM Configuration (Optional - enabled by default)
USE_LITELLM=true

# Langfuse Configuration (Optional but recommended)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com  # or your self-hosted instance
```

### 3. Get Langfuse Keys

1. Sign up at https://cloud.langfuse.com (or deploy self-hosted)
2. Create a project
3. Get your public and secret keys from project settings
4. Add them to `.env`

### 4. Enable LiteLLM Features

LiteLLM is enabled by default. To disable:

```env
USE_LITELLM=false
```

## How It Works

### Current Implementation

1. **LLM Initialization**: 
   - Uses `LLMService` which supports both LiteLLM and direct provider initialization
   - Falls back to direct initialization if LiteLLM fails
   - Automatically integrates Langfuse callback when configured

2. **Cost Tracking**:
   - Enhanced with Langfuse token counts when available
   - Falls back to estimation if Langfuse not configured
   - Integrates with existing cost tracking system

3. **Observability**:
   - All LLM calls are automatically traced in Langfuse
   - View traces in Langfuse dashboard
   - Get detailed analytics and cost breakdowns

## Usage Examples

### With LiteLLM (Default)

```python
# Automatically uses LiteLLM if enabled
llm = llm_service.initialize_llm(
    provider="openai",
    model="gpt-4",
    temperature=0.7,
    use_litellm=True  # Default
)
```

### With Langfuse Tracing

```python
# Traces are automatically created when Langfuse is configured
trace = langfuse_integration.trace_agent_execution(
    agent_id="agent-123",
    user_id="user-456",
    metadata={"custom": "data"}
)
```

## Features Enabled

### LiteLLM Features

1. **Provider Fallbacks**
   ```python
   # Automatically falls back if primary provider fails
   # Configure in LiteLLM settings
   ```

2. **Caching**
   ```python
   # Enable caching to reduce costs
   # Configure in LiteLLM settings
   ```

3. **Rate Limiting**
   ```python
   # Automatic rate limiting per provider
   # Configure in LiteLLM settings
   ```

### Langfuse Features

1. **Trace Viewing**
   - View all LLM calls in Langfuse dashboard
   - See token usage, latency, costs
   - Debug failed calls

2. **Cost Analytics**
   - Detailed cost breakdowns
   - Per-model, per-user, per-workflow costs
   - Budget tracking

3. **Prompt Management**
   - Version prompts
   - A/B testing
   - Prompt performance tracking

## Integration Points

### 1. Agent Execution
- All agent LLM calls are traced in Langfuse
- Cost tracking uses Langfuse token counts when available
- LiteLLM provides unified interface

### 2. Workflow Execution
- Workflow traces include all agent calls
- Cost aggregation per workflow
- Performance monitoring

### 3. Cost Tracking
- Enhanced with Langfuse data
- More accurate token counts
- Better cost calculations

## Configuration Options

### LiteLLM Configuration

Create `litellm_config.yaml` (optional):

```yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY
  
  - model_name: claude-3-opus
    litellm_params:
      model: anthropic/claude-3-opus-20240229
      api_key: os.environ/ANTHROPIC_API_KEY

general_settings:
  master_key: your-master-key
  database_url: postgresql://...
```

### Langfuse Configuration

Set environment variables:
- `LANGFUSE_PUBLIC_KEY`: Your Langfuse public key
- `LANGFUSE_SECRET_KEY`: Your Langfuse secret key
- `LANGFUSE_HOST`: Langfuse server URL (default: cloud)

## Benefits Over Current Implementation

### Before (Direct Providers)
- ❌ Manual provider initialization
- ❌ No automatic retries
- ❌ Estimated token counts
- ❌ Basic cost tracking
- ❌ Limited observability

### After (LiteLLM + Langfuse)
- ✅ Unified provider interface
- ✅ Automatic retries and fallbacks
- ✅ Accurate token counts
- ✅ Enhanced cost tracking
- ✅ Full observability with traces
- ✅ Prompt management
- ✅ Better error handling

## Migration Path

1. **Install dependencies**: `pip install litellm langfuse`
2. **Configure Langfuse**: Add keys to `.env`
3. **Enable LiteLLM**: Set `USE_LITELLM=true` (default)
4. **Test**: Run agents/workflows and check Langfuse dashboard
5. **Monitor**: Use Langfuse for cost and performance analytics

## Next Steps

1. **Set up Langfuse account** (cloud or self-hosted)
2. **Configure environment variables**
3. **Test with a simple agent execution**
4. **View traces in Langfuse dashboard**
5. **Set up cost budgets in Langfuse**
6. **Use Langfuse prompt management**

## Additional Resources

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Langfuse Documentation](https://langfuse.com/docs)
- [Langfuse Dashboard](https://cloud.langfuse.com)

---

**The integration is backward compatible - existing code continues to work, with enhanced features when LiteLLM/Langfuse are configured!**


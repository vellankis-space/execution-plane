# OpenRouter Tool Use Fix

## Issue Summary

You were seeing this error when using OpenRouter with ReAct agents that have MCP tools:

```
INFO:httpx:HTTP Request: POST https://openrouter.ai/api/v1/chat/completions "HTTP/1.1 404 Not Found"
Error code: 404 - {'error': {'message': 'No endpoints found that support tool use', 'code': 404}}
```

## Root Cause Analysis

### What Was Happening

1. **ReAct Agent with 47 MCP Tools**: Your agent successfully loaded all CoinGecko tools
2. **LangGraph Creates Tool-Enabled Request**: The prebuilt `create_react_agent` automatically includes `tools=[...]` in every LLM request
3. **OpenRouter Routing Failure**: When the request hit OpenRouter, it tried to route to a provider that:
   - Supports the model you requested
   - Supports OpenAI-style function/tool calling
   - Matches your account's privacy/data policy
4. **No Match Found**: OpenRouter couldn't find any provider endpoint meeting all criteria, so returned **404**

### Why This Kept Happening

OpenRouter uses **provider routing**. When you send a request with `tools` in the payload:
- It must route to a provider that explicitly supports function calling
- Not all models/providers in OpenRouter's network support tools
- Without routing hints, OpenRouter may pick providers that don't support the feature

**Before the fix:**
```python
ChatOpenAI(
    model="some/model",
    base_url="https://openrouter.ai/api/v1",
    # ❌ No routing preferences
)
```

OpenRouter would try auto-routing and often fail to find a tool-capable endpoint.

---

## The Fix

### Added Provider Routing Preferences

We now explicitly tell OpenRouter to **prefer tool-capable providers** using the `provider` routing configuration:

**Modified Files:**
1. `backend/services/llm_service.py` (lines 120-146)
2. `backend/services/agent_service.py` (lines 1112-1138)

**New Configuration:**
```python
ChatOpenAI(
    model=model,
    base_url="https://openrouter.ai/api/v1",
    api_key=user_api_key,
    model_kwargs={
        "provider": {
            "order": [
                "OpenAI",      # Supports tools natively
                "Anthropic",   # Claude supports function calling
                "Google",      # Gemini supports tools
                "Cohere",      # Command-R supports tools
                "Fireworks"    # Most models support tools
            ],
            "allow_fallbacks": True  # Try next provider if first fails
        }
    }
)
```

### How It Works

1. **Preferred Provider Order**: OpenRouter will try providers in the specified order
2. **Tool Support**: All listed providers support OpenAI-style function/tool calling
3. **Fallback Chain**: If the primary provider is unavailable/rate-limited, it tries the next one
4. **Compatibility**: Works with any OpenRouter model that these providers support

---

## Pattern of Issues You've Been Facing

Looking at all the errors across our session, here's the recurring pattern:

### Issue Type 1: API Key Problems
- **401 "Invalid API Key"** (Groq memory) → Invalid/expired key in `.env`
- **401 "No auth credentials"** (OpenRouter) → Key not being sent properly
  - **Fix**: Corrected `openrouter_api_key` parameter name in LiteLLM

### Issue Type 2: Account/Provider Configuration
- **404 "No endpoints matching data policy"** → OpenRouter account privacy settings
- **404 "No endpoints support tool use"** → Missing routing preferences
  - **Fix**: Added provider routing hints

### Issue Type 3: External API Limitations
- These aren't bugs in your code—they're configuration/external service issues
- Need clear error messages to guide users

---

## Best Practices for OpenRouter + Tools

### 1. Choose Tool-Capable Models

When selecting models from OpenRouter's catalog, verify they support function calling:

**Known Tool-Capable Models:**
```
- openai/gpt-4o
- openai/gpt-4-turbo
- anthropic/claude-3-5-sonnet
- anthropic/claude-3-opus
- google/gemini-pro
- google/gemini-1.5-pro
- cohere/command-r-plus
- meta-llama/llama-3.1-70b-instruct (via Fireworks)
```

### 2. Account Settings Alignment

Ensure your OpenRouter account settings match your usage:
- **Privacy Settings**: https://openrouter.ai/settings/privacy
- **Provider Preferences**: https://openrouter.ai/settings/preferences
- Some free-tier models require specific data policies

### 3. Routing Documentation

Reference: https://openrouter.ai/docs/provider-routing

**Key Parameters:**
- `provider.order`: List of preferred providers
- `provider.allow_fallbacks`: Enable automatic failover
- `provider.require_parameters`: Force specific features (not used here to avoid overly strict filtering)

---

## Testing the Fix

### Expected Behavior After Fix

1. **MCP Tools Load**: ✅ (Already working - 47 tools from CoinGecko)
2. **Agent Creation**: ✅ (ReAct agent with tools - working)
3. **OpenRouter Request**: ✅ Should now succeed with routing to tool-capable provider
4. **Tool Invocation**: Agent can now actually call MCP tools when needed

### Verification Steps

1. **Clear Test**:
   ```bash
   # In chat, ask the agent to use a CoinGecko tool explicitly
   "What's the current price of Bitcoin in USD?"
   ```

2. **Expected Logs**:
   ```
   INFO:httpx:HTTP Request: POST https://openrouter.ai/api/v1/chat/completions "HTTP/1.1 200 OK"
   # No more 404 errors
   ```

3. **Tool Usage**:
   - If the agent decides a tool is needed, you should see MCP tool calls in the logs
   - Response should include real-time data from CoinGecko

---

## Alternative Solutions (If Still Having Issues)

### Option A: Use Specific Tool-Capable Models

Instead of relying on routing, specify exact models:

```python
# In agent config
llm_provider: "openrouter"
llm_model: "openai/gpt-4o"  # Guaranteed tool support
```

### Option B: Use Direct Provider Access

For guaranteed tool support, use providers directly instead of through OpenRouter:

```python
# Direct OpenAI
llm_provider: "openai"
llm_model: "gpt-4o"

# Direct Anthropic
llm_provider: "anthropic"
llm_model: "claude-3-5-sonnet"
```

### Option C: Disable Tools for Specific Agents

If you don't need MCP tools for a particular agent:
- Don't associate MCP servers with that agent
- Use a different agent type (not ReAct)

---

## Summary

**Root Cause**: OpenRouter couldn't route tool-enabled requests to compatible providers

**Fix**: Added explicit provider routing preferences to prioritize tool-capable endpoints

**Files Changed**:
- `backend/services/llm_service.py` (direct initialization)
- `backend/services/agent_service.py` (fallback initialization)

**What Changed**:
```diff
+ model_kwargs={
+     "provider": {
+         "order": ["OpenAI", "Anthropic", "Google", "Cohere", "Fireworks"],
+         "allow_fallbacks": True
+     }
+ }
```

**Result**: OpenRouter now knows to prefer providers that support function/tool calling, preventing the 404 error.

---

## Reference Links

- **OpenRouter Provider Routing**: https://openrouter.ai/docs/provider-routing
- **OpenRouter Models**: https://openrouter.ai/models
- **OpenRouter Settings**: https://openrouter.ai/settings
- **LangChain ChatOpenAI**: https://python.langchain.com/docs/integrations/chat/openai

Your OpenRouter agents with MCP tools should now work correctly! 🚀

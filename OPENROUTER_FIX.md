# OpenRouter Support Fix

## Issue Identified

**Error:** OpenRouter agents failed with "Unsupported provider: openrouter" and 401 authentication errors.

**Root Cause:**
1. LLMService didn't recognize "openrouter" as a valid provider
2. Fell back to direct initialization which also didn't support OpenRouter
3. Eventually defaulted to OpenAI client with OpenRouter API key
4. Sent requests to `https://api.openai.com` instead of `https://openrouter.ai/api/v1`
5. OpenAI rejected the OpenRouter key format (`sk-or-v1...`)

**Log Evidence:**
```
WARNING:services.agent_service:Error initializing LLM with LLMService: Unsupported provider: openrouter, falling back to direct
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 401 Unauthorized"
Error code: 401 - {'error': {'message': 'Incorrect API key provided: sk-or-v1...'}}
```

---

## Fix Applied

### 1. Added OpenRouter Support to LLMService

**File:** `backend/services/llm_service.py`

#### LiteLLM Path
```python
# Add API key if provided
elif provider.lower() == "openrouter":
    litellm_kwargs["api_key"] = user_api_key
```

#### Direct Initialization Path
```python
elif provider.lower() == "openrouter":
    # OpenRouter uses OpenAI-compatible API with custom base_url
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://execution-plane.local",
            "X-Title": "Execution Plane Agent"
        }
    )
```

#### LiteLLM Model Name Mapping
```python
elif provider_lower == "openrouter":
    return f"openrouter/{model}"
```

---

### 2. Added OpenRouter Support to Fallback Initialization

**File:** `backend/services/agent_service.py`

**Method:** `_initialize_llm_direct` (fallback when LLMService fails)

```python
elif provider == "openrouter" and user_api_key:
    # OpenRouter uses OpenAI-compatible API with custom base_url
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=user_api_key,
        base_url="https://openrouter.ai/api/v1",
        max_tokens=300,
        default_headers={
            "HTTP-Referer": "https://execution-plane.local",
            "X-Title": "Execution Plane Agent"
        }
    )
```

---

## OpenRouter Architecture

OpenRouter uses the **OpenAI-compatible API** specification:

- **Base URL:** `https://openrouter.ai/api/v1`
- **API Key Format:** `sk-or-v1-...`
- **Authentication:** Bearer token in Authorization header
- **Client:** LangChain's `ChatOpenAI` with custom `base_url`
- **Optional Headers:**
  - `HTTP-Referer`: Your site URL (for rankings/credits)
  - `X-Title`: Your app name (displayed to users)

---

## Testing Your OpenRouter Agent

### Prerequisites
1. Get an OpenRouter API key from https://openrouter.ai/keys
2. Create an agent with:
   - Provider: `openrouter`
   - Model: Any OpenRouter model (e.g., `anthropic/claude-sonnet-4-5`, `openai/gpt-4o`)
   - API Key: Your OpenRouter key (`sk-or-v1-...`)

### Expected Behavior
After this fix, you should see:
```
INFO:services.agent_service:Loaded 47 tools from MCP server CoinGecko
INFO:services.agent_service:Created ReAct agent with 47 tools
INFO:httpx:HTTP Request: POST https://openrouter.ai/api/v1/chat/completions "HTTP/1.1 200 OK"
```

No more:
- ❌ "Unsupported provider: openrouter"
- ❌ Requests to `https://api.openai.com`
- ❌ 401 Incorrect API key errors

---

## Available OpenRouter Models

Your system already has OpenRouter models configured in `backend/api/v1/models.py`:

**Fallback Models:**
```python
"openrouter": [
    "anthropic/claude-sonnet-4-5",
    "openai/gpt-4o",
    "google/gemini-2.5-pro",
    "google/gemini-2.5-flash",
    "meta-llama/llama-3.3-70b-instruct",
    "qwen/qwen-2.5-72b-instruct",
    "mistralai/mistral-large"
]
```

You can also fetch the full list dynamically from `https://openrouter.ai/api/v1/models`.

---

## Provider Comparison

| Feature | OpenAI | Anthropic | Groq | **OpenRouter** |
|---------|--------|-----------|------|----------------|
| **Base URL** | api.openai.com | api.anthropic.com | api.groq.com | **openrouter.ai/api/v1** |
| **Key Format** | sk-... | sk-ant-... | gsk_... | **sk-or-v1-...** |
| **API Style** | OpenAI | Anthropic | OpenAI | **OpenAI-compatible** |
| **Client** | ChatOpenAI | ChatAnthropic | ChatGroq | **ChatOpenAI + base_url** |
| **Models** | GPT-4, etc. | Claude, etc. | Llama, Mixtral | **All providers** |

---

## What Changed

### Before (Broken)
```
User selects OpenRouter
↓
LLMService: "Unsupported provider: openrouter"
↓
Falls back to direct initialization
↓
Direct: Also doesn't recognize openrouter
↓
Defaults to OpenAI client
↓
Sends OpenRouter key to api.openai.com
↓
401 Error: Invalid key format
```

### After (Fixed)
```
User selects OpenRouter
↓
LLMService: Recognizes "openrouter"
↓
Initializes ChatOpenAI with:
  - base_url = "https://openrouter.ai/api/v1"
  - api_key = user's sk-or-v1-... key
↓
Requests go to openrouter.ai/api/v1
↓
✅ Success: Agent works with all OpenRouter models
```

---

## Architecture Notes

**Why use `ChatOpenAI` for OpenRouter?**

OpenRouter implements the OpenAI-compatible API specification, so we reuse LangChain's `ChatOpenAI` client with a custom `base_url`. This is the recommended approach and avoids creating a separate OpenRouter client.

**Why the custom headers?**

- `HTTP-Referer`: OpenRouter uses this for crediting your app in rankings
- `X-Title`: Shows your app name in OpenRouter's dashboard

These are optional but recommended by OpenRouter.

---

## Summary

✅ **Fixed:** OpenRouter now fully supported in both LLMService and fallback paths  
✅ **Works with:** All OpenRouter models (Claude, GPT-4, Gemini, Llama, etc.)  
✅ **Uses:** Correct endpoint (`https://openrouter.ai/api/v1`)  
✅ **Accepts:** OpenRouter API keys (`sk-or-v1-...`)  
✅ **Supports:** ReAct agents with MCP tools  
✅ **Backward compatible:** Doesn't break existing providers

Your OpenRouter agent should now work correctly with all 47 CoinGecko MCP tools loaded!

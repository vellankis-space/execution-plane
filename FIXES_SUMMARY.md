# Fixes Summary - Nov 19, 2025

## Issues Identified and Fixed

### 1. ✅ Memory 401 Invalid API Key Error

**Root Cause:**
- The Groq API key in `backend/.env` is invalid/expired
- Memory service uses this key to run `llama-3.1-8b-instant` for memory extraction

**Error:**
```
ERROR:services.memory_service:Error adding memory... 401 - {'error': {'message': 'Invalid API Key'...
```

**Fix Required:**
1. Get a valid Groq API key from https://console.groq.com/keys
2. Update `backend/.env`:
   ```bash
   GROQ_API_KEY=gsk_your_new_valid_key_here
   ```
3. Restart backend from backend directory:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

**Verified:**
- Memory defaults changed to always use `groq/llama-3.1-8b-instant`
- All `add_memory` and `search_memory` calls now explicitly use this model
- Agent chat models are separate from memory model

---

### 2. ✅ ReAct Agent Not Loading MCP Tools

**Root Cause:**
- MCP servers exist in DB as "active" with tools (e.g., CoinGecko with 47 tools)
- But FastMCP manager is an in-memory singleton that loses registrations on backend restart
- When `get_agent_mcp_tools` tried to fetch tools, FastMCP manager had no server registered
- Result: `get_tools()` returned empty list → agent fell back to simple chat mode

**Error Pattern:**
```
INFO:services.agent_service:Loaded 0 tools from MCP server CoinGecko
INFO:services.agent_service:Total MCP tools loaded for agent xxx: 0
INFO:services.agent_service:No tools configured - creating simple chat agent without tool calling
```

**Fix Applied:**
Modified `get_agent_mcp_tools` in `agent_service.py` to:
1. Check if server is registered with FastMCP manager
2. If not registered, re-register from DB automatically
3. Connect to server to discover/cache tools
4. Then fetch tools normally

**Code Change:**
```python
# Before calling get_tools, ensure server is registered
if server.server_id not in fastmcp_manager.servers:
    logger.info(f"Re-registering MCP server {server.name} with FastMCP manager from DB")
    config = MCPServerConfig(...)  # Build from DB record
    await fastmcp_manager.register_server(config)
    await fastmcp_manager.connect_server(server.server_id)

# Now get tools
tools = await fastmcp_manager.get_tools(server.server_id)
```

**Result:**
- ReAct agents will now automatically load MCP tools from connected servers
- Tools persist across backend restarts by auto-reloading from DB
- No manual reconnection needed

---

### 3. ✅ Memory Model Consistency

**Changes Made:**
All memory operations now use dedicated model instead of agent's chat model:

**Before:**
```python
# Memory used whatever model the agent used for chat
memory_service.add_memory(...,
    llm_provider=agent.llm_provider,  # Could be anything
    llm_model=agent.llm_model          # e.g., llama-3.3-70b-versatile
)
```

**After:**
```python
# Memory always uses llama-3.1-8b-instant
memory_service.add_memory(...,
    llm_provider="groq",
    llm_model="llama-3.1-8b-instant"
)
```

**Files Changed:**
- `backend/services/memory_service.py` - Changed defaults
- `backend/services/agent_service.py` - Updated all call sites (2× add_memory, 2× search_memory)

---

### 4. ✅ Agent Groq Key Isolation

**Change:**
Added validation to ensure Groq agents use only user-provided keys, not the system memory key:

```python
# In _create_langgraph_agent
if active_provider.lower() == "groq" and not user_api_key:
    raise ValueError("No API key configured for Groq. Please add an API key to this agent.")
```

**Result:**
- Memory: uses `GROQ_API_KEY` from `.env`
- Agents: require per-agent encrypted key from user
- No accidental sharing of keys between systems

---

## Testing Checklist

After updating Groq API key and restarting backend:

- [ ] Memory no longer shows 401 errors
- [ ] Memory logs show: `Mem0 Memory instance created for groq/llama-3.1-8b-instant`
- [ ] ReAct agents with MCP servers load tools: `Loaded X tools from MCP server Y`
- [ ] Agent creates ReAct graph: `Created ReAct agent with X tools`
- [ ] MCP tools are callable during agent execution
- [ ] Chat works normally with configured model
- [ ] Memory stores interactions properly

---

## Environment Configuration

**Required in `backend/.env`:**
```bash
# For memory extraction only
GROQ_API_KEY=gsk_your_valid_key_here

# Optional features
ENABLE_RATE_LIMIT_FALLBACK=true
```

**Optional (if using Mem0 cloud):**
```bash
MEM0_API_KEY=your_mem0_api_key
```

**Not required (agents use user-provided keys):**
- OPENAI_API_KEY (unless you want system fallback)
- ANTHROPIC_API_KEY (unless you want system fallback)

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│ Agent Chat                                              │
│ - Model: User-selected (e.g., llama-3.3-70b-versatile) │
│ - API Key: User-provided per-agent                     │
│ - Tools: MCP + external tools                          │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Memory Service                                          │
│ - Model: Fixed groq/llama-3.1-8b-instant               │
│ - API Key: System GROQ_API_KEY from .env               │
│ - Purpose: Extract/search user facts                   │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ MCP Tools                                               │
│ - Auto-loaded from DB on agent execution               │
│ - FastMCP manager auto-reconnects if needed            │
│ - Tools bound to ReAct agent                           │
└─────────────────────────────────────────────────────────┘
```

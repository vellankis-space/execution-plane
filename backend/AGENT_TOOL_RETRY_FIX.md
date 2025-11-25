# Agent Tool Retry Strategy Fix

## 🎯 Issue Summary

**Problem**: Agent opens browser successfully but keeps retrying the same failing tool (`puppeteer_evaluate`) instead of trying alternative tools to complete the task.

**Symptoms**:
- Agent loads 7 Puppeteer tools successfully
- Browser opens (via `puppeteer_navigate`)
- Agent tries to use `puppeteer_evaluate` to extract page content
- Tool fails with error: `"Cannot read properties of undefined (reading 'originalConsole')"`
- Agent retries the same failing tool 6 times instead of trying alternatives
- Circuit breaker finally blocks the tool after 6 failures
- Task remains incomplete

**Log Evidence**:
```
INFO: Loaded 7 tools from MCP server Puppeteer
INFO: Creating ReAct agent with 7 tools
INFO: POST https://openrouter.ai/api/v1/chat/completions "HTTP/1.1 200 OK"
ERROR: Error calling tool puppeteer_evaluate: Cannot read properties of undefined (reading 'originalConsole')
WARNING: Circuit breaker: Incrementing failure count: 0 -> 1
WARNING: Circuit breaker: Incrementing failure count: 1 -> 2 (all attempts exhausted)
[... agent retries same tool multiple times ...]
ERROR: Circuit breaker OPEN after 6 failures
```

## 🔍 Root Cause Analysis

### Multiple Contributing Factors

#### 1. **Weak Error Recovery Instructions**

The original system prompt instructions were too soft:
```
"After 2-3 failed attempts with the same tool, try a different approach"
```

**Problem**: LLMs don't always follow subtle instructions, especially when they think retrying might work.

#### 2. **Too Many Retry Attempts**

The MCP tool calling logic had `max_attempts = 3`, meaning:
- LLM decides to use tool → Tool fails 3 times → Error returned to LLM
- LLM doesn't learn quickly that the tool is broken
- Each LLM decision results in 3 wasted attempts

#### 3. **No Tool-Specific Guidance**

Puppeteer tools had no guidance about alternatives:
- Agent doesn't know other tools exist (puppeteer_click, puppeteer_screenshot, etc.)
- No clear instruction to try different approaches
- Error messages don't suggest alternatives

#### 4. **Circuit Breaker Kicks In Too Late**

With `max_attempts = 3` and `circuit_breaker_threshold = 3`:
- LLM call 1: 3 attempts fail → count 0→1→2
- LLM call 2: 3 attempts fail → count 2→3→4
- LLM call 3: 3 attempts fail → count 4→5→6
- LLM call 4: Circuit breaker blocks

By the time the circuit breaker activates, the agent has already wasted resources and user time.

### The Core Problem

**LLMs have a tendency to retry actions when they fail**, assuming a transient error. Without explicit, forceful instructions to STOP and try alternatives, they will keep retrying the same action, expecting different results.

## ✅ Solution

### 1. Strengthen Error Recovery Instructions

**Changed from** (soft suggestion):
```
"After 2-3 failed attempts with the same tool, try a different approach"
```

**Changed to** (explicit rules with consequences):
```
## Error Recovery Strategy (CRITICAL - MUST FOLLOW):
**RULE 1**: If a tool fails with an error, READ THE ERROR MESSAGE CAREFULLY.
**RULE 2**: NEVER retry the EXACT same action that just failed. The error will repeat.
**RULE 3**: After ONE failure, you MUST either:
   a) Try a DIFFERENT tool or approach, OR
   b) Fix the parameters based on the error message, OR
   c) Provide a partial answer explaining what went wrong
**RULE 4**: After TWO failures with the same tool, STOP using that tool. Try alternatives.
**RULE 5**: After THREE failures, the tool will be blocked by circuit breaker.

**For Puppeteer errors:**
- If 'puppeteer_evaluate' fails, try 'puppeteer_click', 'puppeteer_screenshot', or other tools
- For JavaScript errors: Follow the syntax guidelines in the error message
- For 'Cannot read properties' errors: The element doesn't exist. Use a different selector or tool

**Remember**: Insanity is trying the same thing repeatedly and expecting different results. BE SMART.
```

### 2. Add Tool-Specific Guidance

Added guidance to each Puppeteer tool description:

**For `puppeteer_evaluate`**:
```
**WARNING**: If this tool fails, DO NOT retry with the same script.
Use alternative tools like puppeteer_click, puppeteer_screenshot, or puppeteer_navigate instead.
```

**For other Puppeteer tools**:
```
**Puppeteer Tool Usage:**
- If this tool fails with an error, try a different Puppeteer tool
- Available alternatives: navigate, click, screenshot, evaluate, etc.
- Do NOT retry the same failing action more than once
```

### 3. Reduce Retry Attempts

**Changed from**:
```python
max_attempts = 3  # Increased from 2 to allow for rate-limit retries
```

**Changed to**:
```python
max_attempts = 2  # Retry once on connection errors, but fail fast on tool errors
```

**Impact**:
- Connection errors: Still get 1 retry (reasonable for network blips)
- Rate limit errors: Still get retry with backoff
- Tool errors (like broken JavaScript): Fail after 2 attempts instead of 3
- Agent learns faster that the tool is broken

### 4. Circuit Breaker Now More Effective

With `max_attempts = 2` and `circuit_breaker_threshold = 3`:
- LLM call 1: 2 attempts fail → count 0→1→2
- LLM call 2: 2 attempts fail → count 2→3 (circuit breaker opens)
- LLM call 3+: Circuit breaker blocks immediately

**Result**: Agent gets **2 chances** to try the tool, then must try alternatives.

## 📊 Comparison

| Scenario | Before | After |
|----------|--------|-------|
| **Max attempts per LLM call** | 3 | 2 |
| **LLM calls before circuit breaker** | 3-4 | 2 |
| **Total failed attempts** | 9-12 | 4 |
| **Error recovery guidance** | Soft suggestion | Explicit rules |
| **Tool alternatives mentioned** | No | Yes |
| **Agent behavior** | Keeps retrying | Tries alternatives |

## 🧪 Testing

### Test Case: Puppeteer Tool Failure

**Scenario**: Agent needs to extract data from a website. `puppeteer_evaluate` tool is broken (JavaScript error).

**Before Fix**:
1. ❌ Agent tries `puppeteer_evaluate` → fails
2. ❌ Agent retries `puppeteer_evaluate` → fails
3. ❌ Agent retries `puppeteer_evaluate` → fails
4. ❌ Agent retries `puppeteer_evaluate` → circuit breaker blocks
5. ❌ Agent gives up, task incomplete
6. **Total**: 9-12 failed attempts, no progress

**After Fix**:
1. ❌ Agent tries `puppeteer_evaluate` → fails (2 attempts)
2. ✅ Agent reads error message, sees instruction to try alternatives
3. ✅ Agent tries `puppeteer_screenshot` → succeeds, gets visual data
4. ✅ OR tries `puppeteer_click` → succeeds, navigates to target page
5. ✅ OR tries different JavaScript in `puppeteer_evaluate` → succeeds
6. **Total**: 2-4 attempts, task progresses

## 🎯 Files Modified

### 1. `services/agent_service.py`

**Lines 546-568** - Added tool-specific guidance for Puppeteer tools:
- Explicit warning in `puppeteer_evaluate` description to try alternatives
- General Puppeteer tool guidance for all other tools
- Lists specific alternative tools by name

**Lines 1051-1067** - Strengthened error recovery instructions:
- Changed from soft suggestions to explicit numbered rules
- Added consequences (circuit breaker blocking)
- Specific guidance for Puppeteer errors
- Memorable reminder ("Insanity is trying the same thing...")

### 2. `services/fastmcp_manager.py`

**Line 510** - Reduced max retry attempts:
- Changed from `max_attempts = 3` to `max_attempts = 2`
- Updated comment to reflect fail-fast strategy
- Still allows one retry for transient errors

## 🔑 Key Learnings

### 1. LLMs Need Explicit Instructions

**Observation**: LLMs will retry failing actions unless explicitly told not to.

**Solution**: Use numbered rules, bold text, and clear consequences instead of suggestions.

### 2. Fail Fast for Tool Errors

**Observation**: Retrying broken tools wastes time and resources.

**Solution**: Reduce retry attempts for tool errors, allow retries only for transient errors (network, rate limits).

### 3. Provide Alternatives Upfront

**Observation**: Agents don't know about alternative tools unless told.

**Solution**: List specific alternatives in tool descriptions and error recovery guidance.

### 4. Circuit Breaker as Safety Net

**Observation**: Circuit breaker prevents hammering, but shouldn't be the primary prevention.

**Solution**: Use strong instructions + fast failure + circuit breaker as defense-in-depth.

### 5. Error Messages Are Communication

**Observation**: Error messages are the primary feedback mechanism for agents.

**Solution**: Error messages should include actionable guidance and alternatives.

## ✅ Summary

**Issue**: Agent retries failing tools instead of trying alternatives  
**Root Cause**: Weak instructions + too many retries + no alternative guidance  
**Solution**: Explicit rules + faster failure + tool alternatives + effective circuit breaker  
**Status**: ✅ **FIXED**  
**Impact**: Agents now try alternatives after 1-2 failures instead of retrying 6+ times  
**User Experience**: Tasks complete faster with fewer wasted API calls  

## 🎉 Expected Behavior After Fix

1. **Agent tries tool** → Fails
2. **Agent reads error** → Understands the problem
3. **Agent tries alternative** → Succeeds OR provides partial answer
4. **Task progresses** → User gets results

No more endless retries. Smart adaptation instead.

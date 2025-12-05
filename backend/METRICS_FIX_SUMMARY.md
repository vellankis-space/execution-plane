# Metrics Fix - Complete Solution

## 🔍 ROOT CAUSE IDENTIFIED

The verification showed **430 new spans** were created during your workflow execution, but:
- ❌ **0 spans had `agent_id`**  
- ❌ **0 spans had `workflow_id`**

### Why Metrics Showed Nothing

The metrics API queries filter spans by `agent_id` and `workflow_id`:
```python
# In api/v1/observability.py
spans_query = db.query(Span).filter(
    Span.attributes.like(f'%"agent_id":"%{agent_id}%'),  # ← NO MATCHES!
    ...
)
```

Since no spans had these attributes, **all metrics returned 0/empty**.

---

## 🎯 THE REAL PROBLEM

**Previous fix attempt failed because:**

1. **`set_span_attributes()` ran but conditions failed silently**
   - `current_span.get_span_context().is_valid` was returning `False`
   - No error was logged (only `logger.warning`)
   - Trace context was NEVER registered

2. **No trace context = No enrichment**
   - SQLite exporter looks up `trace_id` → metadata
   - If trace_id not registered, spans aren't enriched
   - Result: spans saved WITHOUT `agent_id`/`workflow_id`

---

## ✅ THE FIX APPLIED

### 1. **Simplified Trace Registration** (`agent_service.py`)

Instead of relying on `is_valid` checks, we now:
- Get the current span more robustly
- Check each attribute exists before accessing
- Use `logger.info()` so you can SEE registration in logs
- Fail gracefully with `logger.debug()` if anything goes wrong

```python
# Before: Silent failure
if current_span and current_span.get_span_context().is_valid:  # ← This was False!
    trace_id = format(...)
    # Never reached

# After: Robust checking
current_span = trace.get_current_span()
if current_span and hasattr(current_span, 'get_span_context'):
    span_context = current_span.get_span_context()
    if span_context and hasattr(span_context, 'trace_id') and span_context.trace_id:
        trace_id = format(span_context.trace_id, '032x')
        trace_context_manager.set_trace_context(...)
        logger.info(f"📊 Registered trace context...")  # ← YOU'LL SEE THIS!
```

### 2. **Explicit Span Creation** (`workflow_service.py`)

For workflows, we now CREATE a span explicitly:
```python
# Create our own root span
tracer = trace.get_tracer(__name__)
workflow_span = tracer.start_span(f"workflow.execute.{workflow_id}")

# Set attributes directly on the span
workflow_span.set_attribute("workflow_id", workflow_id)
workflow_span.set_attribute("execution_id", execution_id)

# Get trace_id from OUR span (guaranteed to exist)
trace_id = format(workflow_span.get_span_context().trace_id, '032x')

# Register for enrichment
trace_context_manager.set_trace_context(trace_id, workflow_id=workflow_id, ...)

# Execute workflow within span context
with trace.use_span(workflow_span, end_on_exit=True):
    output_data = await self._execute_workflow_graph(...)
```

### 3. **Trace Context Manager** (`trace_context.py`)

Thread-safe singleton that maintains `trace_id → metadata` mapping:
- Stores agent_id, workflow_id, session_id, etc.
- Auto-cleanup after 1 hour (prevents memory leaks)
- Used by SQLite exporter to enrich ALL spans in a trace

### 4. **SQLite Exporter Enhancement** (`sqlite_span_exporter.py`)

During export, enriches every span:
```python
# Look up metadata for this trace
trace_metadata = trace_context_manager.get_trace_context(trace_id)
if trace_metadata:
    # Add to span attributes
    for key, value in trace_metadata.items():
        attributes[key] = str(value)  # ← agent_id, workflow_id added here!
```

---

## 🚀 TESTING INSTRUCTIONS

### **Step 1: Restart Backend**

**CRITICAL:** You MUST restart for new code to load!

```bash
cd /Users/apple/Desktop/execution-plane/backend

# Stop existing process
pkill -f "uvicorn main:app"

# Start fresh (in terminal where you can see logs)
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Watch for these startup logs:**
```
✅ SQLite span exporter added for local metrics
✅ OpenLLMetry initialized successfully with traces and metrics
```

### **Step 2: Execute a Workflow OR Agent**

Execute through your frontend - any workflow or agent execution.

**Watch for these execution logs:**
```
📊 Registered trace context for workflow fd76f8fb-8da5-47fe-a454-b669275ddf85, trace_id: abc123...
```

or

```
📊 Registered trace context for agent 083d40a4-720d-423a-8402-6947f6a3b61a, trace_id: abc123...
```

**If you DON'T see these logs:**
- The code didn't reload properly
- Make sure you restarted the backend
- Check for Python import errors

### **Step 3: Verify Enrichment**

```bash
cd /Users/apple/Desktop/execution-plane/backend
python3 verify_metrics.py
```

**Expected OUTPUT:**
```
🎯 Spans with agent_id: 15     ← Should be > 0 now!
   Sample agent span: groq.chat
   agent_id: 083d40a4-720d-423a-8402-6947f6a3b61a

🎯 Spans with workflow_id: 8   ← Should be > 0 for workflows!
   Sample workflow span: workflow.execute.fd76f8fb...
   workflow_id: fd76f8fb-8da5-47fe-a454-b669275ddf85

✅ SUCCESS: Metrics system is FULLY working!
   ✓ Traces and spans are being saved to SQLite
   ✓ Agent/Workflow IDs are being captured
   ✓ Metrics endpoints will return filtered data
```

### **Step 4: Check Metrics API**

```bash
# For agent metrics
curl "http://localhost:8000/api/v1/observability/agents/083d40a4-720d-423a-8402-6947f6a3b61a/metrics?time_range=24h"

# For workflow metrics  
curl "http://localhost:8000/api/v1/observability/workflows/fd76f8fb-8da5-47fe-a454-b669275ddf85/metrics?time_range=24h"
```

**Should return data like:**
```json
{
  "total_runs": 5,
  "llm_calls": 12,
  "tool_calls": 8,
  "total_tokens": 1520,
  "total_cost": 0.0042,
  "p99_latency": 3500.2,
  ...
}
```

### **Step 5: Check Frontend UI**

Navigate to **Monitoring → Agent** or **Monitoring → Workflow**:
- All metric cards should show real numbers
- Charts should display data points
- Cost calculations should appear

---

## 🐛 DEBUGGING

### **Problem: Still seeing "0 spans with agent_id"**

**Check 1: Did you restart?**
```bash
ps aux | grep uvicorn
# Kill any old processes
pkill -f uvicorn
# Start fresh
python3 -m uvicorn main:app --reload
```

**Check 2: Are registration logs appearing?**
```bash
# In another terminal, watch logs
tail -f nohup.out | grep "Registered trace context"
```

If NO logs appear → trace context registration is failing

**Check 3: Check for errors**
```bash
tail -f nohup.out | grep -i error
```

### **Problem: Registration logs appear but no enrichment**

Check SQLite exporter logs:
```bash
tail -f nohup.out | grep "Enriched span"
```

If no "Enriched span" logs → exporter isn't finding trace context

**Manual check:**
```bash
sqlite3 agents.db "
SELECT 
  json_extract(attributes, '$.agent_id') as agent_id,
  json_extract(attributes, '$.workflow_id') as workflow_id,
  name
FROM spans 
WHERE created_at > datetime('now', '-5 minutes')
LIMIT 10;
"
```

Should show agent_id/workflow_id values (not NULL).

---

## 📁 FILES MODIFIED

| File | Purpose |
|------|---------|
| `services/trace_context.py` | **NEW** - Trace ID → metadata registry |
| `services/agent_service.py` | Robust trace context registration |
| `services/workflow_service.py` | Explicit span creation + registration |
| `services/sqlite_span_exporter.py` | Span enrichment from trace context |
| `services/telemetry_service.py` | Baggage support (backup mechanism) |
| `verify_metrics.py` | Enhanced verification with detailed output |

---

## 🎉 SUCCESS CRITERIA

After restart and execution, you should see:

1. ✅ **Registration logs** in backend console
2. ✅ **Enrichment logs** when spans are saved
3. ✅ **verify_metrics.py shows > 0 spans** with agent_id/workflow_id
4. ✅ **API returns real metrics** (not zeros)
5. ✅ **Frontend displays data** in all cards and charts

---

## 📞 IF STILL NOT WORKING

**Provide these logs:**

1. Backend startup logs (first 50 lines)
2. Execution logs showing "📊 Registered trace context" (or absence)
3. Output of `python3 verify_metrics.py`
4. Output of: 
   ```bash
   sqlite3 agents.db "SELECT COUNT(*), 
     COUNT(CASE WHEN attributes LIKE '%agent_id%' THEN 1 END) as with_agent,
     COUNT(CASE WHEN attributes LIKE '%workflow_id%' THEN 1 END) as with_workflow
   FROM spans WHERE created_at > datetime('now', '-10 minutes');"
   ```

This will help diagnose exactly where the chain is breaking!

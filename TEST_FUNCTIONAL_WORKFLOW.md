# 🧪 Test Your Functional Agentic Workflow

## ✅ Quick Start - Test Now!

### Workflow Created
- **ID:** `0949bca1-4631-47ec-a6ba-08ce7315731a`
- **Name:** AI Content Analysis Workflow
- **Status:** ✅ Ready to use

---

## 🚀 Method 1: API Testing (Recommended)

### Test with cURL

```bash
# Simple test - Analyze any content
curl -X POST http://localhost:8000/api/v1/workflows/0949bca1-4631-47ec-a6ba-08ce7315731a/execute-langgraph \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "0949bca1-4631-47ec-a6ba-08ce7315731a",
    "input_data": {
      "query": "Analyze this product review: The new smartphone is amazing! The camera quality is outstanding, battery lasts all day, and the interface is smooth. However, it is a bit expensive. Would definitely recommend to anyone looking for a premium device."
    }
  }'
```

### Expected Response
```json
{
  "success": true,
  "workflow_id": "0949bca1-4631-47ec-a6ba-08ce7315731a",
  "execution_state": {
    "completed_steps": ["workflow-start", "content-analyzer", "workflow-end"],
    "step_results": {
      "content-analyzer": {
        "output": "* Key points: Outstanding camera, long battery, smooth interface, expensive\n* Sentiment: Positive (80%)\n* Main topics: Product review, smartphone features\n* Recommendations: Good for premium buyers"
      }
    }
  }
}
```

---

## 🎨 Test Cases

### Test 1: Product Review Analysis
```bash
curl -X POST http://localhost:8000/api/v1/workflows/0949bca1-4631-47ec-a6ba-08ce7315731a/execute-langgraph \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "0949bca1-4631-47ec-a6ba-08ce7315731a",
    "input_data": {
      "query": "Analyze this review and extract: sentiment, key features mentioned, pros/cons. Review: I love this coffee maker! Brews quickly, tastes great, but cleaning is a hassle."
    }
  }'
```

### Test 2: Technical Content
```bash
curl -X POST http://localhost:8000/api/v1/workflows/0949bca1-4631-47ec-a6ba-08ce7315731a/execute-langgraph \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "0949bca1-4631-47ec-a6ba-08ce7315731a",
    "input_data": {
      "query": "Summarize key points: Docker containers provide isolated environments for applications. They are lightweight, portable, and enable consistent deployments across different platforms. Kubernetes orchestrates container deployments at scale."
    }
  }'
```

### Test 3: Customer Feedback
```bash
curl -X POST http://localhost:8000/api/v1/workflows/0949bca1-4631-47ec-a6ba-08ce7315731a/execute-langgraph \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "0949bca1-4631-47ec-a6ba-08ce7315731a",
    "input_data": {
      "query": "Analyze customer sentiment and extract action items: Customer support was slow, but the team was very helpful once connected. The product works well but installation instructions were unclear."
    }
  }'
```

---

## 🖥️ Method 2: Frontend UI

### Access Workflow in Browser

1. **Open Frontend:**
   ```bash
   http://localhost:5173
   ```

2. **Navigate to Workflows:**
   - Click "Workflows" in sidebar
   - Find "AI Content Analysis Workflow"
   - Click to view details

3. **Execute Workflow:**
   - Click "Execute" button
   - Enter your content in the input field
   - Submit and view results

### View Execution History
```bash
# Get workflow details
curl http://localhost:8000/api/v1/workflows/0949bca1-4631-47ec-a6ba-08ce7315731a
```

---

## 📊 View Monitoring Data

### Check OpenTelemetry Traces
```bash
# View backend logs
docker logs execution-plane-backend-1 | grep -A 20 "LangGraph workflow"
```

### Check Langfuse Dashboard
1. Open Langfuse dashboard (if configured)
2. Look for trace with workflow ID
3. View complete execution timeline

### Check Database Records
```bash
# Connect to PostgreSQL
docker exec -it execution-plane-postgres-1 psql -U user -d agents_db

# Query workflows
SELECT workflow_id, name, created_at FROM workflows WHERE workflow_id = '0949bca1-4631-47ec-a6ba-08ce7315731a';

# Query executions (if audit table exists)
SELECT * FROM workflow_executions WHERE workflow_id = '0949bca1-4631-47ec-a6ba-08ce7315731a' ORDER BY created_at DESC LIMIT 5;
```

---

## 🔍 Verify Monitoring

### 1. Check Execution Response
```bash
curl -X POST http://localhost:8000/api/v1/workflows/0949bca1-4631-47ec-a6ba-08ce7315731a/execute-langgraph \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "0949bca1-4631-47ec-a6ba-08ce7315731a",
    "input_data": {"query": "Test monitoring"}
  }' | python3 -m json.tool
```

Look for:
- ✅ `"success": true`
- ✅ `"metadata"` with execution_id, trace_id, timestamps
- ✅ `"completed_steps"` array
- ✅ `"step_results"` with agent output

### 2. Check Backend Logs
```bash
# Real-time log watching
docker logs -f execution-plane-backend-1 | grep "LangGraph"
```

Look for:
- ✅ "Starting LangGraph workflow execution"
- ✅ "Executing agent node with agent_id"
- ✅ "Agent execution completed successfully"
- ✅ "LangGraph execution completed"

### 3. Verify State Management
```python
# Save response to file
curl -X POST http://localhost:8000/api/v1/workflows/0949bca1-4631-47ec-a6ba-08ce7315731a/execute-langgraph \
  -H "Content-Type: application/json" \
  -d '{"workflow_id": "0949bca1-4631-47ec-a6ba-08ce7315731a", "input_data": {"query": "Test"}}' \
  > /tmp/test_response.json

# Check state structure
cat /tmp/test_response.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('Messages:', len(data['execution_state']['messages']))
print('Context keys:', list(data['execution_state']['context'].keys()))
print('Completed:', data['execution_state']['completed_steps'])
print('Results:', list(data['execution_state']['step_results'].keys()))
"
```

---

## 🎯 What to Look For

### ✅ Successful Execution Indicators

1. **Response Structure:**
   - `success: true`
   - `workflow_id` present
   - `execution_state` populated
   - `metadata` complete

2. **Agent Output:**
   - Intelligent analysis provided
   - Structured response
   - Relevant to input
   - Complete sentences

3. **State Management:**
   - All 3 steps completed
   - Messages accumulated
   - Context preserved
   - Results captured

4. **Monitoring:**
   - Execution ID generated
   - Timestamps recorded
   - Duration calculated
   - Trace ID available (if Langfuse configured)

5. **Logs:**
   - "LangGraph workflow execution" messages
   - "Agent execution completed successfully"
   - No error messages
   - Completion confirmation

---

## 🐛 Troubleshooting

### Issue: Workflow Not Found
```bash
# List all workflows
curl http://localhost:8000/api/v1/workflows/
```

### Issue: Agent Error
```bash
# Check agent exists
curl http://localhost:8000/api/v1/agents/31ab0b60-98ae-4b3e-b9c5-44481a9155eb
```

### Issue: Execution Timeout
- Agent LLM calls can take 5-10 seconds
- Wait patiently for response
- Check backend logs for progress

### Issue: No Response
```bash
# Check backend is running
curl http://localhost:8000/health

# Check Docker containers
docker ps | grep execution-plane
```

---

## 📈 Performance Benchmarks

### Expected Performance
- **Total Duration:** 3-10 seconds
- **Agent LLM Call:** 3-8 seconds
- **State Management:** <50ms
- **LangGraph Overhead:** <20ms

### Performance Test
```bash
# Time the execution
time curl -X POST http://localhost:8000/api/v1/workflows/0949bca1-4631-47ec-a6ba-08ce7315731a/execute-langgraph \
  -H "Content-Type: application/json" \
  -d '{"workflow_id": "0949bca1-4631-47ec-a6ba-08ce7315731a", "input_data": {"query": "Quick test"}}'
```

---

## 🎓 Advanced Testing

### Test with Python
```python
import requests
import json

# Execute workflow
response = requests.post(
    'http://localhost:8000/api/v1/workflows/0949bca1-4631-47ec-a6ba-08ce7315731a/execute-langgraph',
    headers={'Content-Type': 'application/json'},
    json={
        'workflow_id': '0949bca1-4631-47ec-a6ba-08ce7315731a',
        'input_data': {
            'query': 'Analyze this: Amazing product, highly recommend!'
        }
    }
)

# Parse results
result = response.json()
print(f"Success: {result['success']}")
print(f"Agent Output: {result['execution_state']['step_results']['content-analyzer']['output']}")
print(f"Duration: {result['metadata'].get('duration', 'N/A')}")
```

### Load Testing
```bash
# Run 10 concurrent requests
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/workflows/0949bca1-4631-47ec-a6ba-08ce7315731a/execute-langgraph \
    -H "Content-Type: application/json" \
    -d "{\"workflow_id\": \"0949bca1-4631-47ec-a6ba-08ce7315731a\", \"input_data\": {\"query\": \"Test $i\"}}" &
done
wait
```

---

## 📝 Create Your Own Workflows

### Template
```bash
curl -X POST http://localhost:8000/api/v1/workflows/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Workflow Name",
    "description": "What it does",
    "definition": {
      "steps": [
        {"id": "start", "type": "start"},
        {
          "id": "agent-node",
          "type": "agent",
          "agent_id": "31ab0b60-98ae-4b3e-b9c5-44481a9155eb",
          "data": {"agent_id": "31ab0b60-98ae-4b3e-b9c5-44481a9155eb"}
        },
        {"id": "end", "type": "end"}
      ],
      "dependencies": {
        "agent-node": ["start"],
        "end": ["agent-node"]
      }
    }
  }'
```

---

## 🎉 Success Checklist

Before moving to production, verify:

- [ ] Workflow executes successfully
- [ ] Agent provides meaningful output
- [ ] Monitoring data is captured
- [ ] Logs show complete trace
- [ ] State management works
- [ ] No error messages
- [ ] Response time acceptable
- [ ] Multiple test cases pass

---

*Test Guide v1.0*  
*Workflow ID: 0949bca1-4631-47ec-a6ba-08ce7315731a*  
*Status: ✅ Ready for Testing*

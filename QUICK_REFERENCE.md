# Quick Reference Guide - AI Agents Orchestration Platform

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Access Points
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📋 Core Concepts

### Agents
**Definition**: Individual AI agents with specific capabilities and tools

**Types:**
- `react` - ReAct agent (Reasoning + Acting)
- `plan-execute` - Plan & Execute agent
- `reflection` - Reflection agent (self-improving)
- `custom` - Custom graph-based agent

**Key Features:**
- Multiple LLM providers (OpenAI, Anthropic, Groq, etc.)
- Tool integration (9+ tools available)
- Memory support (Qdrant + Mem0)
- Knowledge base integration
- PII filtering
- Encrypted API key storage

### Workflows
**Definition**: Orchestrated sequences of agents working together

**Structure:**
```json
{
  "steps": [
    {
      "id": "step-1",
      "name": "Step Name",
      "agent_id": "agent-uuid",
      "description": "Description"
    }
  ],
  "dependencies": {
    "step-2": ["step-1"]
  },
  "conditions": {
    "step-3": {
      "type": "simple",
      "step_id": "step-1",
      "operator": "equals",
      "value": "success"
    }
  }
}
```

**Features:**
- Sequential execution
- Parallel execution
- Conditional branching
- Dependency management
- Resource monitoring

---

## 🔌 API Endpoints

### Agents

#### Create Agent
```http
POST /api/v1/agents/
Content-Type: application/json

{
  "name": "My Agent",
  "agent_type": "react",
  "llm_provider": "openai",
  "llm_model": "gpt-4",
  "api_key": "sk-...",
  "temperature": 0.7,
  "system_prompt": "You are a helpful assistant",
  "tools": ["duckduckgo_search"],
  "tool_configs": {},
  "max_iterations": 10,
  "streaming_enabled": true
}
```

#### Get All Agents
```http
GET /api/v1/agents/
```

#### Get Agent
```http
GET /api/v1/agents/{agent_id}
```

#### Chat with Agent
```http
POST /api/v1/agents/{agent_id}/chat/
Content-Type: application/json

{
  "message": "Hello, how are you?",
  "thread_id": "optional-thread-id"
}
```

#### Execute Agent
```http
POST /api/v1/agents/{agent_id}/execute
Content-Type: application/json

{
  "input": "Your input here"
}
```

### Workflows

#### Create Workflow
```http
POST /api/v1/workflows/
Content-Type: application/json

{
  "name": "My Workflow",
  "description": "Workflow description",
  "definition": {
    "steps": [...],
    "dependencies": {...},
    "conditions": {...}
  }
}
```

#### Execute Workflow
```http
POST /api/v1/workflows/{workflow_id}/execute
Content-Type: application/json

{
  "input_data": {
    "key": "value"
  }
}
```

#### Get Workflow Execution
```http
GET /api/v1/workflows/executions/{execution_id}
```

### Monitoring

#### Get Workflow Metrics
```http
GET /api/v1/monitoring/metrics/workflow-executions?workflow_id={id}
```

#### Get Enhanced Metrics
```http
GET /api/v1/enhanced-monitoring/enhanced-metrics/workflow-executions?workflow_id={id}
```

#### Get Performance Bottlenecks
```http
GET /api/v1/enhanced-monitoring/analytics/bottlenecks/{workflow_id}?days=30
```

#### Get Execution Logs
```http
GET /api/v1/enhanced-monitoring/logs/{execution_id}?log_level=ERROR
```

### Knowledge Bases

#### Create Knowledge Base
```http
POST /api/v1/knowledge-bases/
Content-Type: application/json

{
  "agent_id": "agent-uuid",
  "name": "My KB",
  "description": "Description",
  "embedding_model": "qwen3-embedding:0.6b",
  "chunk_size": 1000,
  "chunk_overlap": 200
}
```

#### Add Document (Text)
```http
POST /api/v1/knowledge-bases/{kb_id}/documents/text
Content-Type: multipart/form-data

text: "Document content here"
```

#### Query Knowledge Base
```http
POST /api/v1/knowledge-bases/{kb_id}/query
Content-Type: application/json

{
  "query": "Your query",
  "top_k": 5
}
```

---

## 🛠️ Available Tools

### 1. DuckDuckGo Search
- **API Key**: Not required
- **Config**: Optional `max_results` parameter
- **Use Case**: Free web search

### 2. Brave Search
- **API Key**: Required (Brave API key)
- **Config**: `api_key`, `search_count`
- **Use Case**: Privacy-focused search

### 3. GitHub Toolkit
- **API Key**: Required (GitHub App)
- **Config**: `app_id`, `private_key`, `repository`
- **Use Case**: Repository operations

### 4. Gmail Toolkit
- **API Key**: Required (OAuth2)
- **Config**: `credentials_file` path
- **Use Case**: Email operations

### 5. PlayWright Browser
- **API Key**: Not required
- **Config**: None (requires browser install)
- **Use Case**: Web automation

### 6. MCP Database
- **API Key**: Not required (requires MCP server)
- **Config**: `server_url`, `toolset`
- **Use Case**: Database operations

### 7. FireCrawl
- **API Key**: Required
- **Config**: `api_key`, `scrape_timeout`
- **Use Case**: Web scraping

### 8. Arxiv
- **API Key**: Not required
- **Config**: Optional parameters
- **Use Case**: Academic paper search

### 9. Wikipedia
- **API Key**: Not required
- **Config**: Optional parameters
- **Use Case**: Encyclopedia search

---

## 📊 Monitoring Metrics

### Workflow Execution Metrics
- `execution_time` - Total execution time (seconds)
- `step_count` - Number of steps
- `success_count` - Successful steps
- `failure_count` - Failed steps
- `retry_count` - Number of retries
- `resource_usage` - CPU, memory, I/O metrics

### Step Execution Metrics
- `execution_time` - Step execution time
- `memory_usage` - Memory usage (MB)
- `cpu_usage` - CPU usage (%)
- `io_operations` - I/O operation count
- `network_requests` - Network request count

### Analytics Available
- Performance bottlenecks
- Resource usage trends
- Failure analysis
- Predictive analytics

---

## 🔐 Security Features

### API Key Encryption
- User API keys encrypted with Fernet
- Stored encrypted in database
- Decrypted only during execution

### PII Filtering
- Configurable PII detection
- Multiple strategies: redact, mask, hash, block
- Applied to input/output/tool results

### Supported PII Types
- Email addresses
- Phone numbers
- SSN
- Credit card numbers
- IP addresses
- API keys
- And more...

---

## 💾 Memory System

### Qdrant Integration
- Vector-based memory storage
- Local embeddings (Ollama)
- Agent-specific memory isolation
- User-specific memory

### Mem0 Integration
- Fact extraction
- Conversation memory
- User preference learning

### Memory Operations
- `POST /api/v1/agents/memory/add` - Add memory
- `POST /api/v1/agents/memory/search` - Search memory
- `GET /api/v1/agents/memory/user/{user_id}` - Get user memories

---

## 🎨 Frontend Components

### Agent Components
- `AgentBuilder` - Create/edit agents
- `AgentList` - List all agents
- `AgentChat` - Chat interface
- `ToolSelection` - Tool selection UI
- `ToolConfigDialog` - Tool configuration

### Workflow Components
- `WorkflowBuilder` - Create/edit workflows
- `WorkflowList` - List all workflows
- `WorkflowVisualization` - Visual workflow graph
- `WorkflowExecutionMonitor` - Execution monitoring

### UI Components
- shadcn/ui component library
- Theme support (light/dark)
- Responsive design
- Toast notifications

---

## 🗄️ Database Schema

### Core Tables
- `agents` - Agent configurations
- `workflows` - Workflow definitions
- `workflow_executions` - Execution records
- `step_executions` - Step execution records
- `execution_logs` - Detailed logs
- `knowledge_bases` - KB metadata
- `knowledge_documents` - Document records

### Key Fields

**agents:**
- `agent_id` (UUID)
- `name`, `agent_type`, `llm_provider`, `llm_model`
- `tools` (JSON), `tool_configs` (JSON)
- `api_key_encrypted`
- `pii_config` (JSON)

**workflows:**
- `workflow_id` (UUID)
- `name`, `description`
- `definition` (JSON)

**workflow_executions:**
- `execution_id` (UUID)
- `workflow_id`, `status`
- `execution_time`, `step_count`
- `resource_usage` (JSON)

---

## 🔄 Workflow Execution Flow

```
1. Create Workflow Execution
   ↓
2. Parse Workflow Definition
   ↓
3. Identify Starting Steps (no dependencies)
   ↓
4. Execute Ready Steps in Parallel
   ↓
5. Check Dependencies for Next Steps
   ↓
6. Evaluate Conditions
   ↓
7. Execute Next Batch of Steps
   ↓
8. Repeat until all steps complete
   ↓
9. Update Execution Status
   ↓
10. Return Results
```

---

## 🐛 Troubleshooting

### Agent Not Responding
1. Check API key configuration
2. Verify LLM provider availability
3. Check agent status in database
4. Review execution logs

### Workflow Execution Failing
1. Check step dependencies
2. Verify agent IDs are valid
3. Review step execution logs
4. Check resource constraints

### Tool Not Working
1. Verify tool configuration
2. Check API keys for tools
3. Review tool-specific requirements
4. Check tool service logs

### Memory Issues
1. Verify Qdrant is running
2. Check Ollama embedding model
3. Review memory service logs
4. Check memory storage limits

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Architecture Analysis**: `ARCHITECTURE_ANALYSIS.md`
- **Tools Guide**: `TOOLS_IMPLEMENTATION_GUIDE.md`
- **API Reference**: `API_DOCUMENTATION.md`

---

## 🔗 External Dependencies

### Required Services
- **Ollama** (for embeddings): https://ollama.com/
- **Qdrant** (for vector storage): Embedded mode

### Optional Services
- **MCP Server** (for MCP Database tool)
- **GitHub App** (for GitHub toolkit)
- **OAuth Credentials** (for Gmail toolkit)

---

**Last Updated**: 2025-01-XX


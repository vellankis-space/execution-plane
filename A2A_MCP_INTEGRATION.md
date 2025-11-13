# A2A Protocol & MCP Integration

## Overview

The platform now integrates **A2A Protocol** (Agent-to-Agent) and **MCP** (Model Context Protocol) to enable standardized communication and tool access across the entire agent ecosystem.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Communication Stack                       │
├─────────────────────────────────────────────────────────────┤
│  AG-UI Protocol  │  Agent ↔ User Interface (UI)              │
│  A2A Protocol   │  Agent ↔ Agent Communication             │
│  MCP Protocol   │  Agent ↔ Tools/Resources/Context         │
└─────────────────────────────────────────────────────────────┘
```

### Three Complementary Protocols

1. **AG-UI Protocol**: Agent-to-User Interface communication (already implemented)
   - Real-time streaming
   - Event-based updates
   - Human-in-the-loop workflows

2. **A2A Protocol**: Agent-to-Agent communication (newly implemented)
   - Standardized agent collaboration
   - Agent discovery
   - Task delegation
   - Interoperability across frameworks

3. **MCP Protocol**: Agent-to-Tool/Context communication (newly implemented)
   - Standardized tool access
   - Resource management
   - Prompt templates
   - Context sharing

## A2A Protocol Integration

### What is A2A?

The **Agent-to-Agent (A2A) Protocol** is an open standard developed by Google and now part of the Linux Foundation. It provides:

- **Standardized Communication**: JSON-RPC 2.0 over HTTP(S)
- **Agent Discovery**: Agent Cards (machine-readable JSON)
- **Interoperability**: Works across different agent frameworks
- **Security**: Enterprise-grade authentication and authorization

### Features Implemented

1. **Agent Cards**
   - Machine-readable JSON documents describing agents
   - Capabilities, endpoints, authentication info
   - Automatic generation from agent configuration

2. **JSON-RPC 2.0 Communication**
   - Standardized request/response format
   - Error handling
   - Method routing

3. **Agent Discovery**
   - Discover available agents
   - Filter by capabilities
   - Get agent cards

4. **Task Execution**
   - Execute tasks on remote agents
   - Task status tracking
   - Result retrieval

### API Endpoints

#### Get Agent Card
```http
GET /api/v1/a2a/{agent_id}/agent-card
```

Returns the Agent Card for a specific agent.

#### Discover Agents
```http
GET /api/v1/a2a/discover?capabilities=search,email
```

Discover available agents, optionally filtered by capabilities.

#### Execute Task on Agent
```http
POST /api/v1/a2a/{agent_id}/execute-task
Content-Type: application/json

{
  "task_id": "task-123",
  "input": "Search for information about AI"
}
```

Execute a task on an agent via A2A Protocol.

#### Handle A2A Request (JSON-RPC 2.0)
```http
POST /api/v1/a2a/{agent_id}/a2a
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "a2a.executeTask",
  "params": {
    "task": {
      "input": "Hello, agent!"
    }
  },
  "id": "request-123"
}
```

Handle incoming A2A Protocol requests.

### Usage Example

```python
from services.a2a_protocol import A2AProtocol, AgentCard

# Create agent card
agent_card = AgentCard(
    agent_id="agent-123",
    name="Research Agent",
    version="1.0.0",
    description="Agent for research tasks",
    capabilities=["search", "summarize"],
    endpoint="/api/v1/a2a/agent-123/a2a"
)

# Create protocol instance
protocol = A2AProtocol("agent-123", agent_card)

# Call remote agent
response = await protocol.call_remote_agent(
    agent_endpoint="https://remote-agent.example.com/a2a",
    method="a2a.executeTask",
    params={"task": {"input": "Research AI trends"}}
)
```

## MCP Protocol Integration

### What is MCP?

The **Model Context Protocol (MCP)** is an open-source standard for connecting AI applications to external systems. It provides:

- **Standardized Tool Access**: Unified interface for tools
- **Resource Management**: Access to data sources
- **Prompt Templates**: Reusable prompt definitions
- **Context Sharing**: Standardized context exchange

### Features Implemented

1. **MCP Server Management**
   - Register MCP servers
   - Connect to servers (stdio, SSE, WebSocket)
   - Server capabilities discovery

2. **Tool Management**
   - List available tools
   - Call tools with standardized interface
   - Convert MCP tools to LangChain tools

3. **Resource Management**
   - List available resources
   - Read resources
   - Resource metadata

4. **Prompt Management**
   - List available prompts
   - Get prompts with arguments
   - Prompt templates

### API Endpoints

#### Register MCP Server
```http
POST /api/v1/mcp/servers
Content-Type: application/json

{
  "server_id": "mcp-server-1",
  "name": "Database MCP Server",
  "transport": "stdio",
  "command": ["python", "mcp_server.py"],
  "capabilities": {
    "tools": true,
    "resources": true
  }
}
```

#### List MCP Tools
```http
GET /api/v1/mcp/tools?server_id=mcp-server-1
```

List available MCP tools from a server.

#### Call MCP Tool
```http
POST /api/v1/mcp/tools/call?tool_name=search&server_id=mcp-server-1
Content-Type: application/json

{
  "query": "AI trends",
  "limit": 10
}
```

Call an MCP tool with arguments.

#### List MCP Resources
```http
GET /api/v1/mcp/resources?server_id=mcp-server-1
```

List available MCP resources.

#### Read MCP Resource
```http
GET /api/v1/mcp/resources/file:///path/to/file.txt?server_id=mcp-server-1
```

Read an MCP resource.

#### List MCP Prompts
```http
GET /api/v1/mcp/prompts?server_id=mcp-server-1
```

List available MCP prompts.

#### Get MCP Prompt
```http
POST /api/v1/mcp/prompts/analyze_data?server_id=mcp-server-1
Content-Type: application/json

{
  "data": "sample data"
}
```

Get an MCP prompt with arguments.

### Usage Example

```python
from services.mcp_service import mcp_service, MCPServer, MCPTool

# Register MCP server
server = MCPServer(
    server_id="db-server",
    name="Database MCP Server",
    transport="stdio",
    command=["python", "db_mcp_server.py"]
)
mcp_service.register_server(server)
await mcp_service.connect_server("db-server")

# Register MCP tool
tool = MCPTool(
    name="database_query",
    description="Query a database",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "SQL query"}
        },
        "required": ["query"]
    },
    handler=lambda query: execute_query(query)
)
mcp_service.register_tool(tool)

# List tools
tools = await mcp_service.list_tools("db-server")

# Call tool
result = await mcp_service.call_tool(
    "database_query",
    {"query": "SELECT * FROM users"},
    server_id="db-server"
)

# Convert to LangChain tool
langchain_tool = mcp_service.get_tool_as_langchain_tool("database_query")
```

## Integration with Existing Services

### Agent Service Integration

Agents can now:
- Communicate with other agents via A2A Protocol
- Access tools via MCP Protocol
- Discover and collaborate with remote agents

### Tools Service Integration

The tools service now:
- Supports MCP tools alongside LangChain tools
- Can convert MCP tools to LangChain tools
- Manages MCP server connections

### Workflow Service Integration

Workflows can:
- Delegate tasks to remote agents via A2A
- Use MCP tools in workflow steps
- Access MCP resources for context

## Benefits

### Before
- ❌ No standardized agent-to-agent communication
- ❌ Custom tool integrations
- ❌ Limited interoperability
- ❌ No agent discovery mechanism

### After
- ✅ Standardized A2A Protocol for agent communication
- ✅ MCP Protocol for standardized tool access
- ✅ Agent discovery and collaboration
- ✅ Interoperability across frameworks
- ✅ Enterprise-ready security
- ✅ Resource and context management

## Protocol Comparison

| Feature | AG-UI | A2A | MCP |
|---------|-------|-----|-----|
| **Purpose** | Agent ↔ UI | Agent ↔ Agent | Agent ↔ Tools |
| **Transport** | WebSocket | HTTP(S) | stdio/SSE/WebSocket |
| **Format** | Events | JSON-RPC 2.0 | JSON-RPC 2.0 |
| **Use Case** | User interaction | Agent collaboration | Tool access |
| **Streaming** | ✅ | ✅ | ✅ |

## Next Steps

1. **Enhanced Agent Discovery**
   - Implement distributed agent discovery
   - Agent capability matching
   - Load balancing

2. **MCP Server Registry**
   - Public MCP server registry
   - Server health monitoring
   - Automatic reconnection

3. **Security Enhancements**
   - OAuth2 for A2A
   - MCP server authentication
   - Encrypted communication

4. **Frontend Integration**
   - Agent discovery UI
   - MCP tool browser
   - Agent collaboration visualization

## Documentation

- **A2A Protocol**: https://a2a-protocol.org/latest/
- **MCP Protocol**: https://modelcontextprotocol.io/docs/getting-started/intro
- **Backend Services**:
  - `backend/services/a2a_protocol.py` - A2A Protocol implementation
  - `backend/services/mcp_service.py` - MCP Protocol implementation
- **API Endpoints**:
  - `backend/api/v1/a2a.py` - A2A API endpoints
  - `backend/api/v1/mcp.py` - MCP API endpoints

---

**The integration of A2A and MCP protocols provides a complete, standardized communication stack for the AI agents orchestration platform!**


# MCP (Model Context Protocol) Implementation Plan

## Executive Summary
Implement FastMCP framework to enable the platform to act as an MCP host, connecting to external MCP servers and exposing their tools, resources, and prompts to agents.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Intelligentic AI Platform                 │
│                        (MCP Host/Client)                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Agent Builder│  │  Agent       │  │  MCP         │     │
│  │      UI      │──│  Execution   │──│  Manager     │     │
│  └──────────────┘  └──────────────┘  └──────┬───────┘     │
│                                              │              │
└──────────────────────────────────────────────┼──────────────┘
                                               │
                    ┌──────────────────────────┼──────────────────────┐
                    │         FastMCP Client Layer                     │
                    └──────────────────────────┬──────────────────────┘
                                               │
        ┌──────────────────┬──────────────────┼──────────────────┬───────────────┐
        │                  │                   │                  │               │
┌───────▼────────┐ ┌───────▼────────┐ ┌───────▼────────┐ ┌──────▼──────┐ ┌─────▼─────┐
│  MCP Server 1  │ │  MCP Server 2  │ │  MCP Server 3  │ │  MCP        │ │   MCP     │
│  (HTTP/SSE)    │ │  (STDIO)       │ │  (Python)      │ │  Server N   │ │ Inspector │
│                │ │                │ │                │ │             │ │           │
│  • Weather API │ │  • Database    │ │  • Local Tools │ │  • Custom   │ │ • Debug   │
│  • Stock API   │ │  • File System │ │  • Scripts     │ │             │ │           │
└────────────────┘ └────────────────┘ └────────────────┘ └─────────────┘ └───────────┘
```

## Phase 1: Backend Foundation

### 1.1 Install FastMCP
```bash
pip install fastmcp
```

### 1.2 Database Schema
Create tables for MCP server configurations:

```sql
CREATE TABLE mcp_servers (
    id VARCHAR PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    transport_type VARCHAR NOT NULL,  -- 'http', 'sse', 'stdio'
    config JSON NOT NULL,             -- Transport-specific config
    status VARCHAR DEFAULT 'inactive', -- 'active', 'inactive', 'error'
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE mcp_server_tools (
    id VARCHAR PRIMARY KEY,
    mcp_server_id VARCHAR REFERENCES mcp_servers(id),
    tool_name VARCHAR NOT NULL,
    description TEXT,
    schema JSON,
    discovered_at TIMESTAMP
);

CREATE TABLE agent_mcp_servers (
    agent_id VARCHAR REFERENCES agents(agent_id),
    mcp_server_id VARCHAR REFERENCES mcp_servers(id),
    PRIMARY KEY (agent_id, mcp_server_id)
);
```

### 1.3 API Endpoints
Create new endpoints:
- `POST /api/v1/mcp/servers` - Register new MCP server
- `GET /api/v1/mcp/servers` - List all MCP servers
- `GET /api/v1/mcp/servers/{id}` - Get MCP server details
- `PUT /api/v1/mcp/servers/{id}` - Update MCP server config
- `DELETE /api/v1/mcp/servers/{id}` - Remove MCP server
- `POST /api/v1/mcp/servers/{id}/connect` - Test connection
- `GET /api/v1/mcp/servers/{id}/tools` - List tools from server
- `POST /api/v1/mcp/servers/{id}/tools/{tool_name}/execute` - Execute tool
- `GET /api/v1/mcp/servers/{id}/resources` - List resources
- `GET /api/v1/mcp/servers/{id}/prompts` - List prompts

## Phase 2: MCP Client Service

### 2.1 MCP Manager Service
Create `backend/services/mcp_manager.py`:

```python
from fastmcp import Client
from typing import Dict, List, Optional
import asyncio

class MCPManager:
    def __init__(self):
        self.clients: Dict[str, Client] = {}
        self.configs: Dict[str, dict] = {}
    
    async def register_server(self, server_id: str, config: dict):
        """Register and connect to an MCP server"""
        pass
    
    async def get_client(self, server_id: str) -> Client:
        """Get or create MCP client for server"""
        pass
    
    async def discover_tools(self, server_id: str) -> List[dict]:
        """Discover all tools from MCP server"""
        pass
    
    async def call_tool(self, server_id: str, tool_name: str, args: dict):
        """Execute a tool on MCP server"""
        pass
    
    async def health_check(self, server_id: str) -> bool:
        """Check if MCP server is reachable"""
        pass
```

### 2.2 Configuration Support
Support multiple configuration formats:

**HTTP/SSE Server:**
```json
{
    "transport": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
        "Authorization": "Bearer token"
    }
}
```

**STDIO Server:**
```json
{
    "transport": "stdio",
    "command": "python",
    "args": ["./mcp_server.py"],
    "env": {
        "API_KEY": "xxx"
    }
}
```

## Phase 3: Frontend UI Updates

### 3.1 MCP Servers Management Page
Create new page: `/mcp-servers`

Features:
- List all registered MCP servers
- Add new MCP server (with form)
- Edit server configuration
- Test connection
- View available tools
- Enable/disable servers
- Delete servers

### 3.2 Agent Builder MCP Integration

Add new section to Agent Builder:

```
┌─────────────────────────────────────────────────────────┐
│ MCP Servers                                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Select MCP servers to connect this agent to:            │
│                                                          │
│ ☑ Weather Service (5 tools available)         [Config] │
│ ☑ Database Manager (8 tools available)        [Config] │
│ ☐ File System (12 tools available)            [Config] │
│ ☐ Stock API (6 tools available)               [Config] │
│                                                          │
│ [+ Add New MCP Server]                                  │
│                                                          │
│ Available MCP Tools (13):                               │
│ ┌────────────────────────────────────────────────────┐ │
│ │ ☑ weather_get_forecast - Get weather forecast     │ │
│ │ ☑ weather_get_current - Get current weather       │ │
│ │ ☑ db_query - Execute SQL query                    │ │
│ │ ☑ db_insert - Insert data                         │ │
│ │ ...                                                │ │
│ └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 3.3 MCP Server Configuration Modal

```
┌─────────────────────────────────────────────────────────┐
│ Add MCP Server                                    [X]   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Server Name:                                            │
│ [Weather API                                         ]  │
│                                                          │
│ Description:                                            │
│ [External weather data provider                     ]  │
│                                                          │
│ Transport Type:                                         │
│ [HTTP ▼]  [STDIO]  [SSE]                               │
│                                                          │
│ ┌─ HTTP Configuration ──────────────────────────────┐  │
│ │                                                    │  │
│ │ Server URL:                                        │  │
│ │ [https://weather-api.example.com/mcp           ]  │  │
│ │                                                    │  │
│ │ Authentication:                                    │  │
│ │ [Bearer Token ▼]                                  │  │
│ │                                                    │  │
│ │ API Key:                                           │  │
│ │ [••••••••••••••                                 ]  │  │
│ │                                                    │  │
│ │ Additional Headers (JSON):                         │  │
│ │ {                                                  │  │
│ │   "User-Agent": "Intelligentic-AI"                │  │
│ │ }                                                  │  │
│ │                                                    │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│              [Test Connection]  [Cancel]  [Add Server]  │
└─────────────────────────────────────────────────────────┘
```

## Phase 4: Agent Integration

### 4.1 Dynamic Tool Loading
When agent is executed:
1. Load configured MCP servers
2. Connect to each server
3. Discover available tools
4. Add MCP tools to agent's toolset
5. Prefix tools with server name (e.g., `weather_get_forecast`)

### 4.2 Tool Execution Wrapper
Create wrapper that routes tool calls to appropriate MCP server:

```python
async def execute_mcp_tool(server_id: str, tool_name: str, args: dict):
    mcp_manager = get_mcp_manager()
    client = await mcp_manager.get_client(server_id)
    result = await client.call_tool(tool_name, args)
    return result.data
```

## Phase 5: Advanced Features

### 5.1 MCP Inspector
Build a debugging UI that shows:
- Connected servers
- Available tools per server
- Tool execution history
- Error logs
- Performance metrics

### 5.2 MCP Resources Support
Implement resources loading:
- List available resources from servers
- Load resources into agent context
- Cache resource data

### 5.3 MCP Prompts Support
Implement prompt templates:
- List available prompts from servers
- Render prompts with parameters
- Use prompts in agent conversations

### 5.4 Health Monitoring
Background service that:
- Periodically pings MCP servers
- Updates server status
- Sends alerts on failures
- Auto-reconnects on recovery

## Implementation Steps

### Step 1: Backend Setup (Day 1)
- [ ] Install fastmcp
- [ ] Create database models
- [ ] Create API endpoints
- [ ] Implement MCP manager service

### Step 2: Basic UI (Day 1-2)
- [ ] Create MCP servers management page
- [ ] Add server configuration modal
- [ ] Implement server list/add/edit/delete

### Step 3: Agent Integration (Day 2)
- [ ] Add MCP section to agent builder
- [ ] Implement tool discovery
- [ ] Connect MCP tools to agent execution

### Step 4: Testing & Polish (Day 2-3)
- [ ] Test with sample MCP servers
- [ ] Add error handling
- [ ] Improve UI/UX
- [ ] Documentation

## Sample MCP Server Configurations

### Weather API (HTTP)
```json
{
    "name": "Weather Service",
    "transport": "http",
    "url": "https://weather.example.com/mcp",
    "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
    }
}
```

### Local Database (STDIO)
```json
{
    "name": "Database Manager",
    "transport": "stdio",
    "command": "python",
    "args": ["./mcp_servers/database.py"],
    "env": {
        "DB_PATH": "/data/app.db"
    }
}
```

### File System (STDIO)
```json
{
    "name": "File System",
    "transport": "stdio",
    "command": "python",
    "args": ["./mcp_servers/filesystem.py"],
    "env": {
        "BASE_PATH": "/workspace"
    }
}
```

## Security Considerations

1. **Authentication**: Store API keys securely (encrypted in DB)
2. **Sandboxing**: Limit STDIO servers to specific directories
3. **Rate Limiting**: Prevent abuse of MCP tools
4. **Validation**: Validate all tool inputs/outputs
5. **Permissions**: Role-based access to MCP servers

## Testing Strategy

1. **Unit Tests**: Test MCP manager service
2. **Integration Tests**: Test with mock MCP servers
3. **E2E Tests**: Test full agent workflow with MCP
4. **Manual Testing**: Test with real MCP servers

## Documentation Needs

1. User Guide: How to add MCP servers
2. Developer Guide: How to create custom MCP servers
3. API Reference: MCP endpoints
4. Examples: Sample MCP server implementations

## Success Metrics

- ✅ Can connect to HTTP/SSE MCP servers
- ✅ Can connect to STDIO MCP servers
- ✅ Tools from MCP servers available in agents
- ✅ Agents can successfully execute MCP tools
- ✅ UI allows easy MCP server management
- ✅ Error handling and recovery works
- ✅ Performance acceptable (<500ms for tool discovery)

## Future Enhancements

1. MCP Server Marketplace
2. Pre-built MCP server templates
3. MCP server health dashboard
4. MCP tool usage analytics
5. MCP server versioning
6. Automatic tool documentation generation
7. MCP proxy/gateway for better security
8. MCP tool chaining and workflows

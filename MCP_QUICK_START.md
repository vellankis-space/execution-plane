# MCP Quick Start Guide 🚀

## 5-Minute Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt  # Includes fastmcp==2.13.1
```

### 2. Start the Platform
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 3. Create a Test MCP Server
```bash
# save as weather_server.py
cat > weather_server.py << 'EOF'
from fastmcp import FastMCP

mcp = FastMCP("Weather Tools")

@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather"""
    return f"Weather in {city}: Sunny, 72°F"

if __name__ == "__main__":
    mcp.run()
EOF

# Run it
python weather_server.py
```

### 4. Register in UI
1. Open http://localhost:5173/mcp-servers
2. Click "Add MCP Server"
3. Fill in:
   - Name: `Weather Tools`
   - Transport: `STDIO`
   - Command: `python`
   - Args: `["weather_server.py"]`
4. Click "Add Server"
5. Click "Connect"

### 5. Create Agent
1. Go to `/playground`
2. Create agent (any type)
3. Scroll to "MCP Servers" section
4. Check "Weather Tools"
5. Save agent

### 6. Test
1. Go to `/chat`
2. Select your agent
3. Ask: "What's the weather in NYC?"
4. Agent uses MCP tool! ✨

## API Examples

### Create MCP Server
```bash
curl -X POST http://localhost:8000/api/v1/mcp-servers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Server",
    "transport_type": "stdio",
    "command": "python",
    "args": ["server.py"]
  }'
```

### Connect to Server
```bash
curl -X POST http://localhost:8000/api/v1/mcp-servers/{server_id}/connect
```

### List Tools
```bash
curl http://localhost:8000/api/v1/mcp-servers/{server_id}/tools
```

### Call Tool
```bash
curl -X POST http://localhost:8000/api/v1/mcp-servers/{server_id}/tools/get_weather/call \
  -H "Content-Type: application/json" \
  -d '{"city": "San Francisco"}'
```

## MCP Server Templates

### HTTP Server
```json
{
  "name": "External API",
  "transport_type": "http",
  "url": "https://api.example.com/mcp",
  "auth_type": "bearer",
  "auth_token": "sk-xxx"
}
```

### STDIO Server
```json
{
  "name": "Local Tools",
  "transport_type": "stdio",
  "command": "python",
  "args": ["tools.py"],
  "env": {"API_KEY": "xxx"},
  "cwd": "/path/to/project"
}
```

### SSE Server
```json
{
  "name": "Stream Server",
  "transport_type": "sse",
  "url": "https://stream.example.com/mcp"
}
```

## Sample MCP Servers

### Database Tools
```python
from fastmcp import FastMCP
import sqlite3

mcp = FastMCP("Database Tools")

@mcp.tool()
def query_db(sql: str) -> list:
    """Execute SQL query"""
    conn = sqlite3.connect('data.db')
    results = conn.execute(sql).fetchall()
    conn.close()
    return results

@mcp.tool()
def list_tables() -> list:
    """List all tables"""
    conn = sqlite3.connect('data.db')
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    conn.close()
    return [t[0] for t in tables]

if __name__ == "__main__":
    mcp.run()
```

### File System Tools
```python
from fastmcp import FastMCP
import os

mcp = FastMCP("File System")

@mcp.tool()
def list_files(directory: str = ".") -> list:
    """List files in directory"""
    return os.listdir(directory)

@mcp.tool()
def read_file(path: str) -> str:
    """Read file contents"""
    with open(path, 'r') as f:
        return f.read()

@mcp.resource("fs://workspace")
def workspace_info():
    """Get workspace info"""
    return {"cwd": os.getcwd(), "files": len(os.listdir())}

if __name__ == "__main__":
    mcp.run()
```

### API Client Tools
```python
from fastmcp import FastMCP
import requests

mcp = FastMCP("API Client")

@mcp.tool()
def fetch_data(endpoint: str) -> dict:
    """Fetch data from API"""
    response = requests.get(f"https://api.example.com/{endpoint}")
    return response.json()

@mcp.tool()
def post_data(endpoint: str, data: dict) -> dict:
    """Post data to API"""
    response = requests.post(
        f"https://api.example.com/{endpoint}",
        json=data
    )
    return response.json()

if __name__ == "__main__":
    mcp.run()
```

## Troubleshooting

### Server Won't Connect
- Check if MCP server process is running
- Verify command/args are correct
- Check logs in backend terminal

### Tools Not Appearing
- Click "Connect" button on server
- Verify server status is "active"
- Check backend logs for errors

### Tool Execution Fails
- Test tool directly on MCP server
- Check tool arguments match schema
- Verify server is still connected

### Agent Can't Use Tools
- Ensure MCP server is checked in agent config
- Verify server is active (not inactive)
- Re-create agent if needed

## Common Patterns

### Multi-Tool Server
```python
mcp = FastMCP("Multi Tools")

@mcp.tool()
def tool1(arg: str) -> str:
    return f"Tool1: {arg}"

@mcp.tool()
def tool2(arg: int) -> int:
    return arg * 2

@mcp.tool()
def tool3(arg: dict) -> dict:
    return {"result": arg}
```

### With Resources
```python
@mcp.resource("config://settings")
def get_settings():
    return {"version": "1.0"}

@mcp.resource("data://users")
def get_users():
    return [{"id": 1, "name": "Alice"}]
```

### With Prompts
```python
@mcp.prompt()
def analyze_prompt(data: str):
    return {
        "messages": [
            {"role": "system", "content": "You are an analyst"},
            {"role": "user", "content": f"Analyze: {data}"}
        ]
    }
```

## Best Practices

✅ **DO:**
- Keep tools focused and simple
- Validate inputs with Pydantic
- Return structured data
- Include clear descriptions
- Handle errors gracefully

❌ **DON'T:**
- Make tools too complex
- Return huge data blobs
- Ignore error handling
- Forget to document tools
- Use blocking operations

## Performance Tips

1. **Connection Pooling** - Reuse connections
2. **Lazy Loading** - Load tools when needed
3. **Caching** - Cache tool schemas
4. **Async** - Use async/await
5. **Timeouts** - Set reasonable timeouts

## Security Checklist

- [ ] Use HTTPS for remote servers
- [ ] Store API keys in environment variables
- [ ] Validate all inputs
- [ ] Limit tool access per agent
- [ ] Monitor tool usage
- [ ] Rotate credentials regularly
- [ ] Use least privilege principle

## UI Features

### MCP Servers Page
- ✅ Server list with status
- ✅ Add/Edit/Delete servers
- ✅ Connect/Disconnect
- ✅ View tools, resources, prompts
- ✅ Health checks
- ✅ Error messages

### Agent Builder
- ✅ MCP Servers section
- ✅ Server selection
- ✅ Tool counts
- ✅ Status indicators
- ✅ Quick add link

## Advanced Usage

### Custom Transport
```python
from fastmcp import FastMCP
from fastmcp.client import Client

# Use custom client
config = {
    "mcpServers": {
        "custom": {
            "url": "https://custom.example.com",
            "headers": {"X-Custom": "value"}
        }
    }
}
client = Client(config)
```

### Tool Composition
```python
@mcp.tool()
def composite_tool(input: str) -> str:
    result1 = tool1(input)
    result2 = tool2(result1)
    return tool3(result2)
```

### Dynamic Tools
```python
def create_tool(name: str):
    @mcp.tool()
    def dynamic_tool(input: str) -> str:
        return f"{name}: {input}"
    return dynamic_tool

# Create multiple tools
for i in range(5):
    create_tool(f"tool_{i}")
```

## Resources

- **FastMCP Docs:** https://gofastmcp.com
- **MCP Spec:** https://modelcontextprotocol.io
- **Platform Docs:** See `MCP_IMPLEMENTATION_COMPLETE.md`

## Support

Need help?
1. Check logs: `backend/main.py` output
2. Test connection: Click "Connect" button
3. View tools: Click wrench icon
4. Check status: Server status badge

---

**That's it! You're ready to extend your agents with MCP! 🎉**

For complete documentation, see `MCP_INTEGRATION_COMPLETE.md`

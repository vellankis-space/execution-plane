# MCP Integration Guide

This guide explains how to integrate Docker-based MCP (Model Context Protocol) toolkits with the Execution Plane project.

## Overview

The Execution Plane project now supports loading MCP server configurations from a JSON file (`mcp.json`) at startup. This allows you to easily integrate Docker-based MCP toolkits without manual configuration through the UI.

## How It Works

1. The system looks for an `mcp.json` file in the project root directory at startup
2. If found, it automatically loads all MCP server configurations from the file
3. The servers are registered with the FastMCP manager and ready for use

## Configuration File Format

The `mcp.json` file should follow this structure:

```json
{
  "mcpServers": {
    "server-name": {
      "transport": "stdio|http|sse",
      "command": "executable-command", // For stdio transport
      "args": ["arg1", "arg2"],       // For stdio transport
      "url": "http://server-url",     // For http/sse transport
      "auth_type": "bearer",          // Optional authentication type
      "auth_token": "api-token",      // Optional authentication token
      "headers": {},                  // Optional HTTP headers
      "env": {},                      // Optional environment variables
      "cwd": "/working/directory"     // Optional working directory
    }
  }
}
```

## Docker MCP Toolkit Integration

### Option 1: Direct Docker Execution (STDIO)

To run a Docker-based MCP toolkit as a local process:

```json
{
  "mcpServers": {
    "docker-toolkit": {
      "transport": "stdio",
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "your-mcp-image:tag",
        "mcp-server-executable"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Option 2: Pre-running Docker Container (HTTP)

To connect to a Docker container running an MCP server:

```json
{
  "mcpServers": {
    "docker-http-toolkit": {
      "transport": "http",
      "url": "http://localhost:3000",
      "auth_token": "your-api-token"  // If required
    }
  }
}
```

## Example: Calculator MCP Server

Here's a complete example of a simple calculator MCP server that can be run locally:

```json
{
  "mcpServers": {
    "local-calculator": {
      "transport": "stdio",
      "command": "python",
      "args": [
        "-c",
        "import json, sys; print(json.dumps({'protocolVersion': '2024-06-12', 'capabilities': {'tools': {'listTools': True}}})); sys.stdout.flush(); exec('import sys,json\\nwhile True:\\n line = sys.stdin.readline()\\n if not line: break\\n try:\\n  req = json.loads(line)\\n  if req.get(\"method\") == \"tools/list\":\\n   resp = {\"id\": req.get(\"id\"), \"result\": {\"tools\": [{\"name\": \"calculate\", \"description\": \"Performs basic arithmetic calculations\", \"inputSchema\": {\"type\": \"object\", \"properties\": {\"expression\": {\"type\": \"string\", \"description\": \"Mathematical expression to evaluate\"}}, \"required\": [\"expression\"]}}]}}\\n   print(json.dumps(resp))\\n   sys.stdout.flush()\\n  elif req.get(\"method\") == \"tools/call\":\\n   args = req.get(\"params\", {}).get(\"arguments\", {})\\n   expr = args.get(\"expression\", \"\")\\n   try:\\n    result = eval(expr)\\n    resp = {\"id\": req.get(\"id\"), \"result\": {\"content\": [{\"type\": \"text\", \"text\": str(result)}]}}\\n   except Exception as e:\\n    resp = {\"id\": req.get(\"id\"), \"error\": {\"code\": -32603, \"message\": str(e)}}\\n   print(json.dumps(resp))\\n   sys.stdout.flush()\\n except Exception as e:\\n  print(json.dumps({\"id\": 0, \"error\": {\"code\": -32700, \"message\": str(e)}}))\\n  sys.stdout.flush()\\n')"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Usage

1. Create an `mcp.json` file in the project root directory with your MCP server configurations
2. Start the Execution Plane backend (the MCP servers will be automatically loaded)
3. Access the MCP Servers page in the UI to see your configured servers
4. Connect to the servers to discover and use their tools in your agents

## Verification

To verify that your MCP configuration is working:

1. Check the backend logs for messages about loading MCP configurations
2. Look for successful server registration messages
3. Verify that tools are discovered when connecting to servers

## Benefits

- **Automatic Loading**: MCP servers are loaded at startup without manual configuration
- **Flexible Configuration**: Support for various transport types and authentication methods
- **Easy Deployment**: Simple JSON configuration makes it easy to deploy consistent MCP setups
- **Docker Integration**: Seamless integration with Docker-based MCP toolkits
"""
Unit tests for MCPService
"""
import pytest
from services.mcp_service import mcp_service, MCPServer, MCPTool, MCPResource, MCPPrompt


def test_register_server():
    """Test registering an MCP server"""
    server = MCPServer(
        server_id="test-server",
        name="Test MCP Server",
        transport="stdio",
        command=["python", "test_server.py"]
    )
    
    mcp_service.register_server(server)
    
    assert "test-server" in mcp_service.servers
    assert mcp_service.servers["test-server"].name == "Test MCP Server"


def test_register_tool():
    """Test registering an MCP tool"""
    tool = MCPTool(
        name="test_tool",
        description="A test tool",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        },
        handler=lambda query: f"Result for {query}"
    )
    
    mcp_service.register_tool(tool)
    
    assert "test_tool" in mcp_service.tools
    assert mcp_service.tools["test_tool"].name == "test_tool"


def test_register_resource():
    """Test registering an MCP resource"""
    resource = MCPResource(
        uri="file:///test/file.txt",
        name="Test File",
        description="A test resource",
        mimeType="text/plain"
    )
    
    mcp_service.register_resource(resource)
    
    assert "file:///test/file.txt" in mcp_service.resources
    assert mcp_service.resources["file:///test/file.txt"].name == "Test File"


def test_register_prompt():
    """Test registering an MCP prompt"""
    prompt = MCPPrompt(
        name="test_prompt",
        description="A test prompt",
        arguments=[
            {"name": "topic", "description": "Topic to write about", "required": True}
        ]
    )
    
    mcp_service.register_prompt(prompt)
    
    assert "test_prompt" in mcp_service.prompts
    assert mcp_service.prompts["test_prompt"].name == "test_prompt"


@pytest.mark.asyncio
async def test_list_tools():
    """Test listing MCP tools"""
    # Register a tool first
    tool = MCPTool(
        name="list_test_tool",
        description="Test tool for listing",
        inputSchema={"type": "object", "properties": {}}
    )
    mcp_service.register_tool(tool)
    
    tools = await mcp_service.list_tools()
    
    assert len(tools) >= 1
    assert any(t.name == "list_test_tool" for t in tools)


@pytest.mark.asyncio
async def test_call_tool():
    """Test calling an MCP tool"""
    # Register a tool with handler
    def test_handler(query: str) -> str:
        return f"Result: {query}"
    
    tool = MCPTool(
        name="call_test_tool",
        description="Test tool for calling",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        },
        handler=test_handler
    )
    mcp_service.register_tool(tool)
    
    result = await mcp_service.call_tool("call_test_tool", {"query": "test"})
    
    assert result["isError"] is False
    assert "test" in result["content"][0]["text"]


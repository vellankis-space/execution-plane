"""
MCP (Model Context Protocol) API Endpoints
Standardized tool and resource access
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import logging

from core.database import get_db
from services.mcp_service import mcp_service, MCPServer, MCPTool, MCPResource, MCPPrompt

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/servers")
async def register_mcp_server(server: Dict[str, Any]):
    """Register an MCP server"""
    try:
        mcp_server = MCPServer(
            server_id=server["server_id"],
            name=server["name"],
            transport=server["transport"],
            endpoint=server.get("endpoint"),
            command=server.get("command"),
            env=server.get("env"),
            capabilities=server.get("capabilities")
        )
        mcp_service.register_server(mcp_server)
        
        # Connect to server
        await mcp_service.connect_server(server["server_id"])
        
        return {"status": "registered", "server_id": server["server_id"]}
    
    except Exception as e:
        logger.error(f"Error registering MCP server: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools")
async def list_mcp_tools(server_id: Optional[str] = None) -> Dict[str, Any]:
    """List available MCP tools"""
    try:
        tools = await mcp_service.list_tools(server_id)
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in tools
            ],
            "count": len(tools)
        }
    except Exception as e:
        logger.error(f"Error listing MCP tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/call")
async def call_mcp_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    server_id: Optional[str] = None
) -> Dict[str, Any]:
    """Call an MCP tool"""
    try:
        result = await mcp_service.call_tool(tool_name, arguments, server_id)
        return result
    except Exception as e:
        logger.error(f"Error calling MCP tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources")
async def list_mcp_resources(server_id: Optional[str] = None) -> Dict[str, Any]:
    """List available MCP resources"""
    try:
        resources = await mcp_service.list_resources(server_id)
        return {
            "resources": [
                {
                    "uri": resource.uri,
                    "name": resource.name,
                    "description": resource.description,
                    "mimeType": resource.mimeType
                }
                for resource in resources
            ],
            "count": len(resources)
        }
    except Exception as e:
        logger.error(f"Error listing MCP resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources/{uri:path}")
async def read_mcp_resource(
    uri: str,
    server_id: Optional[str] = None
) -> Dict[str, Any]:
    """Read an MCP resource"""
    try:
        result = await mcp_service.read_resource(uri, server_id)
        return result
    except Exception as e:
        logger.error(f"Error reading MCP resource: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prompts")
async def list_mcp_prompts(server_id: Optional[str] = None) -> Dict[str, Any]:
    """List available MCP prompts"""
    try:
        prompts = await mcp_service.list_prompts(server_id)
        return {
            "prompts": [
                {
                    "name": prompt.name,
                    "description": prompt.description,
                    "arguments": prompt.arguments
                }
                for prompt in prompts
            ],
            "count": len(prompts)
        }
    except Exception as e:
        logger.error(f"Error listing MCP prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prompts/{prompt_name}")
async def get_mcp_prompt(
    prompt_name: str,
    arguments: Optional[Dict[str, Any]] = None,
    server_id: Optional[str] = None
) -> Dict[str, Any]:
    """Get an MCP prompt"""
    try:
        result = await mcp_service.get_prompt(prompt_name, arguments, server_id)
        return result
    except Exception as e:
        logger.error(f"Error getting MCP prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


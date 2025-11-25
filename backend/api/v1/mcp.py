"""
MCP (Model Context Protocol) API Endpoints
Standardized tool and resource access using FastMCP
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import logging

from core.database import get_db
from services.fastmcp_manager import fastmcp_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/servers")
async def register_mcp_server(server: Dict[str, Any]):
    """
    Register an MCP server (deprecated - use /api/v1/mcp-servers instead)
    """
    logger.warning("Deprecated endpoint used: /api/v1/mcp/servers. Use /api/v1/mcp-servers instead.")
    raise HTTPException(
        status_code=410,
        detail="This endpoint is deprecated. Please use /api/v1/mcp-servers/ for MCP server management."
    )


@router.get("/tools")
async def list_mcp_tools(server_id: Optional[str] = None) -> Dict[str, Any]:
    """List available MCP tools from FastMCP manager"""
    try:
        tools = await fastmcp_manager.get_tools(server_id)
        return {
            "tools": tools,
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
    """Call an MCP tool via FastMCP manager"""
    try:
        if not server_id:
            raise HTTPException(status_code=400, detail="server_id is required")
        
        result = await fastmcp_manager.call_tool(server_id, tool_name, arguments)
        return {"result": result}
    except Exception as e:
        logger.error(f"Error calling MCP tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources")
async def list_mcp_resources(server_id: Optional[str] = None) -> Dict[str, Any]:
    """List available MCP resources from FastMCP manager"""
    try:
        resources = await fastmcp_manager.get_resources(server_id)
        return {
            "resources": resources,
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
    """Read an MCP resource via FastMCP manager"""
    try:
        if not server_id:
            raise HTTPException(status_code=400, detail="server_id is required")
        
        result = await fastmcp_manager.read_resource(server_id, uri)
        return {"result": result}
    except Exception as e:
        logger.error(f"Error reading MCP resource: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prompts")
async def list_mcp_prompts(server_id: Optional[str] = None) -> Dict[str, Any]:
    """List available MCP prompts from FastMCP manager"""
    try:
        prompts = await fastmcp_manager.get_prompts(server_id)
        return {
            "prompts": prompts,
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
    """Get an MCP prompt (deprecated - prompts not yet implemented in FastMCP manager)"""
    logger.warning("MCP prompts endpoint called but not fully implemented in FastMCP manager")
    raise HTTPException(
        status_code=501,
        detail="Prompts are not yet fully implemented. Please use tools and resources instead."
    )


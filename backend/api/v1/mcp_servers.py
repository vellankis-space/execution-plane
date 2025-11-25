"""
MCP Servers API Endpoints
Manage MCP server configurations and connections using FastMCP
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timezone
import uuid
import json

from core.database import get_db
from models.mcp_server import MCPServer, AgentMCPServer
from services.fastmcp_manager import fastmcp_manager, MCPServerConfig

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for API
class MCPServerCreate(BaseModel):
    name: str = Field(..., description="Server name")
    description: str = Field("", description="Server description")
    transport_type: str = Field(..., description="Transport type: http, sse, stdio")
    
    # HTTP/SSE fields
    url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    auth_type: Optional[str] = None
    auth_token: Optional[str] = None
    
    # STDIO fields
    command: Optional[str] = None
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    cwd: Optional[str] = None


class MCPServerUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    auth_type: Optional[str] = None
    auth_token: Optional[str] = None
    command: Optional[str] = None
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    cwd: Optional[str] = None


class MCPServerResponse(BaseModel):
    server_id: str
    name: str
    description: str
    transport_type: str
    status: str
    url: Optional[str] = None
    command: Optional[str] = None
    tools_count: int
    resources_count: int
    prompts_count: int
    last_connected: Optional[str] = None
    last_error: Optional[str] = None
    created_at: str


@router.post("/", response_model=MCPServerResponse, status_code=status.HTTP_201_CREATED)
async def create_mcp_server(
    server_data: MCPServerCreate,
    db: Session = Depends(get_db)
):
    """
    Create and register a new MCP server.
    """
    try:
        # Generate unique server ID
        server_id = f"mcp_{uuid.uuid4().hex[:12]}"
        
        # Create database record
        db_server = MCPServer(
            server_id=server_id,
            name=server_data.name,
            description=server_data.description,
            transport_type=server_data.transport_type,
            url=server_data.url,
            headers=server_data.headers,
            auth_type=server_data.auth_type,
            auth_token=server_data.auth_token,
            command=server_data.command,
            args=server_data.args,
            env=server_data.env,
            cwd=server_data.cwd,
            status="inactive"
        )
        
        db.add(db_server)
        db.commit()
        db.refresh(db_server)
        
        # Register with FastMCP manager
        config = MCPServerConfig(
            server_id=server_id,
            name=server_data.name,
            description=server_data.description,
            transport_type=server_data.transport_type,
            url=server_data.url,
            headers=server_data.headers or {},
            auth_type=server_data.auth_type,
            auth_token=server_data.auth_token,
            command=server_data.command,
            args=server_data.args or [],
            env=server_data.env or {},
            cwd=server_data.cwd
        )
        
        await fastmcp_manager.register_server(config)
        
        logger.info(f"Created MCP server: {server_id} ({server_data.name})")
        
        return MCPServerResponse(
            server_id=db_server.server_id,
            name=db_server.name,
            description=db_server.description or "",
            transport_type=db_server.transport_type,
            status=db_server.status,
            url=db_server.url,
            command=db_server.command,
            tools_count=db_server.tools_count,
            resources_count=db_server.resources_count,
            prompts_count=db_server.prompts_count,
            last_connected=db_server.last_connected.isoformat() if db_server.last_connected else None,
            last_error=db_server.last_error,
            created_at=db_server.created_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error creating MCP server: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[MCPServerResponse])
async def list_mcp_servers(db: Session = Depends(get_db)):
    """
    List all registered MCP servers.
    """
    try:
        servers = db.query(MCPServer).all()
        
        return [
            MCPServerResponse(
                server_id=server.server_id,
                name=server.name,
                description=server.description or "",
                transport_type=server.transport_type,
                status=server.status,
                url=server.url,
                command=server.command,
                tools_count=server.tools_count,
                resources_count=server.resources_count,
                prompts_count=server.prompts_count,
                last_connected=server.last_connected.isoformat() if server.last_connected else None,
                last_error=server.last_error,
                created_at=server.created_at.isoformat()
            )
            for server in servers
        ]
        
    except Exception as e:
        logger.error(f"Error listing MCP servers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{server_id}", response_model=MCPServerResponse)
async def get_mcp_server(
    server_id: str,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific MCP server.
    """
    server = db.query(MCPServer).filter(MCPServer.server_id == server_id).first()
    
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    return MCPServerResponse(
        server_id=server.server_id,
        name=server.name,
        description=server.description or "",
        transport_type=server.transport_type,
        status=server.status,
        url=server.url,
        command=server.command,
        tools_count=server.tools_count,
        resources_count=server.resources_count,
        prompts_count=server.prompts_count,
        last_connected=server.last_connected.isoformat() if server.last_connected else None,
        last_error=server.last_error,
        created_at=server.created_at.isoformat()
    )


@router.put("/{server_id}", response_model=MCPServerResponse)
async def update_mcp_server(
    server_id: str,
    server_data: MCPServerUpdate,
    db: Session = Depends(get_db)
):
    """
    Update MCP server configuration.
    """
    server = db.query(MCPServer).filter(MCPServer.server_id == server_id).first()
    
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    try:
        # Update fields
        if server_data.name is not None:
            server.name = server_data.name
        if server_data.description is not None:
            server.description = server_data.description
        if server_data.url is not None:
            server.url = server_data.url
        if server_data.headers is not None:
            server.headers = server_data.headers
        if server_data.auth_type is not None:
            server.auth_type = server_data.auth_type
        if server_data.auth_token is not None:
            server.auth_token = server_data.auth_token
        if server_data.command is not None:
            server.command = server_data.command
        if server_data.args is not None:
            server.args = server_data.args
        if server_data.env is not None:
            server.env = server_data.env
        if server_data.cwd is not None:
            server.cwd = server_data.cwd
        
        server.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(server)
        
        # Update in FastMCP manager
        config = MCPServerConfig(
            server_id=server.server_id,
            name=server.name,
            description=server.description or "",
            transport_type=server.transport_type,
            url=server.url,
            headers=server.headers or {},
            auth_type=server.auth_type,
            auth_token=server.auth_token,
            command=server.command,
            args=server.args or [],
            env=server.env or {},
            cwd=server.cwd
        )
        
        await fastmcp_manager.register_server(config)
        
        logger.info(f"Updated MCP server: {server_id}")
        
        return MCPServerResponse(
            server_id=server.server_id,
            name=server.name,
            description=server.description or "",
            transport_type=server.transport_type,
            status=server.status,
            url=server.url,
            command=server.command,
            tools_count=server.tools_count,
            resources_count=server.resources_count,
            prompts_count=server.prompts_count,
            last_connected=server.last_connected.isoformat() if server.last_connected else None,
            last_error=server.last_error,
            created_at=server.created_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error updating MCP server: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcp_server(
    server_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete an MCP server.
    """
    server = db.query(MCPServer).filter(MCPServer.server_id == server_id).first()
    
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    try:
        # Disconnect from FastMCP manager
        await fastmcp_manager.disconnect_server(server_id)
        
        # Delete from database
        db.delete(server)
        db.commit()
        
        logger.info(f"Deleted MCP server: {server_id}")
        
    except Exception as e:
        logger.error(f"Error deleting MCP server: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{server_id}/connect")
async def connect_mcp_server(
    server_id: str,
    db: Session = Depends(get_db)
):
    """
    Connect to an MCP server and discover its capabilities.
    """
    server = db.query(MCPServer).filter(MCPServer.server_id == server_id).first()
    
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    try:
        # Ensure the server is registered with FastMCP manager before connecting.
        # This is important after backend restarts where the in-memory FastMCP
        # manager state is empty but the database still has MCP server records.
        config = MCPServerConfig(
            server_id=server.server_id,
            name=server.name,
            description=server.description or "",
            transport_type=server.transport_type,
            url=server.url,
            headers=server.headers or {},
            auth_type=server.auth_type,
            auth_token=server.auth_token,
            command=server.command,
            args=server.args or [],
            env=server.env or {},
            cwd=server.cwd
        )
        await fastmcp_manager.register_server(config)
        
        # Attempt connection
        success = await fastmcp_manager.connect_server(server_id)
        
        if success:
            # Update database with status from manager
            status_info = await fastmcp_manager.get_server_status(server_id)
            
            server.status = "active"
            server.last_connected = datetime.now(timezone.utc)
            server.last_error = None
            server.tools_count = status_info.get("tools_count", 0)
            server.resources_count = status_info.get("resources_count", 0)
            server.prompts_count = status_info.get("prompts_count", 0)
            
            db.commit()
            
            return {
                "status": "connected",
                "server_id": server_id,
                "tools_count": server.tools_count,
                "resources_count": server.resources_count,
                "prompts_count": server.prompts_count
            }
        else:
            # Get error details from manager
            status_info = await fastmcp_manager.get_server_status(server_id)
            error_message = status_info.get("last_error", "Connection failed")
            
            server.status = "error"
            server.last_error = error_message
            db.commit()
            
            raise HTTPException(
                status_code=503,  # Service Unavailable
                detail={
                    "error": "MCP_SERVER_UNAVAILABLE",
                    "message": error_message,
                    "server_id": server_id,
                    "server_name": server.name,
                    "suggestion": "This appears to be a temporary issue with the external MCP service. Please try again in a few minutes."
                }
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        logger.error(f"Error connecting to MCP server {server_id}: {e}")
        error_msg = str(e)
        
        # Provide helpful error message
        if "500" in error_msg or "Internal Server Error" in error_msg:
            detail_msg = "The MCP server is experiencing technical issues (HTTP 500). This is a temporary problem with the service provider."
            suggestion = "Please wait a few minutes and try again. If the issue persists, the service provider may be experiencing extended downtime."
        elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            detail_msg = "Unable to reach the MCP server."
            suggestion = "Please check if the server URL is correct and the service is online."
        else:
            detail_msg = error_msg
            suggestion = "Please check the server configuration and try again."
        
        server.status = "error"
        server.last_error = detail_msg
        db.commit()
        
        raise HTTPException(
            status_code=503,
            detail={
                "error": "MCP_CONNECTION_FAILED",
                "message": detail_msg,
                "server_id": server_id,
                "server_name": server.name,
                "suggestion": suggestion
            }
        )


@router.post("/{server_id}/disconnect")
async def disconnect_mcp_server(
    server_id: str,
    db: Session = Depends(get_db)
):
    """
    Disconnect from an MCP server.
    """
    server = db.query(MCPServer).filter(MCPServer.server_id == server_id).first()
    
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    try:
        await fastmcp_manager.disconnect_server(server_id)
        
        server.status = "inactive"
        db.commit()
        
        return {"status": "disconnected", "server_id": server_id}
        
    except Exception as e:
        logger.error(f"Error disconnecting from MCP server {server_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{server_id}/tools")
async def get_mcp_server_tools(server_id: str, db: Session = Depends(get_db)):
    """
    Get available tools from an MCP server.
    """
    try:
        # Ensure server exists in DB
        server = db.query(MCPServer).filter(MCPServer.server_id == server_id).first()
        if not server:
            raise HTTPException(status_code=404, detail="MCP server not found")

        # Ensure server is registered with FastMCP manager (handles backend restarts)
        if server_id not in fastmcp_manager.servers:
            headers = server.headers
            if isinstance(headers, str) and headers:
                headers = json.loads(headers)
            headers = headers or {}

            args = server.args
            if isinstance(args, str) and args:
                args = json.loads(args)
            args = args or []

            env = server.env
            if isinstance(env, str) and env:
                env = json.loads(env)
            env = env or {}

            config = MCPServerConfig(
                server_id=server.server_id,
                name=server.name,
                description=server.description or "",
                transport_type=server.transport_type,
                url=server.url,
                headers=headers,
                auth_type=server.auth_type,
                auth_token=server.auth_token,
                command=server.command,
                args=args,
                env=env,
                cwd=server.cwd,
                status=server.status
            )
            await fastmcp_manager.register_server(config)

        # Attempt to connect/discover tools if not cached yet
        tools = await fastmcp_manager.get_tools(server_id)
        if not tools:
            logger.info(f"Tools not cached for {server_id}. Triggering reconnection.")
            await fastmcp_manager.connect_server(server_id)
            tools = await fastmcp_manager.get_tools(server_id)

        return {"server_id": server_id, "tools": tools, "count": len(tools)}
    except Exception as e:
        logger.error(f"Error getting tools from MCP server {server_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{server_id}/tools/{tool_name}/call")
async def call_mcp_tool(
    server_id: str,
    tool_name: str,
    arguments: Dict[str, Any]
):
    """
    Execute a tool on an MCP server.
    """
    try:
        result = await fastmcp_manager.call_tool(server_id, tool_name, arguments)
        return {"server_id": server_id, "tool_name": tool_name, "result": result}
    except Exception as e:
        logger.error(f"Error calling tool {tool_name} on MCP server {server_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{server_id}/resources")
async def get_mcp_server_resources(server_id: str):
    """
    Get available resources from an MCP server.
    """
    try:
        resources = await fastmcp_manager.get_resources(server_id)
        return {"server_id": server_id, "resources": resources, "count": len(resources)}
    except Exception as e:
        logger.error(f"Error getting resources from MCP server {server_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{server_id}/resources/{uri:path}")
async def read_mcp_resource(server_id: str, uri: str):
    """
    Read a resource from an MCP server.
    """
    try:
        content = await fastmcp_manager.read_resource(server_id, uri)
        return {"server_id": server_id, "uri": uri, "content": content}
    except Exception as e:
        logger.error(f"Error reading resource {uri} from MCP server {server_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{server_id}/prompts")
async def get_mcp_server_prompts(server_id: str):
    """
    Get available prompts from an MCP server.
    """
    try:
        prompts = await fastmcp_manager.get_prompts(server_id)
        return {"server_id": server_id, "prompts": prompts, "count": len(prompts)}
    except Exception as e:
        logger.error(f"Error getting prompts from MCP server {server_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{server_id}/health")
async def check_mcp_server_health(
    server_id: str,
    db: Session = Depends(get_db)
):
    """
    Check health status of an MCP server.
    """
    server = db.query(MCPServer).filter(MCPServer.server_id == server_id).first()
    
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    try:
        is_healthy = await fastmcp_manager.health_check(server_id)
        
        if is_healthy:
            server.status = "active"
            server.last_error = None
        else:
            server.status = "error"
        
        db.commit()
        
        return {
            "server_id": server_id,
            "healthy": is_healthy,
            "status": server.status,
            "last_error": server.last_error
        }
        
    except Exception as e:
        logger.error(f"Error checking health of MCP server {server_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

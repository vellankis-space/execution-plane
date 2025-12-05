import asyncio
import logging
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.mcp_server import MCPServer
from services.fastmcp_manager import FastMCPManager, MCPServerConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reproduce():
    db = SessionLocal()
    try:
        # Get Browser Use server
        server_id = "mcp_5cad0256b861"
        server = db.query(MCPServer).filter(MCPServer.server_id == server_id).first()
        
        if not server:
            logger.error(f"Server {server_id} not found")
            return

        logger.info(f"Found server: {server.name}")
        logger.info(f"Transport: {server.transport_type}")
        logger.info(f"URL: {server.url}")
        logger.info(f"Auth Token: {server.auth_token}")

        # Create config
        config = MCPServerConfig(
            server_id=server.server_id,
            name=server.name,
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



        manager = FastMCPManager()
        await manager.register_server(config)
        
        logger.info("Connecting...")
        connected = await manager.connect_server(server_id)
        if not connected:
            logger.error("Failed to connect")
            return
            
        logger.info("Connected. Calling tool...")
        try:
            # Try to call browser_task with a simple task
            result = await manager.call_tool(
                server_id, 
                "browser_task", 
                {"task": "Search Google for 'test'"}
            )
            logger.info(f"Result: {result}")
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            if hasattr(e, 'response'):
                try:
                    # Try to read content if it's an httpx response
                    if hasattr(e.response, 'read'):
                        content = e.response.read()
                        logger.error(f"Response content: {content.decode('utf-8', errors='replace')}")
                    elif hasattr(e.response, 'content'):
                        logger.error(f"Response content: {e.response.content.decode('utf-8', errors='replace')}")
                except Exception as read_err:
                    logger.error(f"Could not read response: {read_err}")
            
            import traceback
            traceback.print_exc()
            
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(reproduce())

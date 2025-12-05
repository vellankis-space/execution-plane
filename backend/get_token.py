import sys
import os
sys.path.append(os.getcwd())
from core.database import SessionLocal
from models.mcp_server import MCPServer

db = SessionLocal()
server = db.query(MCPServer).filter(MCPServer.server_id == "mcp_5cad0256b861").first()
if server:
    print(f"TOKEN:{server.auth_token}")
else:
    print("Server not found")
db.close()

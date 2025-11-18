"""
MCP Server Models
Database models for storing MCP server configurations
"""
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class MCPServer(Base):
    """MCP Server Configuration Model"""
    __tablename__ = "mcp_servers"
    
    server_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Transport configuration
    transport_type = Column(String, nullable=False)  # http, sse, stdio
    
    # HTTP/SSE config (JSON encoded)
    url = Column(String, nullable=True)
    headers = Column(JSON, nullable=True)
    auth_type = Column(String, nullable=True)
    auth_token = Column(String, nullable=True)  # Encrypted in practice
    
    # STDIO config (JSON encoded)
    command = Column(String, nullable=True)
    args = Column(JSON, nullable=True)
    env = Column(JSON, nullable=True)
    cwd = Column(String, nullable=True)
    
    # Status tracking
    status = Column(String, default="inactive")  # inactive, active, error, connecting
    last_error = Column(Text, nullable=True)
    last_connected = Column(DateTime, nullable=True)
    
    # Capabilities
    tools_count = Column(Integer, default=0)
    resources_count = Column(Integer, default=0)
    prompts_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agent_associations = relationship("AgentMCPServer", back_populates="mcp_server", cascade="all, delete-orphan")


# Association table for many-to-many relationship between agents and MCP servers
class AgentMCPServer(Base):
    """Association between Agents and MCP Servers"""
    __tablename__ = "agent_mcp_servers"
    
    agent_id = Column(String, ForeignKey("agents.agent_id", ondelete="CASCADE"), primary_key=True)
    server_id = Column(String, ForeignKey("mcp_servers.server_id", ondelete="CASCADE"), primary_key=True)
    
    # Configuration specific to this agent-server relationship
    enabled = Column(String, default="true")  # SQLite doesn't have boolean
    priority = Column(Integer, default=0)  # For ordering multiple servers
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="mcp_server_associations")
    mcp_server = relationship("MCPServer", back_populates="agent_associations")

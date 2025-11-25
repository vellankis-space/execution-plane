-- Migration: Add selected_tools column to agent_mcp_servers table
-- This allows users to select specific tools from an MCP server instead of loading all tools

-- Add the column (SQLite compatible)
ALTER TABLE agent_mcp_servers ADD COLUMN selected_tools TEXT;

-- Note: In SQLite, JSON columns are stored as TEXT
-- NULL value means "all tools" - this is the default for existing associations

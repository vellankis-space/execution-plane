"""add selected_tools to agent_mcp_servers

Revision ID: add_selected_tools
Revises: add_triggers_to_workflows
Create Date: 2025-11-19 16:58:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = 'add_selected_tools'
down_revision = 'add_triggers_to_workflows'
branch_labels = None
depends_on = None


def upgrade():
    # Add selected_tools column to agent_mcp_servers table
    # This allows users to select specific tools from an MCP server instead of loading all tools
    op.add_column('agent_mcp_servers', sa.Column('selected_tools', JSON, nullable=True))
    
    # Null value means "all tools" - this is the default for existing associations


def downgrade():
    # Remove selected_tools column from agent_mcp_servers table
    op.drop_column('agent_mcp_servers', 'selected_tools')

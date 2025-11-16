"""add triggers column to workflows

Revision ID: add_triggers_to_workflows
Revises: 
Create Date: 2024-11-14 12:31:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = 'add_triggers_to_workflows'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add triggers column to workflows table
    op.add_column('workflows', sa.Column('triggers', JSON, nullable=True))
    
    # Set default empty array for existing workflows
    op.execute("UPDATE workflows SET triggers = '[]' WHERE triggers IS NULL")


def downgrade():
    # Remove triggers column from workflows table
    op.drop_column('workflows', 'triggers')

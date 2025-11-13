"""
Migration: Add tenant_id to agents and workflows for multi-tenancy isolation
"""
import sqlite3
import os
from pathlib import Path

def migrate():
    """Add tenant_id columns to agents and workflows tables"""
    # Get database path from environment or use default
    db_path = os.getenv("DATABASE_URL", "sqlite:///agents.db")
    
    # Extract path for SQLite
    if db_path.startswith("sqlite:///"):
        db_file = db_path.replace("sqlite:///", "")
    else:
        print("This migration is for SQLite. For PostgreSQL, use Alembic migrations.")
        return
    
    if not os.path.exists(db_file):
        print(f"Database file not found: {db_file}")
        return
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        # Check if tenant_id column exists in agents table
        cursor.execute("PRAGMA table_info(agents)")
        agent_columns = [row[1] for row in cursor.fetchall()]
        
        if "tenant_id" not in agent_columns:
            print("Adding tenant_id column to agents table...")
            cursor.execute("ALTER TABLE agents ADD COLUMN tenant_id VARCHAR")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_agents_tenant_id ON agents(tenant_id)")
            print("✓ Added tenant_id to agents table")
        else:
            print("✓ tenant_id already exists in agents table")
        
        # Check if tenant_id column exists in workflows table
        cursor.execute("PRAGMA table_info(workflows)")
        workflow_columns = [row[1] for row in cursor.fetchall()]
        
        if "tenant_id" not in workflow_columns:
            print("Adding tenant_id column to workflows table...")
            cursor.execute("ALTER TABLE workflows ADD COLUMN tenant_id VARCHAR")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflows_tenant_id ON workflows(tenant_id)")
            print("✓ Added tenant_id to workflows table")
        else:
            print("✓ tenant_id already exists in workflows table")
        
        # Check if tenant_id column exists in workflow_executions table
        cursor.execute("PRAGMA table_info(workflow_executions)")
        execution_columns = [row[1] for row in cursor.fetchall()]
        
        if "tenant_id" not in execution_columns:
            print("Adding tenant_id column to workflow_executions table...")
            cursor.execute("ALTER TABLE workflow_executions ADD COLUMN tenant_id VARCHAR")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_executions_tenant_id ON workflow_executions(tenant_id)")
            print("✓ Added tenant_id to workflow_executions table")
        else:
            print("✓ tenant_id already exists in workflow_executions table")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()


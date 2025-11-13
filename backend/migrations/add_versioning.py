"""
Migration script to add versioning support for agents and workflows
"""
from sqlalchemy import text
from core.database import engine

def add_versioning_support():
    """Add versioning columns and tables"""
    with engine.connect() as conn:
        # Add version column to agents table
        try:
            conn.execute(text("ALTER TABLE agents ADD COLUMN version INTEGER DEFAULT 1"))
            print("Added version column to agents table")
        except Exception as e:
            print(f"Version column may already exist in agents: {e}")
        
        # Add version column to workflows table
        try:
            conn.execute(text("ALTER TABLE workflows ADD COLUMN version INTEGER DEFAULT 1"))
            print("Added version column to workflows table")
        except Exception as e:
            print(f"Version column may already exist in workflows: {e}")
        
        # Create agent_versions table
        try:
            conn.execute(text("""
                CREATE TABLE agent_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id VARCHAR NOT NULL,
                    version INTEGER NOT NULL,
                    config_snapshot JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR,
                    UNIQUE(agent_id, version)
                )
            """))
            print("Created agent_versions table")
        except Exception as e:
            print(f"agent_versions table may already exist: {e}")
        
        # Create workflow_versions table
        try:
            conn.execute(text("""
                CREATE TABLE workflow_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id VARCHAR NOT NULL,
                    version INTEGER NOT NULL,
                    definition_snapshot JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR,
                    UNIQUE(workflow_id, version)
                )
            """))
            print("Created workflow_versions table")
        except Exception as e:
            print(f"workflow_versions table may already exist: {e}")
        
        # Create indexes
        try:
            conn.execute(text("CREATE INDEX idx_agent_versions_agent_id ON agent_versions(agent_id)"))
            conn.execute(text("CREATE INDEX idx_workflow_versions_workflow_id ON workflow_versions(workflow_id)"))
            print("Created indexes for versioning tables")
        except Exception as e:
            print(f"Indexes may already exist: {e}")
        
        conn.commit()
        print("Versioning support added successfully!")

if __name__ == "__main__":
    add_versioning_support()


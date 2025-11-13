"""
Migration script to add human-in-the-loop support
"""
from sqlalchemy import text
from core.database import engine

def add_human_in_loop_support():
    """Add human-in-the-loop tables"""
    with engine.connect() as conn:
        # Create approval_gates table
        try:
            conn.execute(text("""
                CREATE TABLE approval_gates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gate_id VARCHAR UNIQUE NOT NULL,
                    workflow_id VARCHAR NOT NULL,
                    step_id VARCHAR,
                    name VARCHAR NOT NULL,
                    description TEXT,
                    approver_type VARCHAR NOT NULL,
                    approver_ids JSON DEFAULT '[]',
                    timeout_seconds INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP,
                    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id)
                )
            """))
            print("Created approval_gates table")
        except Exception as e:
            print(f"approval_gates table may already exist: {e}")
        
        # Create human_tasks table
        try:
            conn.execute(text("""
                CREATE TABLE human_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id VARCHAR UNIQUE NOT NULL,
                    gate_id VARCHAR NOT NULL,
                    workflow_id VARCHAR NOT NULL,
                    execution_id VARCHAR NOT NULL,
                    step_id VARCHAR,
                    task_type VARCHAR NOT NULL,
                    title VARCHAR NOT NULL,
                    description TEXT,
                    assigned_to VARCHAR,
                    status VARCHAR DEFAULT 'pending',
                    input_data JSON DEFAULT '{}',
                    response_data JSON,
                    response_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    assigned_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    metadata JSON DEFAULT '{}',
                    FOREIGN KEY (gate_id) REFERENCES approval_gates(gate_id)
                )
            """))
            print("Created human_tasks table")
        except Exception as e:
            print(f"human_tasks table may already exist: {e}")
        
        # Create indexes
        try:
            conn.execute(text("CREATE INDEX idx_approval_gates_workflow_id ON approval_gates(workflow_id)"))
            conn.execute(text("CREATE INDEX idx_human_tasks_task_id ON human_tasks(task_id)"))
            conn.execute(text("CREATE INDEX idx_human_tasks_assigned_to ON human_tasks(assigned_to)"))
            conn.execute(text("CREATE INDEX idx_human_tasks_execution_id ON human_tasks(execution_id)"))
            conn.execute(text("CREATE INDEX idx_human_tasks_status ON human_tasks(status)"))
            conn.execute(text("CREATE INDEX idx_human_tasks_created_at ON human_tasks(created_at)"))
            conn.execute(text("CREATE INDEX idx_human_tasks_status_assigned ON human_tasks(status, assigned_to, created_at)"))
            print("Created indexes for human-in-the-loop tables")
        except Exception as e:
            print(f"Indexes may already exist: {e}")
        
        conn.commit()
        print("Human-in-the-loop support added successfully!")

if __name__ == "__main__":
    add_human_in_loop_support()


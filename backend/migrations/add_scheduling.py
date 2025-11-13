"""
Migration script to add workflow scheduling support
"""
from sqlalchemy import text
from core.database import engine

def add_scheduling_support():
    """Add scheduling tables"""
    with engine.connect() as conn:
        # Create workflow_schedules table
        try:
            conn.execute(text("""
                CREATE TABLE workflow_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schedule_id VARCHAR UNIQUE NOT NULL,
                    workflow_id VARCHAR NOT NULL,
                    name VARCHAR NOT NULL,
                    description TEXT,
                    cron_expression VARCHAR NOT NULL,
                    timezone VARCHAR DEFAULT 'UTC',
                    is_active BOOLEAN DEFAULT 1,
                    input_data JSON DEFAULT '{}',
                    created_by VARCHAR,
                    next_run_at TIMESTAMP,
                    last_run_at TIMESTAMP,
                    last_run_status VARCHAR,
                    run_count INTEGER DEFAULT 0,
                    max_runs INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP,
                    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id)
                )
            """))
            print("Created workflow_schedules table")
        except Exception as e:
            print(f"workflow_schedules table may already exist: {e}")
        
        # Create scheduled_executions table
        try:
            conn.execute(text("""
                CREATE TABLE scheduled_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id VARCHAR UNIQUE NOT NULL,
                    schedule_id VARCHAR NOT NULL,
                    workflow_id VARCHAR NOT NULL,
                    workflow_execution_id VARCHAR,
                    scheduled_at TIMESTAMP NOT NULL,
                    executed_at TIMESTAMP,
                    status VARCHAR DEFAULT 'pending',
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (schedule_id) REFERENCES workflow_schedules(schedule_id)
                )
            """))
            print("Created scheduled_executions table")
        except Exception as e:
            print(f"scheduled_executions table may already exist: {e}")
        
        # Create indexes
        try:
            conn.execute(text("CREATE INDEX idx_workflow_schedules_workflow_id ON workflow_schedules(workflow_id)"))
            conn.execute(text("CREATE INDEX idx_workflow_schedules_is_active ON workflow_schedules(is_active)"))
            conn.execute(text("CREATE INDEX idx_workflow_schedules_next_run_at ON workflow_schedules(next_run_at)"))
            conn.execute(text("CREATE INDEX idx_scheduled_executions_schedule_id ON scheduled_executions(schedule_id)"))
            conn.execute(text("CREATE INDEX idx_scheduled_executions_status ON scheduled_executions(status)"))
            print("Created indexes for scheduling tables")
        except Exception as e:
            print(f"Indexes may already exist: {e}")
        
        conn.commit()
        print("Scheduling support added successfully!")

if __name__ == "__main__":
    add_scheduling_support()


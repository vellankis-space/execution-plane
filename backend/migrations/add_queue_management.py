"""
Migration script to add queue management support
"""
from sqlalchemy import text
from core.database import engine

def add_queue_management_support():
    """Add queue management tables"""
    with engine.connect() as conn:
        # Create workflow_queues table
        try:
            conn.execute(text("""
                CREATE TABLE workflow_queues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    queue_id VARCHAR UNIQUE NOT NULL,
                    name VARCHAR UNIQUE NOT NULL,
                    description TEXT,
                    priority_levels INTEGER DEFAULT 5,
                    max_concurrent_executions INTEGER DEFAULT 10,
                    is_active BOOLEAN DEFAULT 1,
                    settings JSON DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """))
            print("Created workflow_queues table")
        except Exception as e:
            print(f"workflow_queues table may already exist: {e}")
        
        # Create queued_executions table
        try:
            conn.execute(text("""
                CREATE TABLE queued_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    queue_item_id VARCHAR UNIQUE NOT NULL,
                    queue_id VARCHAR NOT NULL,
                    workflow_id VARCHAR NOT NULL,
                    execution_id VARCHAR UNIQUE NOT NULL,
                    priority INTEGER DEFAULT 3,
                    status VARCHAR DEFAULT 'pending',
                    input_data JSON DEFAULT '{}',
                    scheduled_at TIMESTAMP,
                    queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    metadata JSON DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (queue_id) REFERENCES workflow_queues(queue_id)
                )
            """))
            print("Created queued_executions table")
        except Exception as e:
            print(f"queued_executions table may already exist: {e}")
        
        # Create indexes
        try:
            conn.execute(text("CREATE INDEX idx_workflow_queues_name ON workflow_queues(name)"))
            conn.execute(text("CREATE INDEX idx_queued_executions_queue_id ON queued_executions(queue_id)"))
            conn.execute(text("CREATE INDEX idx_queued_executions_execution_id ON queued_executions(execution_id)"))
            conn.execute(text("CREATE INDEX idx_queued_executions_status ON queued_executions(status)"))
            conn.execute(text("CREATE INDEX idx_queue_priority_status ON queued_executions(queue_id, priority, status, queued_at)"))
            print("Created indexes for queue management tables")
        except Exception as e:
            print(f"Indexes may already exist: {e}")
        
        conn.commit()
        print("Queue management support added successfully!")

if __name__ == "__main__":
    add_queue_management_support()


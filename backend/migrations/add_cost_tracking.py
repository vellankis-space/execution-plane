"""
Migration script to add cost tracking support
"""
from sqlalchemy import text
from core.database import engine

def add_cost_tracking_support():
    """Add cost tracking tables"""
    with engine.connect() as conn:
        # Create api_calls table
        try:
            conn.execute(text("""
                CREATE TABLE api_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    call_id VARCHAR UNIQUE NOT NULL,
                    agent_id VARCHAR,
                    workflow_id VARCHAR,
                    execution_id VARCHAR,
                    provider VARCHAR NOT NULL,
                    model VARCHAR NOT NULL,
                    call_type VARCHAR,
                    input_tokens INTEGER DEFAULT 0,
                    output_tokens INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    cost REAL DEFAULT 0.0,
                    metadata JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("Created api_calls table")
        except Exception as e:
            print(f"api_calls table may already exist: {e}")
        
        # Create cost_budgets table
        try:
            conn.execute(text("""
                CREATE TABLE cost_budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    budget_id VARCHAR UNIQUE NOT NULL,
                    name VARCHAR NOT NULL,
                    description TEXT,
                    budget_type VARCHAR NOT NULL,
                    amount REAL NOT NULL,
                    period_start TIMESTAMP,
                    period_end TIMESTAMP,
                    alert_threshold REAL DEFAULT 0.8,
                    enabled BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """))
            print("Created cost_budgets table")
        except Exception as e:
            print(f"cost_budgets table may already exist: {e}")
        
        # Create cost_alerts table
        try:
            conn.execute(text("""
                CREATE TABLE cost_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id VARCHAR UNIQUE NOT NULL,
                    budget_id VARCHAR NOT NULL,
                    alert_type VARCHAR NOT NULL,
                    message TEXT NOT NULL,
                    current_cost REAL NOT NULL,
                    budget_amount REAL NOT NULL,
                    percentage_used REAL NOT NULL,
                    status VARCHAR DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("Created cost_alerts table")
        except Exception as e:
            print(f"cost_alerts table may already exist: {e}")
        
        # Create indexes
        try:
            conn.execute(text("CREATE INDEX idx_api_calls_agent_id ON api_calls(agent_id)"))
            conn.execute(text("CREATE INDEX idx_api_calls_workflow_id ON api_calls(workflow_id)"))
            conn.execute(text("CREATE INDEX idx_api_calls_execution_id ON api_calls(execution_id)"))
            conn.execute(text("CREATE INDEX idx_api_calls_provider ON api_calls(provider)"))
            conn.execute(text("CREATE INDEX idx_api_calls_created_at ON api_calls(created_at)"))
            conn.execute(text("CREATE INDEX idx_cost_budgets_enabled ON cost_budgets(enabled)"))
            conn.execute(text("CREATE INDEX idx_cost_alerts_budget_id ON cost_alerts(budget_id)"))
            conn.execute(text("CREATE INDEX idx_cost_alerts_status ON cost_alerts(status)"))
            print("Created indexes for cost tracking tables")
        except Exception as e:
            print(f"Indexes may already exist: {e}")
        
        conn.commit()
        print("Cost tracking support added successfully!")

if __name__ == "__main__":
    add_cost_tracking_support()


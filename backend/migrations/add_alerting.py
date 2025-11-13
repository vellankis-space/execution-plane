"""
Migration script to add alerting support
"""
from sqlalchemy import text
from core.database import engine

def add_alerting_support():
    """Add alerting tables"""
    with engine.connect() as conn:
        # Create alert_rules table
        try:
            conn.execute(text("""
                CREATE TABLE alert_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_id VARCHAR UNIQUE NOT NULL,
                    name VARCHAR NOT NULL,
                    description TEXT,
                    workflow_id VARCHAR,
                    condition_type VARCHAR NOT NULL,
                    condition_config JSON NOT NULL,
                    notification_channels JSON NOT NULL,
                    enabled BOOLEAN DEFAULT 1,
                    severity VARCHAR DEFAULT 'medium',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """))
            print("Created alert_rules table")
        except Exception as e:
            print(f"alert_rules table may already exist: {e}")
        
        # Create alerts table
        try:
            conn.execute(text("""
                CREATE TABLE alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id VARCHAR UNIQUE NOT NULL,
                    rule_id VARCHAR NOT NULL,
                    workflow_id VARCHAR,
                    execution_id VARCHAR,
                    severity VARCHAR NOT NULL,
                    message TEXT NOT NULL,
                    details JSON,
                    status VARCHAR DEFAULT 'active',
                    acknowledged_by VARCHAR,
                    acknowledged_at TIMESTAMP,
                    resolved_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("Created alerts table")
        except Exception as e:
            print(f"alerts table may already exist: {e}")
        
        # Create notification_channels table
        try:
            conn.execute(text("""
                CREATE TABLE notification_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id VARCHAR UNIQUE NOT NULL,
                    name VARCHAR NOT NULL,
                    channel_type VARCHAR NOT NULL,
                    config JSON NOT NULL,
                    enabled BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """))
            print("Created notification_channels table")
        except Exception as e:
            print(f"notification_channels table may already exist: {e}")
        
        # Create indexes
        try:
            conn.execute(text("CREATE INDEX idx_alert_rules_workflow_id ON alert_rules(workflow_id)"))
            conn.execute(text("CREATE INDEX idx_alert_rules_enabled ON alert_rules(enabled)"))
            conn.execute(text("CREATE INDEX idx_alerts_rule_id ON alerts(rule_id)"))
            conn.execute(text("CREATE INDEX idx_alerts_workflow_id ON alerts(workflow_id)"))
            conn.execute(text("CREATE INDEX idx_alerts_status ON alerts(status)"))
            conn.execute(text("CREATE INDEX idx_alerts_severity ON alerts(severity)"))
            print("Created indexes for alerting tables")
        except Exception as e:
            print(f"Indexes may already exist: {e}")
        
        conn.commit()
        print("Alerting support added successfully!")

if __name__ == "__main__":
    add_alerting_support()


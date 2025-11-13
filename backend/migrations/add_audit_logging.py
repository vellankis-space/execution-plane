"""
Migration script to add audit logging support
"""
from sqlalchemy import text
from core.database import engine

def add_audit_logging_support():
    """Add audit logging tables"""
    with engine.connect() as conn:
        # Create audit_logs table
        try:
            conn.execute(text("""
                CREATE TABLE audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_id VARCHAR UNIQUE NOT NULL,
                    user_id VARCHAR,
                    action VARCHAR NOT NULL,
                    resource_type VARCHAR NOT NULL,
                    resource_id VARCHAR,
                    resource_name VARCHAR,
                    tenant_id VARCHAR,
                    ip_address VARCHAR,
                    user_agent VARCHAR,
                    request_method VARCHAR,
                    request_path VARCHAR,
                    status_code INTEGER,
                    success INTEGER DEFAULT 1,
                    error_message TEXT,
                    changes JSON DEFAULT '{}',
                    metadata JSON DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("Created audit_logs table")
        except Exception as e:
            print(f"audit_logs table may already exist: {e}")
        
        # Create indexes
        try:
            conn.execute(text("CREATE INDEX idx_audit_logs_log_id ON audit_logs(log_id)"))
            conn.execute(text("CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id)"))
            conn.execute(text("CREATE INDEX idx_audit_logs_action ON audit_logs(action)"))
            conn.execute(text("CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type)"))
            conn.execute(text("CREATE INDEX idx_audit_logs_resource_id ON audit_logs(resource_id)"))
            conn.execute(text("CREATE INDEX idx_audit_logs_tenant_id ON audit_logs(tenant_id)"))
            conn.execute(text("CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at)"))
            conn.execute(text("CREATE INDEX idx_audit_user_action ON audit_logs(user_id, action)"))
            conn.execute(text("CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id)"))
            conn.execute(text("CREATE INDEX idx_audit_tenant_time ON audit_logs(tenant_id, created_at)"))
            print("Created indexes for audit_logs table")
        except Exception as e:
            print(f"Indexes may already exist: {e}")
        
        conn.commit()
        print("Audit logging support added successfully!")

if __name__ == "__main__":
    add_audit_logging_support()


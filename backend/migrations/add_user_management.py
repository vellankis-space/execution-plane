"""
Migration script to add user management and RBAC support
"""
from sqlalchemy import text
from core.database import engine

def add_user_management_support():
    """Add user management and RBAC tables"""
    with engine.connect() as conn:
        # Create users table
        try:
            conn.execute(text("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id VARCHAR UNIQUE NOT NULL,
                    email VARCHAR UNIQUE NOT NULL,
                    username VARCHAR UNIQUE NOT NULL,
                    hashed_password VARCHAR NOT NULL,
                    full_name VARCHAR,
                    is_active BOOLEAN DEFAULT 1,
                    is_superuser BOOLEAN DEFAULT 0,
                    tenant_id VARCHAR,
                    roles JSON DEFAULT '[]',
                    permissions JSON DEFAULT '[]',
                    metadata JSON DEFAULT '{}',
                    last_login TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """))
            print("Created users table")
        except Exception as e:
            print(f"users table may already exist: {e}")
        
        # Create user_sessions table
        try:
            conn.execute(text("""
                CREATE TABLE user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id VARCHAR UNIQUE NOT NULL,
                    user_id VARCHAR NOT NULL,
                    token VARCHAR UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    ip_address VARCHAR,
                    user_agent VARCHAR,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """))
            print("Created user_sessions table")
        except Exception as e:
            print(f"user_sessions table may already exist: {e}")
        
        # Create roles table
        try:
            conn.execute(text("""
                CREATE TABLE roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role_id VARCHAR UNIQUE NOT NULL,
                    name VARCHAR UNIQUE NOT NULL,
                    description TEXT,
                    permissions JSON NOT NULL,
                    is_system_role BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """))
            print("Created roles table")
        except Exception as e:
            print(f"roles table may already exist: {e}")
        
        # Create tenants table
        try:
            conn.execute(text("""
                CREATE TABLE tenants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id VARCHAR UNIQUE NOT NULL,
                    name VARCHAR NOT NULL,
                    domain VARCHAR UNIQUE,
                    is_active BOOLEAN DEFAULT 1,
                    settings JSON DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """))
            print("Created tenants table")
        except Exception as e:
            print(f"tenants table may already exist: {e}")
        
        # Create indexes
        try:
            conn.execute(text("CREATE INDEX idx_users_email ON users(email)"))
            conn.execute(text("CREATE INDEX idx_users_username ON users(username)"))
            conn.execute(text("CREATE INDEX idx_users_tenant_id ON users(tenant_id)"))
            conn.execute(text("CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id)"))
            conn.execute(text("CREATE INDEX idx_user_sessions_token ON user_sessions(token)"))
            conn.execute(text("CREATE INDEX idx_roles_name ON roles(name)"))
            conn.execute(text("CREATE INDEX idx_tenants_domain ON tenants(domain)"))
            print("Created indexes for user management tables")
        except Exception as e:
            print(f"Indexes may already exist: {e}")
        
        # Create default roles (will be created on first run via a separate script)
        print("Default roles should be created separately using the init_roles script")
        
        conn.commit()
        print("User management support added successfully!")

if __name__ == "__main__":
    add_user_management_support()


"""
Migration script to add workflow template support
"""
from sqlalchemy import text
from core.database import engine

def add_template_support():
    """Add template tables"""
    with engine.connect() as conn:
        # Create workflow_templates table
        try:
            conn.execute(text("""
                CREATE TABLE workflow_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id VARCHAR UNIQUE NOT NULL,
                    name VARCHAR NOT NULL,
                    description TEXT,
                    category VARCHAR,
                    tags JSON DEFAULT '[]',
                    workflow_definition JSON NOT NULL,
                    is_public BOOLEAN DEFAULT 0,
                    is_featured BOOLEAN DEFAULT 0,
                    created_by VARCHAR,
                    usage_count INTEGER DEFAULT 0,
                    rating INTEGER,
                    rating_count INTEGER DEFAULT 0,
                    metadata JSON DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """))
            print("Created workflow_templates table")
        except Exception as e:
            print(f"workflow_templates table may already exist: {e}")
        
        # Create template_usage table
        try:
            conn.execute(text("""
                CREATE TABLE template_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usage_id VARCHAR UNIQUE NOT NULL,
                    template_id VARCHAR NOT NULL,
                    user_id VARCHAR,
                    workflow_id VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (template_id) REFERENCES workflow_templates(template_id)
                )
            """))
            print("Created template_usage table")
        except Exception as e:
            print(f"template_usage table may already exist: {e}")
        
        # Create template_ratings table
        try:
            conn.execute(text("""
                CREATE TABLE template_ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rating_id VARCHAR UNIQUE NOT NULL,
                    template_id VARCHAR NOT NULL,
                    user_id VARCHAR NOT NULL,
                    rating INTEGER NOT NULL,
                    review TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP,
                    FOREIGN KEY (template_id) REFERENCES workflow_templates(template_id)
                )
            """))
            print("Created template_ratings table")
        except Exception as e:
            print(f"template_ratings table may already exist: {e}")
        
        # Create indexes
        try:
            conn.execute(text("CREATE INDEX idx_workflow_templates_name ON workflow_templates(name)"))
            conn.execute(text("CREATE INDEX idx_workflow_templates_category ON workflow_templates(category)"))
            conn.execute(text("CREATE INDEX idx_workflow_templates_created_by ON workflow_templates(created_by)"))
            conn.execute(text("CREATE INDEX idx_workflow_templates_created_at ON workflow_templates(created_at)"))
            conn.execute(text("CREATE INDEX idx_template_usage_template_id ON template_usage(template_id)"))
            conn.execute(text("CREATE INDEX idx_template_usage_user_id ON template_usage(user_id)"))
            conn.execute(text("CREATE INDEX idx_template_ratings_template_id ON template_ratings(template_id)"))
            conn.execute(text("CREATE INDEX idx_template_ratings_user_id ON template_ratings(user_id)"))
            print("Created indexes for template tables")
        except Exception as e:
            print(f"Indexes may already exist: {e}")
        
        conn.commit()
        print("Template support added successfully!")

if __name__ == "__main__":
    add_template_support()


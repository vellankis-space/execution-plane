"""
Script to initialize the database tables
"""
from core.database import engine
from models import workflow

if __name__ == "__main__":
    # Create all tables
    workflow.Base.metadata.create_all(engine)
    print("Database tables created successfully!")
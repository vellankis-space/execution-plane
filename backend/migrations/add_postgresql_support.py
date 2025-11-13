"""
Migration helper for PostgreSQL support
This script helps verify PostgreSQL connection and create tables
"""
import os
from sqlalchemy import create_engine, text
from core.config import settings

def verify_postgresql_connection():
    """Verify PostgreSQL connection and create tables if needed"""
    database_url = settings.DATABASE_URL
    
    if not database_url.startswith("postgresql"):
        print("Not using PostgreSQL, skipping verification")
        return
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            # Test connection
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"Connected to PostgreSQL: {version}")
            
            # Create all tables
            from core.database import Base
            from models import (
                agent, knowledge_base, workflow, user, scheduling,
                audit, queue, template, human_in_loop, alerting, cost_tracking
            )
            
            Base.metadata.create_all(bind=engine)
            print("All tables created/verified in PostgreSQL")
            
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        print("Make sure PostgreSQL is running and DATABASE_URL is correct")

if __name__ == "__main__":
    verify_postgresql_connection()


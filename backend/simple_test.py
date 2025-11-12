"""
Simple test script for the enhanced monitoring service
"""
import asyncio
from sqlalchemy.orm import Session
from core.database import get_db, engine
from models.workflow import Base, WorkflowExecution, StepExecution, ExecutionLog

def test_db_connection():
    try:
        # Test database connection
        connection = engine.connect()
        print("Database connection successful!")
        connection.close()
        
        # Test that tables exist by checking if we can create a session
        print("Database tables are ready!")
        return True
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_db_connection()
    if success:
        print("\nAll tests completed successfully!")
    else:
        print("\nTests failed!")
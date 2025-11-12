"""
Test script for the enhanced monitoring service
"""
import asyncio
from sqlalchemy.orm import Session
from core.database import get_db
from services.enhanced_monitoring_service import EnhancedMonitoringService

async def test_enhanced_monitoring():
    # Get database session
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # Create monitoring service
        monitoring_service = EnhancedMonitoringService(db)
        
        # Test getting enhanced workflow metrics
        print("Testing enhanced workflow metrics...")
        workflow_metrics = await monitoring_service.get_enhanced_workflow_metrics()
        print(f"Workflow metrics: {workflow_metrics}")
        
        # Test getting enhanced step metrics
        print("\nTesting enhanced step metrics...")
        step_metrics = await monitoring_service.get_enhanced_step_metrics()
        print(f"Step metrics: {step_metrics}")
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
    finally:
        # Close database session
        db.close()

if __name__ == "__main__":
    asyncio.run(test_enhanced_monitoring())
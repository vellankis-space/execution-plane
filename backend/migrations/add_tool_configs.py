"""
Database Migration: Add Tool Configs Column

This migration adds the tool_configs JSON column to the agents table
to store tool-specific configurations including API keys and settings
for external tools like DuckDuckGo Search, Brave Search, GitHub, etc.

Run with: python migrations/add_tool_configs.py
"""

import sys
import os

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from core.config import settings


def run_migration():
    """Add tool_configs column to agents table"""
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("PRAGMA table_info(agents)"))
            columns = [row[1] for row in result]
            
            if 'tool_configs' in columns:
                print("✓ Column 'tool_configs' already exists in agents table")
                return True
            
            # Add the column
            print("Adding tool_configs column to agents table...")
            conn.execute(text("ALTER TABLE agents ADD COLUMN tool_configs JSON"))
            conn.commit()
            
            print("✓ Successfully added tool_configs column to agents table")
            return True
            
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False


def verify_migration():
    """Verify the migration was successful"""
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(agents)"))
            columns = [row[1] for row in result]
            
            if 'tool_configs' in columns:
                print("✓ Migration verified: tool_configs column exists")
                return True
            else:
                print("✗ Verification failed: tool_configs column not found")
                return False
                
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Tool Configs Migration")
    print("=" * 60)
    
    success = run_migration()
    
    if success:
        verify_migration()
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Migration failed!")
        print("=" * 60)
        sys.exit(1)

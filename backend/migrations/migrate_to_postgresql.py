"""
Migration script to migrate from SQLite to PostgreSQL
"""
import os
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import sql
import json
from datetime import datetime

def migrate_to_postgresql():
    """Migrate data from SQLite to PostgreSQL"""
    
    # Database URLs
    sqlite_db_path = os.getenv("SQLITE_DB_PATH", "agents.db")
    postgres_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/execution_plane")
    
    if not postgres_url.startswith("postgresql://"):
        print("Error: DATABASE_URL must be a PostgreSQL connection string")
        return
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    try:
        postgres_conn = psycopg2.connect(postgres_url)
        postgres_cursor = postgres_conn.cursor()
        print("Connected to PostgreSQL")
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return
    
    # List of tables to migrate
    tables = [
        "agents", "knowledge_bases", "workflows", "workflow_executions",
        "step_executions", "execution_logs", "users", "user_sessions",
        "roles", "tenants", "workflow_schedules", "scheduled_executions",
        "audit_logs", "alert_rules", "alerts", "notification_channels",
        "api_calls", "cost_budgets", "cost_alerts", "workflow_queues",
        "queued_executions", "workflow_templates", "template_usage",
        "template_ratings", "approval_gates", "human_tasks"
    ]
    
    for table_name in tables:
        try:
            # Check if table exists in SQLite
            sqlite_cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            if not sqlite_cursor.fetchone():
                print(f"Skipping {table_name} (doesn't exist in SQLite)")
                continue
            
            print(f"Migrating {table_name}...")
            
            # Get data from SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"  No data in {table_name}")
                continue
            
            # Get column names
            columns = [description[0] for description in sqlite_cursor.description]
            
            # Prepare data for PostgreSQL
            values = []
            for row in rows:
                row_dict = dict(row)
                # Convert JSON strings to dicts
                for key, value in row_dict.items():
                    if isinstance(value, str) and (key.endswith('_config') or key.endswith('_data') or 
                                                   key in ['tools', 'tool_configs', 'pii_config', 'definition',
                                                          'input_data', 'output_data', 'changes', 'metadata',
                                                          'settings', 'roles', 'permissions', 'tags']):
                        try:
                            row_dict[key] = json.loads(value)
                        except:
                            pass
                values.append([row_dict.get(col) for col in columns])
            
            # Insert into PostgreSQL (assuming table already exists)
            if values:
                insert_query = sql.SQL("INSERT INTO {} ({}) VALUES %s ON CONFLICT DO NOTHING").format(
                    sql.Identifier(table_name),
                    sql.SQL(', ').join(map(sql.Identifier, columns))
                )
                
                execute_values(
                    postgres_cursor,
                    insert_query,
                    values,
                    template=None,
                    page_size=100
                )
                
                postgres_conn.commit()
                print(f"  Migrated {len(values)} rows")
            
        except Exception as e:
            print(f"  Error migrating {table_name}: {e}")
            postgres_conn.rollback()
    
    # Close connections
    sqlite_conn.close()
    postgres_conn.close()
    print("Migration completed!")


if __name__ == "__main__":
    migrate_to_postgresql()


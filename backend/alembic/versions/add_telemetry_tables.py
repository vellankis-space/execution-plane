"""Add telemetry tables for traces and spans

Revision ID: add_telemetry_tables
Revises: 
Create Date: 2025-12-01

"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    # Create traces table
    op.execute("""
        CREATE TABLE IF NOT EXISTS traces (
            trace_id TEXT PRIMARY KEY,
            service_name TEXT,
            start_time TEXT,
            end_time TEXT,
            duration_ms INTEGER,
            status TEXT,
            root_span_name TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # Create spans table
    op.execute("""
        CREATE TABLE IF NOT EXISTS spans (
            span_id TEXT PRIMARY KEY,
            trace_id TEXT NOT NULL,
            parent_span_id TEXT,
            name TEXT,
            span_kind TEXT,
            start_time TEXT,
            end_time TEXT,
            duration_us INTEGER,
            status TEXT,
            attributes TEXT,
            events TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (trace_id) REFERENCES traces(trace_id)
        )
    """)
    
    # Create indexes
    op.execute("CREATE INDEX IF NOT EXISTS idx_spans_trace_id ON spans(trace_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_traces_start_time ON traces(start_time DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_spans_name ON spans(name)")


def downgrade():
    op.execute("DROP TABLE IF EXISTS spans")
    op.execute("DROP TABLE IF EXISTS traces")

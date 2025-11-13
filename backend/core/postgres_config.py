"""
PostgreSQL configuration and connection management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Use PostgreSQL if DATABASE_URL is set, otherwise fall back to SQLite
DATABASE_URL = settings.DATABASE_URL

# Create engine with connection pooling for PostgreSQL
if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL connection with pooling
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=False
    )
else:
    # SQLite (development)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


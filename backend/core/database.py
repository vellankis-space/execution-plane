from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from .config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

async def init_db():
    from models import agent, knowledge_base, workflow, user, telemetry
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Add api_key_encrypted column if it doesn't exist (for existing databases)
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("PRAGMA table_info(agents)"))
            columns = [row[1] for row in result]
            
            if 'api_key_encrypted' not in columns:
                # Add the column
                conn.execute(text("ALTER TABLE agents ADD COLUMN api_key_encrypted VARCHAR"))
                conn.commit()
                print("Added api_key_encrypted column to agents table")
    except Exception as e:
        print(f"Warning: Could not add api_key_encrypted column: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
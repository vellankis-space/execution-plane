import asyncio
from core.database import init_db, engine, Base
from models import telemetry

async def create_tables():
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")

if __name__ == "__main__":
    # Sync version for simplicity if async fails
    Base.metadata.create_all(bind=engine)
    print("Tables created (sync).")

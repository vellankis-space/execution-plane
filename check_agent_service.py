import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.agent_service import AgentService
from core.database import SessionLocal
import asyncio

async def test():
    db = SessionLocal()
    service = AgentService(db)
    print('Agent service initialized successfully')
    db.close()

if __name__ == "__main__":
    asyncio.run(test())
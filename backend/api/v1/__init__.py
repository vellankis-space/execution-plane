from fastapi import APIRouter
from . import agents, knowledge_base, workflows, monitoring, enhanced_monitoring

router = APIRouter()
router.include_router(agents.router, prefix="/agents", tags=["agents"])
router.include_router(knowledge_base.router, prefix="/knowledge-bases", tags=["knowledge-bases"])
router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
router.include_router(enhanced_monitoring.router, prefix="/enhanced-monitoring", tags=["enhanced-monitoring"])
from fastapi import APIRouter
from . import agents, knowledge_base, workflows, versioning, auth, scheduling, audit, queue, templates, human_in_loop, a2a, mcp, credentials, webhooks, models, mcp_servers, dashboard, observability, telemetry

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(models.router, prefix="/models", tags=["models"])
router.include_router(agents.router, prefix="/agents", tags=["agents"])
router.include_router(mcp_servers.router, prefix="/mcp-servers", tags=["mcp-servers"])
router.include_router(knowledge_base.router, prefix="/knowledge-bases", tags=["knowledge-bases"])
router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
router.include_router(credentials.router, prefix="/credentials", tags=["credentials"])
router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
router.include_router(observability.router, prefix="/observability", tags=["observability"])
router.include_router(telemetry.router, prefix="/telemetry", tags=["telemetry"])
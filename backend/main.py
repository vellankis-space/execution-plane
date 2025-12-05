from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.v1 import router as api_v1_router
from core.config import settings
from core.database import init_db, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()

    # Initialize Telemetry (OpenLLMetry)
    try:
        from services.telemetry_service import telemetry_service
        telemetry_service.start()
    except Exception as e:
        print(f"Warning: Could not initialize telemetry: {e}")

    
    # Load MCP configuration from file if it exists
    try:
        from services.fastmcp_manager import fastmcp_manager
        import os
        config_file_path = os.path.join(os.path.dirname(__file__), "..", "mcp.json")
        if os.path.exists(config_file_path):
            success = await fastmcp_manager.load_config_from_file(config_file_path)
            if success:
                print("MCP configuration loaded successfully from mcp.json")
            else:
                print("Failed to load MCP configuration from mcp.json")
        else:
            print("No mcp.json file found, skipping MCP configuration load")
    except Exception as e:
        print(f"Warning: Could not load MCP configuration: {e}")
    
    # Initialize workflow scheduler
    try:
        from services.scheduling_service import SchedulingService
        from core.database import SessionLocal
        
        db = SessionLocal()
        scheduling_service = SchedulingService(db)
        await scheduling_service.load_all_schedules()
        db.close()
        print("Workflow scheduler initialized")
    except Exception as e:
        print(f"Warning: Could not initialize scheduler: {e}")
    
    yield
    
    # Shutdown
    try:
        from services.scheduling_service import scheduler
        if scheduler.running:
            scheduler.shutdown()
            print("Workflow scheduler shut down")
    except Exception as e:
        print(f"Warning: Error shutting down scheduler: {e}")

app = FastAPI(
    title="LangGraph Agent API",
    description="API for creating and managing LangGraph agents",
    version="1.0.0",
    lifespan=lifespan
)



# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add tenant middleware for multi-tenancy support
try:
    from middleware.tenant_middleware import TenantMiddleware
    app.add_middleware(TenantMiddleware)
    print("Tenant middleware enabled")
except Exception as e:
    print(f"Warning: Could not enable tenant middleware: {e}")

# Add audit middleware for automatic request logging
try:
    from middleware.audit_middleware import AuditMiddleware
    app.add_middleware(AuditMiddleware)
    print("Audit middleware enabled")
except Exception as e:
    print(f"Warning: Could not enable audit middleware: {e}")

# Include API routers
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "LangGraph Agent API"}
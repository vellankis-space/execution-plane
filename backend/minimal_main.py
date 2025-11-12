from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import init_db

# Import only the workflow-related API
from api.v1 import workflows, enhanced_monitoring

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Workflow Execution API",
    description="API for executing and monitoring workflows",
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

# Include only workflow-related API routers
app.include_router(workflows.router, prefix="/api/v1")
app.include_router(enhanced_monitoring.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Workflow Execution API"}
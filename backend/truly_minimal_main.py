from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
import json

from core.config import settings
from core.database import init_db

# Create a simple lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

# Create the FastAPI app
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

@app.get("/")
async def root():
    return {"message": "Workflow Execution API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Simple endpoints for testing
@app.get("/api/v1/workflows")
async def list_workflows():
    return {"message": "List of workflows"}

@app.get("/api/v1/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    return {"workflow_id": workflow_id, "name": "Sample Workflow"}

@app.get("/api/v1/executions/{execution_id}")
async def get_execution(execution_id: str):
    return {
        "execution_id": execution_id,
        "status": "completed",
        "started_at": "2025-01-01T00:00:00Z",
        "completed_at": "2025-01-01T00:05:00Z"
    }
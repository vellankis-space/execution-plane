"""
API endpoints for versioning management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from services.versioning_service import VersioningService
from core.database import get_db
from pydantic import BaseModel, ConfigDict

router = APIRouter()


# Response models
class AgentVersionResponse(BaseModel):
    id: int
    agent_id: str
    version: int
    created_at: str
    created_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class WorkflowVersionResponse(BaseModel):
    id: int
    workflow_id: str
    version: int
    created_at: str
    created_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VersionComparisonResponse(BaseModel):
    agent_id: Optional[str] = None
    workflow_id: Optional[str] = None
    version1: int
    version2: int
    differences: dict
    created_at_v1: Optional[str] = None
    created_at_v2: Optional[str] = None


# Agent Versioning Endpoints

@router.post("/agents/{agent_id}/versions")
async def create_agent_version(
    agent_id: str,
    created_by: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a new version snapshot of an agent"""
    try:
        versioning_service = VersioningService(db)
        version = await versioning_service.create_agent_version(agent_id, created_by)
        return AgentVersionResponse(
            id=version.id,
            agent_id=version.agent_id,
            version=version.version,
            created_at=version.created_at.isoformat() if version.created_at else "",
            created_by=version.created_by
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/agents/{agent_id}/versions", response_model=List[AgentVersionResponse])
async def get_agent_versions(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Get all versions of an agent"""
    try:
        versioning_service = VersioningService(db)
        versions = await versioning_service.get_agent_versions(agent_id)
        return [
            AgentVersionResponse(
                id=v.id,
                agent_id=v.agent_id,
                version=v.version,
                created_at=v.created_at.isoformat() if v.created_at else "",
                created_by=v.created_by
            )
            for v in versions
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/agents/{agent_id}/versions/{version}")
async def get_agent_version(
    agent_id: str,
    version: int,
    db: Session = Depends(get_db)
):
    """Get a specific version of an agent"""
    try:
        versioning_service = VersioningService(db)
        version_record = await versioning_service.get_agent_version(agent_id, version)
        if not version_record:
            raise HTTPException(status_code=404, detail="Version not found")
        return {
            "id": version_record.id,
            "agent_id": version_record.agent_id,
            "version": version_record.version,
            "config_snapshot": version_record.config_snapshot,
            "created_at": version_record.created_at.isoformat() if version_record.created_at else "",
            "created_by": version_record.created_by
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/agents/{agent_id}/rollback/{target_version}")
async def rollback_agent(
    agent_id: str,
    target_version: int,
    created_by: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Rollback an agent to a specific version"""
    try:
        versioning_service = VersioningService(db)
        agent = await versioning_service.rollback_agent(agent_id, target_version, created_by)
        return {"message": f"Agent rolled back to version {target_version}", "agent_id": agent.agent_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/agents/{agent_id}/compare/{version1}/{version2}", response_model=VersionComparisonResponse)
async def compare_agent_versions(
    agent_id: str,
    version1: int,
    version2: int,
    db: Session = Depends(get_db)
):
    """Compare two versions of an agent"""
    try:
        versioning_service = VersioningService(db)
        comparison = await versioning_service.compare_agent_versions(agent_id, version1, version2)
        return VersionComparisonResponse(**comparison)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Workflow Versioning Endpoints

@router.post("/workflows/{workflow_id}/versions")
async def create_workflow_version(
    workflow_id: str,
    created_by: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a new version snapshot of a workflow"""
    try:
        versioning_service = VersioningService(db)
        version = await versioning_service.create_workflow_version(workflow_id, created_by)
        return WorkflowVersionResponse(
            id=version.id,
            workflow_id=version.workflow_id,
            version=version.version,
            created_at=version.created_at.isoformat() if version.created_at else "",
            created_by=version.created_by
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workflows/{workflow_id}/versions", response_model=List[WorkflowVersionResponse])
async def get_workflow_versions(
    workflow_id: str,
    db: Session = Depends(get_db)
):
    """Get all versions of a workflow"""
    try:
        versioning_service = VersioningService(db)
        versions = await versioning_service.get_workflow_versions(workflow_id)
        return [
            WorkflowVersionResponse(
                id=v.id,
                workflow_id=v.workflow_id,
                version=v.version,
                created_at=v.created_at.isoformat() if v.created_at else "",
                created_by=v.created_by
            )
            for v in versions
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workflows/{workflow_id}/versions/{version}")
async def get_workflow_version(
    workflow_id: str,
    version: int,
    db: Session = Depends(get_db)
):
    """Get a specific version of a workflow"""
    try:
        versioning_service = VersioningService(db)
        version_record = await versioning_service.get_workflow_version(workflow_id, version)
        if not version_record:
            raise HTTPException(status_code=404, detail="Version not found")
        return {
            "id": version_record.id,
            "workflow_id": version_record.workflow_id,
            "version": version_record.version,
            "definition_snapshot": version_record.definition_snapshot,
            "created_at": version_record.created_at.isoformat() if version_record.created_at else "",
            "created_by": version_record.created_by
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/workflows/{workflow_id}/rollback/{target_version}")
async def rollback_workflow(
    workflow_id: str,
    target_version: int,
    created_by: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Rollback a workflow to a specific version"""
    try:
        versioning_service = VersioningService(db)
        workflow = await versioning_service.rollback_workflow(workflow_id, target_version, created_by)
        return {"message": f"Workflow rolled back to version {target_version}", "workflow_id": workflow.workflow_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workflows/{workflow_id}/compare/{version1}/{version2}", response_model=VersionComparisonResponse)
async def compare_workflow_versions(
    workflow_id: str,
    version1: int,
    version2: int,
    db: Session = Depends(get_db)
):
    """Compare two versions of a workflow"""
    try:
        versioning_service = VersioningService(db)
        comparison = await versioning_service.compare_workflow_versions(workflow_id, version1, version2)
        return VersionComparisonResponse(**comparison)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


"""
Workflow template API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from services.template_service import TemplateService
from core.database import get_db
from api.v1.auth import get_current_user

router = APIRouter()


# Request/Response models
class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    workflow_definition: Dict[str, Any]
    is_public: bool = False
    metadata: Optional[Dict[str, Any]] = None


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class CreateFromTemplateRequest(BaseModel):
    workflow_name: str
    input_overrides: Optional[Dict[str, Any]] = None


class RateTemplateRequest(BaseModel):
    rating: int  # 1-5
    review: Optional[str] = None


# Template Endpoints

@router.post("/templates")
async def create_template(
    template_data: TemplateCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a workflow template"""
    try:
        template_service = TemplateService(db)
        template = await template_service.create_template(
            name=template_data.name,
            description=template_data.description,
            category=template_data.category,
            tags=template_data.tags,
            workflow_definition=template_data.workflow_definition,
            is_public=template_data.is_public,
            created_by=current_user.user_id,
            metadata=template_data.metadata
        )
        return {
            "template_id": template.template_id,
            "name": template.name,
            "is_public": template.is_public
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_templates(
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    is_public: Optional[bool] = Query(None),
    is_featured: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get workflow templates"""
    try:
        template_service = TemplateService(db)
        templates = await template_service.get_templates(
            category=category,
            tag=tag,
            is_public=is_public,
            is_featured=is_featured,
            search=search,
            limit=limit,
            offset=offset
        )
        
        return [
            {
                "template_id": t.template_id,
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "tags": t.tags or [],
                "is_public": t.is_public,
                "is_featured": t.is_featured,
                "usage_count": t.usage_count,
                "rating": t.rating,
                "rating_count": t.rating_count,
                "created_by": t.created_by,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in templates
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}")
async def get_template(
    template_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific template"""
    try:
        template_service = TemplateService(db)
        template = await template_service.get_template(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Only show workflow definition if public or created by user
        show_definition = template.is_public or template.created_by == current_user.user_id
        
        return {
            "template_id": template.template_id,
            "name": template.name,
            "description": template.description,
            "category": template.category,
            "tags": template.tags or [],
            "workflow_definition": template.workflow_definition if show_definition else None,
            "is_public": template.is_public,
            "is_featured": template.is_featured,
            "usage_count": template.usage_count,
            "rating": template.rating,
            "rating_count": template.rating_count,
            "created_by": template.created_by,
            "created_at": template.created_at.isoformat() if template.created_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates/{template_id}/create-workflow")
async def create_workflow_from_template(
    template_id: str,
    request: CreateFromTemplateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a workflow from a template"""
    try:
        template_service = TemplateService(db)
        result = await template_service.create_workflow_from_template(
            template_id=template_id,
            workflow_name=request.workflow_name,
            user_id=current_user.user_id,
            input_overrides=request.input_overrides
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates/{template_id}/rate")
async def rate_template(
    template_id: str,
    rating_data: RateTemplateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rate a template"""
    try:
        template_service = TemplateService(db)
        rating = await template_service.rate_template(
            template_id=template_id,
            user_id=current_user.user_id,
            rating=rating_data.rating,
            review=rating_data.review
        )
        return {
            "rating_id": rating.rating_id,
            "rating": rating.rating,
            "message": "Template rated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/categories")
async def get_categories(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all template categories"""
    try:
        template_service = TemplateService(db)
        categories = await template_service.get_template_categories()
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/tags")
async def get_tags(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all template tags"""
    try:
        template_service = TemplateService(db)
        tags = await template_service.get_template_tags()
        return {"tags": tags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


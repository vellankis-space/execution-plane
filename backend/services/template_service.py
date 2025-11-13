"""
Workflow template service
"""
import uuid
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime

from models.template import WorkflowTemplate, TemplateUsage, TemplateRating
from services.workflow_service import WorkflowService

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for managing workflow templates"""
    
    def __init__(self, db: Session):
        self.db = db
        self.workflow_service = WorkflowService(db)
    
    # Template Management
    
    async def create_template(
        self,
        name: str,
        workflow_definition: Dict[str, Any],
        description: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_public: bool = False,
        created_by: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkflowTemplate:
        """Create a workflow template"""
        template_id = str(uuid.uuid4())
        
        template = WorkflowTemplate(
            template_id=template_id,
            name=name,
            description=description,
            category=category,
            tags=tags or [],
            workflow_definition=workflow_definition,
            is_public=is_public,
            created_by=created_by,
            metadata=metadata or {}
        )
        
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    async def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get a template by ID"""
        return self.db.query(WorkflowTemplate).filter(
            WorkflowTemplate.template_id == template_id
        ).first()
    
    async def get_templates(
        self,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        is_public: Optional[bool] = None,
        is_featured: Optional[bool] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[WorkflowTemplate]:
        """Get templates with filters"""
        query = self.db.query(WorkflowTemplate)
        
        if category:
            query = query.filter(WorkflowTemplate.category == category)
        
        if tag:
            query = query.filter(WorkflowTemplate.tags.contains([tag]))
        
        if is_public is not None:
            query = query.filter(WorkflowTemplate.is_public == is_public)
        
        if is_featured is not None:
            query = query.filter(WorkflowTemplate.is_featured == is_featured)
        
        if search:
            query = query.filter(
                or_(
                    WorkflowTemplate.name.ilike(f"%{search}%"),
                    WorkflowTemplate.description.ilike(f"%{search}%")
                )
            )
        
        return query.order_by(desc(WorkflowTemplate.usage_count)).offset(offset).limit(limit).all()
    
    async def update_template(
        self,
        template_id: str,
        updates: Dict[str, Any]
    ) -> Optional[WorkflowTemplate]:
        """Update a template"""
        template = await self.get_template(template_id)
        if not template:
            return None
        
        for key, value in updates.items():
            if hasattr(template, key):
                setattr(template, key, value)
        
        setattr(template, 'updated_at', datetime.utcnow())
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        template = await self.get_template(template_id)
        if not template:
            return False
        
        self.db.delete(template)
        self.db.commit()
        return True
    
    # Template Usage
    
    async def create_workflow_from_template(
        self,
        template_id: str,
        workflow_name: str,
        user_id: Optional[str] = None,
        input_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a workflow from a template"""
        template = await self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Create workflow from template
        workflow = await self.workflow_service.create_workflow(
            name=workflow_name,
            description=f"Created from template: {template.name}",
            definition=template.workflow_definition,
            created_by=user_id
        )
        
        # Track template usage
        usage_id = str(uuid.uuid4())
        usage = TemplateUsage(
            usage_id=usage_id,
            template_id=template_id,
            user_id=user_id,
            workflow_id=workflow.workflow_id
        )
        
        self.db.add(usage)
        
        # Update template usage count
        template.usage_count += 1
        self.db.commit()
        
        return {
            "workflow_id": workflow.workflow_id,
            "workflow_name": workflow.name,
            "template_id": template_id,
            "template_name": template.name
        }
    
    # Template Ratings
    
    async def rate_template(
        self,
        template_id: str,
        user_id: str,
        rating: int,
        review: Optional[str] = None
    ) -> TemplateRating:
        """Rate a template"""
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Check if user already rated
        existing_rating = self.db.query(TemplateRating).filter(
            and_(
                TemplateRating.template_id == template_id,
                TemplateRating.user_id == user_id
            )
        ).first()
        
        if existing_rating:
            existing_rating.rating = rating
            existing_rating.review = review
            existing_rating.updated_at = datetime.utcnow()
            rating_obj = existing_rating
        else:
            rating_id = str(uuid.uuid4())
            rating_obj = TemplateRating(
                rating_id=rating_id,
                template_id=template_id,
                user_id=user_id,
                rating=rating,
                review=review
            )
            self.db.add(rating_obj)
        
        self.db.commit()
        self.db.refresh(rating_obj)
        
        # Update template average rating
        await self._update_template_rating(template_id)
        
        return rating_obj
    
    async def _update_template_rating(self, template_id: str):
        """Update template's average rating"""
        ratings = self.db.query(TemplateRating).filter(
            TemplateRating.template_id == template_id
        ).all()
        
        if ratings:
            avg_rating = sum(r.rating for r in ratings) / len(ratings)
            template = await self.get_template(template_id)
            if template:
                template.rating = round(avg_rating, 2)
                template.rating_count = len(ratings)
                self.db.commit()
    
    async def get_template_categories(self) -> List[str]:
        """Get all template categories"""
        categories = self.db.query(WorkflowTemplate.category).filter(
            WorkflowTemplate.category.isnot(None)
        ).distinct().all()
        
        return [cat[0] for cat in categories if cat[0]]
    
    async def get_template_tags(self) -> List[str]:
        """Get all template tags"""
        templates = self.db.query(WorkflowTemplate.tags).all()
        all_tags = set()
        
        for tags in templates:
            if tags[0]:
                all_tags.update(tags[0])
        
        return sorted(list(all_tags))


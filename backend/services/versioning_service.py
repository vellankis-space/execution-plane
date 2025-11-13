"""
Versioning service for agents and workflows
"""
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from models.versioning import AgentVersion, WorkflowVersion
from models.agent import Agent as AgentModel
from models.workflow import Workflow as WorkflowModel


class VersioningService:
    """Service for managing versions of agents and workflows"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Agent Versioning Methods
    
    async def create_agent_version(self, agent_id: str, created_by: Optional[str] = None) -> AgentVersion:
        """Create a new version snapshot of an agent"""
        # Get current agent
        agent = self.db.query(AgentModel).filter(AgentModel.agent_id == agent_id).first()
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Get current version number
        current_version = getattr(agent, 'version', 1)
        new_version = current_version + 1
        
        # Create config snapshot
        config_snapshot = {
            "name": agent.name,
            "agent_type": agent.agent_type,
            "llm_provider": agent.llm_provider,
            "llm_model": agent.llm_model,
            "temperature": agent.temperature,
            "system_prompt": agent.system_prompt,
            "tools": agent.tools,
            "tool_configs": agent.tool_configs,
            "max_iterations": agent.max_iterations,
            "memory_type": agent.memory_type,
            "streaming_enabled": agent.streaming_enabled,
            "human_in_loop": agent.human_in_loop,
            "recursion_limit": agent.recursion_limit,
            "pii_config": agent.pii_config,
        }
        
        # Create version record
        agent_version = AgentVersion(
            agent_id=agent_id,
            version=new_version,
            config_snapshot=config_snapshot,
            created_by=created_by
        )
        
        self.db.add(agent_version)
        
        # Update agent version number
        setattr(agent, 'version', new_version)
        
        self.db.commit()
        self.db.refresh(agent_version)
        
        return agent_version
    
    async def get_agent_versions(self, agent_id: str) -> List[AgentVersion]:
        """Get all versions of an agent"""
        return self.db.query(AgentVersion).filter(
            AgentVersion.agent_id == agent_id
        ).order_by(desc(AgentVersion.version)).all()
    
    async def get_agent_version(self, agent_id: str, version: int) -> Optional[AgentVersion]:
        """Get a specific version of an agent"""
        return self.db.query(AgentVersion).filter(
            AgentVersion.agent_id == agent_id,
            AgentVersion.version == version
        ).first()
    
    async def rollback_agent(self, agent_id: str, target_version: int, created_by: Optional[str] = None) -> AgentModel:
        """Rollback an agent to a specific version"""
        # Get target version
        target_version_record = await self.get_agent_version(agent_id, target_version)
        if not target_version_record:
            raise ValueError(f"Version {target_version} not found for agent {agent_id}")
        
        # Get current agent
        agent = self.db.query(AgentModel).filter(AgentModel.agent_id == agent_id).first()
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Create a new version snapshot of current state before rollback
        await self.create_agent_version(agent_id, created_by)
        
        # Restore from snapshot
        config = target_version_record.config_snapshot
        agent.name = config.get("name")
        agent.agent_type = config.get("agent_type")
        agent.llm_provider = config.get("llm_provider")
        agent.llm_model = config.get("llm_model")
        agent.temperature = config.get("temperature")
        agent.system_prompt = config.get("system_prompt")
        agent.tools = config.get("tools")
        agent.tool_configs = config.get("tool_configs")
        agent.max_iterations = config.get("max_iterations")
        agent.memory_type = config.get("memory_type")
        agent.streaming_enabled = config.get("streaming_enabled")
        agent.human_in_loop = config.get("human_in_loop")
        agent.recursion_limit = config.get("recursion_limit")
        agent.pii_config = config.get("pii_config")
        
        # Create new version after rollback
        await self.create_agent_version(agent_id, created_by)
        
        self.db.commit()
        self.db.refresh(agent)
        
        return agent
    
    async def compare_agent_versions(self, agent_id: str, version1: int, version2: int) -> Dict[str, Any]:
        """Compare two versions of an agent"""
        v1 = await self.get_agent_version(agent_id, version1)
        v2 = await self.get_agent_version(agent_id, version2)
        
        if not v1 or not v2:
            raise ValueError("One or both versions not found")
        
        config1 = v1.config_snapshot
        config2 = v2.config_snapshot
        
        differences = {}
        all_keys = set(config1.keys()) | set(config2.keys())
        
        for key in all_keys:
            val1 = config1.get(key)
            val2 = config2.get(key)
            
            if val1 != val2:
                differences[key] = {
                    "version1": val1,
                    "version2": val2
                }
        
        return {
            "agent_id": agent_id,
            "version1": version1,
            "version2": version2,
            "differences": differences,
            "created_at_v1": v1.created_at.isoformat() if v1.created_at else None,
            "created_at_v2": v2.created_at.isoformat() if v2.created_at else None,
        }
    
    # Workflow Versioning Methods
    
    async def create_workflow_version(self, workflow_id: str, created_by: Optional[str] = None) -> WorkflowVersion:
        """Create a new version snapshot of a workflow"""
        # Get current workflow
        workflow = self.db.query(WorkflowModel).filter(WorkflowModel.workflow_id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Get current version number
        current_version = getattr(workflow, 'version', 1)
        new_version = current_version + 1
        
        # Create definition snapshot
        definition_snapshot = {
            "name": workflow.name,
            "description": workflow.description,
            "definition": workflow.definition,
        }
        
        # Create version record
        workflow_version = WorkflowVersion(
            workflow_id=workflow_id,
            version=new_version,
            definition_snapshot=definition_snapshot,
            created_by=created_by
        )
        
        self.db.add(workflow_version)
        
        # Update workflow version number
        setattr(workflow, 'version', new_version)
        
        self.db.commit()
        self.db.refresh(workflow_version)
        
        return workflow_version
    
    async def get_workflow_versions(self, workflow_id: str) -> List[WorkflowVersion]:
        """Get all versions of a workflow"""
        return self.db.query(WorkflowVersion).filter(
            WorkflowVersion.workflow_id == workflow_id
        ).order_by(desc(WorkflowVersion.version)).all()
    
    async def get_workflow_version(self, workflow_id: str, version: int) -> Optional[WorkflowVersion]:
        """Get a specific version of a workflow"""
        return self.db.query(WorkflowVersion).filter(
            WorkflowVersion.workflow_id == workflow_id,
            WorkflowVersion.version == version
        ).first()
    
    async def rollback_workflow(self, workflow_id: str, target_version: int, created_by: Optional[str] = None) -> WorkflowModel:
        """Rollback a workflow to a specific version"""
        # Get target version
        target_version_record = await self.get_workflow_version(workflow_id, target_version)
        if not target_version_record:
            raise ValueError(f"Version {target_version} not found for workflow {workflow_id}")
        
        # Get current workflow
        workflow = self.db.query(WorkflowModel).filter(WorkflowModel.workflow_id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Create a new version snapshot of current state before rollback
        await self.create_workflow_version(workflow_id, created_by)
        
        # Restore from snapshot
        config = target_version_record.definition_snapshot
        workflow.name = config.get("name")
        workflow.description = config.get("description")
        workflow.definition = config.get("definition")
        
        # Create new version after rollback
        await self.create_workflow_version(workflow_id, created_by)
        
        self.db.commit()
        self.db.refresh(workflow)
        
        return workflow
    
    async def compare_workflow_versions(self, workflow_id: str, version1: int, version2: int) -> Dict[str, Any]:
        """Compare two versions of a workflow"""
        v1 = await self.get_workflow_version(workflow_id, version1)
        v2 = await self.get_workflow_version(workflow_id, version2)
        
        if not v1 or not v2:
            raise ValueError("One or both versions not found")
        
        config1 = v1.definition_snapshot
        config2 = v2.definition_snapshot
        
        differences = {}
        all_keys = set(config1.keys()) | set(config2.keys())
        
        for key in all_keys:
            val1 = config1.get(key)
            val2 = config2.get(key)
            
            if val1 != val2:
                differences[key] = {
                    "version1": val1,
                    "version2": val2
                }
        
        return {
            "workflow_id": workflow_id,
            "version1": version1,
            "version2": version2,
            "differences": differences,
            "created_at_v1": v1.created_at.isoformat() if v1.created_at else None,
            "created_at_v2": v2.created_at.isoformat() if v2.created_at else None,
        }


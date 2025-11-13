"""
Unit tests for WorkflowService
"""
import pytest
from services.workflow_service import WorkflowService
from schemas.workflow import WorkflowCreate, WorkflowExecutionCreate


@pytest.mark.asyncio
async def test_create_workflow(db_session):
    """Test creating a workflow"""
    workflow_service = WorkflowService(db_session)
    
    workflow_data = WorkflowCreate(
        name="Test Workflow",
        description="A test workflow",
        definition={
            "steps": [
                {
                    "id": "step1",
                    "agent_id": "test-agent-1",
                    "input": "{{input}}"
                }
            ]
        }
    )
    
    workflow = await workflow_service.create_workflow(workflow_data)
    
    assert workflow is not None
    assert workflow.name == "Test Workflow"
    assert workflow.version == 1  # Initial version


@pytest.mark.asyncio
async def test_get_workflow(db_session, test_workflow):
    """Test retrieving a workflow"""
    workflow_service = WorkflowService(db_session)
    
    workflow = await workflow_service.get_workflow(test_workflow.workflow_id)
    
    assert workflow is not None
    assert workflow.workflow_id == test_workflow.workflow_id
    assert workflow.name == test_workflow.name


@pytest.mark.asyncio
async def test_get_workflows(db_session, test_workflow):
    """Test retrieving all workflows"""
    workflow_service = WorkflowService(db_session)
    
    workflows = await workflow_service.get_workflows()
    
    assert len(workflows) >= 1
    assert any(w.workflow_id == test_workflow.workflow_id for w in workflows)


@pytest.mark.asyncio
async def test_delete_workflow(db_session, test_workflow):
    """Test deleting a workflow"""
    workflow_service = WorkflowService(db_session)
    
    success = await workflow_service.delete_workflow(test_workflow.workflow_id)
    
    assert success is True
    
    # Verify workflow is deleted
    workflow = await workflow_service.get_workflow(test_workflow.workflow_id)
    assert workflow is None


@pytest.mark.asyncio
async def test_create_workflow_execution(db_session, test_workflow):
    """Test creating a workflow execution"""
    workflow_service = WorkflowService(db_session)
    
    execution_data = WorkflowExecutionCreate(
        workflow_id=test_workflow.workflow_id,
        input_data={"input": "test input"}
    )
    
    execution = await workflow_service.create_workflow_execution(execution_data)
    
    assert execution is not None
    assert execution.workflow_id == test_workflow.workflow_id
    assert execution.status == "pending"


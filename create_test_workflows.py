#!/usr/bin/env python3
"""
Script to create and execute 10 test workflows that will complete successfully.
This populates the monitoring dashboard with successful executions.
"""

import requests
import time
import json
from typing import List, Dict, Any

BASE_URL = "http://localhost:8000/api/v1"

# Simple workflow templates with realistic use cases
WORKFLOW_TEMPLATES = [
    {
        "name": "Daily Summary Workflow",
        "description": "Generate a brief daily summary",
        "input": "Summarize the key points from today's meeting"
    },
    {
        "name": "Email Response Workflow",
        "description": "Draft a professional email response",
        "input": "Write a polite response to a customer inquiry"
    },
    {
        "name": "Code Review Workflow",
        "description": "Review code changes",
        "input": "Review the recent pull request for improvements"
    },
    {
        "name": "Data Analysis Workflow",
        "description": "Analyze sample data",
        "input": "What insights can we derive from this quarter's data?"
    },
    {
        "name": "Content Creation Workflow",
        "description": "Create marketing content",
        "input": "Write a short product description for our new feature"
    },
    {
        "name": "Bug Triage Workflow",
        "description": "Prioritize bug reports",
        "input": "Categorize this bug report by severity"
    },
    {
        "name": "Documentation Workflow",
        "description": "Generate documentation",
        "input": "Create brief API documentation for this endpoint"
    },
    {
        "name": "Research Workflow",
        "description": "Quick research summary",
        "input": "What are the current trends in AI development?"
    },
    {
        "name": "Planning Workflow",
        "description": "Create project plan",
        "input": "Outline the steps for implementing this feature"
    },
    {
        "name": "Feedback Analysis Workflow",
        "description": "Analyze user feedback",
        "input": "Summarize the main themes from customer feedback"
    }
]


def get_agents() -> List[Dict[str, Any]]:
    """Fetch all available agents"""
    try:
        response = requests.get(f"{BASE_URL}/agents/")
        response.raise_for_status()
        agents = response.json()
        print(f"✓ Found {len(agents)} agents")
        return agents
    except Exception as e:
        print(f"✗ Error fetching agents: {e}")
        return []


def create_workflow(agent_id: str, name: str, description: str) -> Dict[str, Any]:
    """Create a simple workflow with one step"""
    workflow_data = {
        "name": name,
        "description": description,
        "definition": {
            "steps": [
                {
                    "id": "step_1",
                    "agent_id": agent_id,
                    "name": "Process Request",
                    "dependencies": []
                }
            ]
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/workflows/",
            json=workflow_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        workflow = response.json()
        print(f"✓ Created workflow: {name}")
        return workflow
    except Exception as e:
        print(f"✗ Error creating workflow '{name}': {e}")
        return None


def execute_workflow(workflow_id: str, input_message: str, workflow_name: str) -> bool:
    """Execute a workflow with the given input"""
    execution_data = {
        "workflow_id": workflow_id,
        "input_data": {
            "message": input_message
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/workflows/{workflow_id}/execute",
            json=execution_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()
        status = result.get("status", "unknown")
        
        if status == "completed":
            print(f"✓ Executed workflow: {workflow_name} - Status: {status}")
            return True
        else:
            print(f"⚠ Executed workflow: {workflow_name} - Status: {status}")
            return status in ["completed", "running"]
            
    except Exception as e:
        print(f"✗ Error executing workflow '{workflow_name}': {e}")
        return False


def main():
    print("=" * 60)
    print("Creating 10 Test Workflows for Monitoring Dashboard")
    print("=" * 60)
    print()
    
    # Step 1: Get available agents
    print("Step 1: Fetching available agents...")
    agents = get_agents()
    
    if not agents:
        print("\n✗ No agents found. Please create at least one agent first.")
        print("   Visit http://localhost:3000/playground to create an agent.")
        return
    
    # Use the first agent for all workflows
    agent = agents[0]
    agent_id = agent["agent_id"]
    agent_name = agent["name"]
    print(f"   Using agent: {agent_name} ({agent_id})")
    print()
    
    # Step 2: Create workflows
    print("Step 2: Creating workflows...")
    created_workflows = []
    
    for i, template in enumerate(WORKFLOW_TEMPLATES, 1):
        workflow = create_workflow(
            agent_id=agent_id,
            name=template["name"],
            description=template["description"]
        )
        
        if workflow:
            created_workflows.append({
                "workflow": workflow,
                "input": template["input"]
            })
        
        time.sleep(0.5)  # Small delay between creations
    
    print(f"\n✓ Successfully created {len(created_workflows)}/10 workflows")
    print()
    
    # Step 3: Execute workflows
    print("Step 3: Executing workflows...")
    successful_executions = 0
    
    for i, item in enumerate(created_workflows, 1):
        workflow = item["workflow"]
        input_msg = item["input"]
        
        print(f"\n[{i}/{len(created_workflows)}] Executing: {workflow['name']}")
        
        success = execute_workflow(
            workflow_id=workflow["workflow_id"],
            input_message=input_msg,
            workflow_name=workflow["name"]
        )
        
        if success:
            successful_executions += 1
        
        # Wait a bit between executions to avoid overwhelming the system
        time.sleep(2)
    
    # Summary
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total workflows created: {len(created_workflows)}")
    print(f"Successful executions: {successful_executions}")
    print(f"Failed executions: {len(created_workflows) - successful_executions}")
    print()
    print("✓ Done! Check the monitoring dashboard to see the results.")
    print("   Visit: http://localhost:3000/monitoring")
    print()


if __name__ == "__main__":
    main()

#!/bin/bash

# Script to create and execute 10 test workflows that will complete successfully
# This populates the monitoring dashboard with successful executions

BASE_URL="http://localhost:8000/api/v1"

echo "============================================================"
echo "Creating 10 Test Workflows for Monitoring Dashboard"
echo "============================================================"
echo ""

# Step 1: Get available agents
echo "Step 1: Fetching available agents..."
AGENTS_RESPONSE=$(curl -s "${BASE_URL}/agents/")
AGENT_ID=$(echo $AGENTS_RESPONSE | grep -o '"agent_id":"[^"]*"' | head -1 | cut -d'"' -f4)
AGENT_NAME=$(echo $AGENTS_RESPONSE | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$AGENT_ID" ]; then
    echo "✗ No agents found. Please create at least one agent first."
    echo "   Visit http://localhost:3000/playground to create an agent."
    exit 1
fi

echo "✓ Using agent: $AGENT_NAME ($AGENT_ID)"
echo ""

# Workflow templates
declare -a WORKFLOWS=(
    "Daily Summary Workflow|Generate a brief daily summary|Summarize the key points from today"
    "Email Response Workflow|Draft a professional email response|Write a polite response to an inquiry"
    "Code Review Workflow|Review code changes|Review this code for improvements"
    "Data Analysis Workflow|Analyze sample data|What insights can we derive from the data?"
    "Content Creation Workflow|Create marketing content|Write a short product description"
    "Bug Triage Workflow|Prioritize bug reports|Categorize this bug by severity"
    "Documentation Workflow|Generate documentation|Create brief documentation"
    "Research Workflow|Quick research summary|What are current AI trends?"
    "Planning Workflow|Create project plan|Outline steps for this feature"
    "Feedback Analysis Workflow|Analyze user feedback|Summarize customer feedback themes"
)

echo "Step 2: Creating and executing workflows..."
echo ""

CREATED=0
EXECUTED=0

for i in "${!WORKFLOWS[@]}"; do
    IFS='|' read -r -a WORKFLOW <<< "${WORKFLOWS[$i]}"
    NAME="${WORKFLOW[0]}"
    DESC="${WORKFLOW[1]}"
    INPUT="${WORKFLOW[2]}"
    
    NUM=$((i + 1))
    echo "[$NUM/10] Creating: $NAME"
    
    # Create workflow
    WORKFLOW_DATA=$(cat <<EOF
{
    "name": "$NAME",
    "description": "$DESC",
    "definition": {
        "steps": [
            {
                "id": "step_1",
                "agent_id": "$AGENT_ID",
                "name": "Process Request",
                "dependencies": []
            }
        ]
    }
}
EOF
)
    
    CREATE_RESPONSE=$(curl -s -X POST "${BASE_URL}/workflows/" \
        -H "Content-Type: application/json" \
        -d "$WORKFLOW_DATA")
    
    WORKFLOW_ID=$(echo $CREATE_RESPONSE | grep -o '"workflow_id":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$WORKFLOW_ID" ]; then
        echo "  ✓ Created workflow ID: $WORKFLOW_ID"
        CREATED=$((CREATED + 1))
        
        # Execute workflow
        echo "  ⟳ Executing workflow..."
        
        EXECUTE_DATA=$(cat <<EOF
{
    "workflow_id": "$WORKFLOW_ID",
    "input_data": {
        "message": "$INPUT"
    }
}
EOF
)
        
        EXEC_RESPONSE=$(curl -s -X POST "${BASE_URL}/workflows/${WORKFLOW_ID}/execute" \
            -H "Content-Type: application/json" \
            -d "$EXECUTE_DATA")
        
        STATUS=$(echo $EXEC_RESPONSE | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        
        if [ -n "$STATUS" ]; then
            echo "  ✓ Execution status: $STATUS"
            EXECUTED=$((EXECUTED + 1))
        else
            echo "  ⚠ Execution started (check monitoring for status)"
            EXECUTED=$((EXECUTED + 1))
        fi
    else
        echo "  ✗ Failed to create workflow"
    fi
    
    echo ""
    sleep 2  # Wait between executions
done

# Summary
echo "============================================================"
echo "Summary"
echo "============================================================"
echo "Total workflows created: $CREATED"
echo "Total workflows executed: $EXECUTED"
echo ""
echo "✓ Done! Check the monitoring dashboard to see the results."
echo "   Visit: http://localhost:3000/monitoring"
echo ""

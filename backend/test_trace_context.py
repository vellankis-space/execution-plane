"""
Quick test to verify trace context system
"""
from services.trace_context import trace_context_manager

# Test basic operations
print("Testing trace context manager...")

# Set context
trace_context_manager.set_trace_context(
    "test_trace_123",
    agent_id="test_agent",
    workflow_id="test_workflow",
    session_id="test_session"
)

# Get context
context = trace_context_manager.get_trace_context("test_trace_123")
print(f"✅ Stored context: {context}")

if context and 'agent_id' in context:
    print("✅ Trace context manager is working!")
else:
    print("❌ Trace context manager failed!")

print("\nNow restart backend and execute a workflow/agent to test full system")

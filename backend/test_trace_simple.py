#!/usr/bin/env python3
"""Quick test to verify OpenTelemetry trace creation works"""
import sys
sys.path.insert(0, '/Users/apple/Desktop/execution-plane/backend')

try:
    from opentelemetry import trace
    from services.trace_context import trace_context_manager
    
    print("✅ Imports successful")
    
    # Create a tracer
    tracer = trace.get_tracer(__name__)
    print("✅ Got tracer")
    
    # Create a span
    with tracer.start_as_current_span("test_span") as span:
        print("✅ Created span")
        
        # Get trace_id
        trace_id = format(span.get_span_context().trace_id, '032x')
        print(f"✅ Got trace_id: {trace_id}")
        
        # Register in trace context
        trace_context_manager.set_trace_context(
            trace_id,
            agent_id="test_agent_123",
            workflow_id="test_workflow_456"
        )
        print("✅ Registered trace context")
        
        # Retrieve it
        context = trace_context_manager.get_trace_context(trace_id)
        print(f"✅ Retrieved context: {context}")
        
        if context and 'agent_id' in context:
            print("\n🎉 SUCCESS: Trace context system working perfectly!")
        else:
            print("\n❌ FAIL: Context not stored correctly")
            
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

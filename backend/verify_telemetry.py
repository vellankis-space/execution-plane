import asyncio
import sys
import os
import time

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.telemetry_service import telemetry_service
from opentelemetry import trace

async def verify_telemetry():
    print("🚀 Starting Telemetry Verification...")
    
    # 1. Initialize Telemetry
    print("Initializing TelemetryService...")
    telemetry_service.start()
    
    if not telemetry_service.enabled:
        print("❌ TelemetryService failed to enable.")
        return
    
    print("✅ TelemetryService enabled.")
    
    # 2. Generate a Test Trace
    print("Generating test trace...")
    tracer = trace.get_tracer("verify_telemetry")
    
    test_trace_id = None
    with tracer.start_as_current_span("verification_test_span") as span:
        span.set_attribute("test.attribute", "verification_value")
        span.set_attribute("gen_ai.system", "test_llm") # To test LLM type detection
        span.set_attribute("llm.usage.total_tokens", 42)
        test_trace_id = span.get_span_context().trace_id
        print(f"Created span with Trace ID: {test_trace_id:x}")
        
    # 3. Wait for export
    print("Waiting 5 seconds for trace export...")
    await asyncio.sleep(5)
    
    # 4. Query Jaeger
    print("Querying Jaeger for traces...")
    # Convert trace_id to hex string
    trace_id_hex = f"{test_trace_id:x}"
    
    # Try to get specific trace
    trace_details = await telemetry_service.get_trace_details(trace_id_hex)
    
    if trace_details:
        print(f"✅ Found trace {trace_id_hex} in Jaeger!")
        print(f"  Operation Name: {trace_details.get('operationName')}") # Jaeger format
        # Check spans
        spans = trace_details.get('spans', [])
        print(f"  Spans count: {len(spans)}")
        if spans:
            print(f"  First span tags: {spans[0].get('tags')}")
    else:
        print(f"⚠️ Trace {trace_id_hex} not found in Jaeger yet. It might take longer to flush.")
        
        # Try listing traces
        print("Listing recent traces...")
        traces = await telemetry_service.get_traces(limit=5)
        print(f"Found {len(traces.get('data', []))} traces.")
        for t in traces.get('data', []):
            print(f"  - {t.get('traceID')}: {t.get('spans', [{}])[0].get('operationName')}")

if __name__ == "__main__":
    asyncio.run(verify_telemetry())

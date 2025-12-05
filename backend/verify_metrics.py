"""
Verification script to check if metrics are being calculated properly.
Run this after executing an agent to verify traces/spans are saved to SQLite.
"""
import sqlite3
import json

def verify_metrics():
    """Check if traces and spans are being saved to database"""
    
    try:
        conn = sqlite3.connect('agents.db')
        cursor = conn.cursor()
        
        # Check traces
        cursor.execute("SELECT COUNT(*) FROM traces")
        trace_count = cursor.fetchone()[0]
        print(f"✅ Total traces in database: {trace_count}")
        
        # Check spans
        cursor.execute("SELECT COUNT(*) FROM spans")
        span_count = cursor.fetchone()[0]
        print(f"✅ Total spans in database: {span_count}")
        
        if trace_count == 0 and span_count == 0:
            print("\n⚠️  WARNING: No traces or spans found in database!")
            print("   This is normal if you haven't executed any agents yet.")
            print("   Please:")
            print("   1. Restart the backend server")
            print("   2. Execute an agent")
            print("   3. Run this script again")
            return False
        
        # Show sample trace
        if trace_count > 0:
            cursor.execute("SELECT trace_id, service_name, status, root_span_name FROM traces LIMIT 1")
            trace = cursor.fetchone()
            print(f"\n📊 Sample trace:")
            print(f"   ID: {trace[0]}")
            print(f"   Service: {trace[1]}")
            print(f"   Status: {trace[2]}")
            print(f"   Root span: {trace[3]}")
        
        # Check for agent spans with metrics
        if span_count > 0:
            cursor.execute("""
                SELECT name, attributes 
                FROM spans 
                WHERE attributes LIKE '%gen_ai.system%' 
                LIMIT 1
            """)
            llm_span = cursor.fetchone()
            
            if llm_span:
                print(f"\n🤖 Sample LLM span:")
                print(f"   Name: {llm_span[0]}")
                
                try:
                    attrs = json.loads(llm_span[1])
                    print(f"   LLM Provider: {attrs.get('gen_ai.system', 'N/A')}")
                    print(f"   Model: {attrs.get('gen_ai.request.model', 'N/A')}")
                    print(f"   Input tokens: {attrs.get('gen_ai.usage.input_tokens', 'N/A')}")
                    print(f"   Output tokens: {attrs.get('gen_ai.usage.output_tokens', 'N/A')}")
                except:
                    print("   (Could not parse attributes)")
            else:
                print("\n⚠️  No LLM spans found (spans without gen_ai.system attribute)")
        
        # Check for agent_id filtering
        cursor.execute("""
            SELECT COUNT(*) 
            FROM spans 
            WHERE attributes LIKE '%agent_id%'
        """)
        agent_spans = cursor.fetchone()[0]
        print(f"\n🎯 Spans with agent_id: {agent_spans}")
        
        if agent_spans > 0:
            # Show sample agent span
            cursor.execute("""
                SELECT name, attributes 
                FROM spans 
                WHERE attributes LIKE '%agent_id%' 
                LIMIT 1
            """)
            agent_span = cursor.fetchone()
            if agent_span:
                print(f"   Sample agent span: {agent_span[0]}")
                try:
                    attrs = json.loads(agent_span[1])
                    print(f"   agent_id: {attrs.get('agent_id', 'N/A')}")
                except:
                    pass
        
        # Check for workflow_id filtering
        cursor.execute("""
            SELECT COUNT(*) 
            FROM spans 
            WHERE attributes LIKE '%workflow_id%'
        """)
        workflow_spans = cursor.fetchone()[0]
        print(f"🎯 Spans with workflow_id: {workflow_spans}")
        
        if workflow_spans > 0:
            # Show sample workflow span
            cursor.execute("""
                SELECT name, attributes 
                FROM spans 
                WHERE attributes LIKE '%workflow_id%' 
                LIMIT 1
            """)
            wf_span = cursor.fetchone()
            if wf_span:
                print(f"   Sample workflow span: {wf_span[0]}")
                try:
                    attrs = json.loads(wf_span[1])
                    print(f"   workflow_id: {attrs.get('workflow_id', 'N/A')}")
                except:
                    pass
        
        conn.close()
        
        print("\n" + "="*60)
        if trace_count > 0 and span_count > 0:
            if agent_spans > 0 or workflow_spans > 0:
                print("✅ SUCCESS: Metrics system is FULLY working!")
                print("   ✓ Traces and spans are being saved to SQLite")
                print("   ✓ Agent/Workflow IDs are being captured")
                print("   ✓ Metrics endpoints will return filtered data")
            else:
                print("⚠️  PARTIAL SUCCESS: Spans exist but missing agent_id/workflow_id")
                print("   Traces and spans are being saved to SQLite.")
                print("   BUT: No agent_id or workflow_id attributes found!")
                print("   This means metrics filtering won't work.")
                print("\n   📝 ACTION REQUIRED:")
                print("   1. Restart the backend server to load new code")
                print("   2. Execute an agent or workflow")
                print("   3. Run this verification script again")
        else:
            print("⚠️  WAITING: Database is accessible but no data yet.")
            print("   Execute an agent to generate trace data.")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verifying metrics system...\n")
    verify_metrics()

import sqlite3
import os

# Connect to the database
db_path = os.path.join("backend", "agents.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Update the Docker MCP Toolkit server to use HTTP transport
    cursor.execute("""
        UPDATE mcp_servers 
        SET transport_type = 'http', 
            url = 'http://localhost:3000', 
            command = NULL,
            auth_token = 'my-test-token-123',
            args = NULL,
            env = '{"PYTHONUNBUFFERED": "1"}'
        WHERE name = 'Docker MCP Toolkit';
    """)
    
    if cursor.rowcount > 0:
        print("Successfully updated Docker MCP Toolkit server configuration to use HTTP transport.")
        print("Updated fields:")
        print("  - transport_type: http")
        print("  - url: http://localhost:3000")
        print("  - auth_token: my-test-token-123")
        print("  - command: NULL (removed)")
        print("  - args: NULL (removed)")
        print("  - env: {'PYTHONUNBUFFERED': '1'}")
    else:
        print("No Docker MCP Toolkit server found to update.")
        
    conn.commit()
    
    # Verify the update
    cursor.execute("SELECT server_id, name, transport_type, url, command FROM mcp_servers WHERE name = 'Docker MCP Toolkit';")
    rows = cursor.fetchall()
    
    if rows:
        row = rows[0]
        print("\nVerification:")
        print(f"  Server ID: {row[0]}")
        print(f"  Name: {row[1]}")
        print(f"  Transport Type: {row[2]}")
        print(f"  URL: {row[3]}")
        print(f"  Command: {row[4]}")
    else:
        print("Verification failed - server not found.")
        
except Exception as e:
    print(f"Error updating database: {e}")
finally:
    conn.close()

print("\nDatabase fix completed.")
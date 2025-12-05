import sqlite3
import os

# Connect to the database
db_path = os.path.join("backend", "db.sqlite3")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if the mcp_servers table exists
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mcp_servers';")
    table_exists = cursor.fetchone()
    
    if table_exists:
        print("MCP servers table exists.")
        
        # Check if there's a server with the name "Docker MCP Toolkit"
        cursor.execute("SELECT server_id, name, transport_type, url, command FROM mcp_servers WHERE name = 'Docker MCP Toolkit';")
        rows = cursor.fetchall()
        
        if rows:
            print(f"Found {len(rows)} server(s) named 'Docker MCP Toolkit':")
            for row in rows:
                print(f"  Server ID: {row[0]}")
                print(f"  Name: {row[1]}")
                print(f"  Transport Type: {row[2]}")
                print(f"  URL: {row[3]}")
                print(f"  Command: {row[4]}")
                
                # Update the server to use HTTP transport
                cursor.execute("""
                    UPDATE mcp_servers 
                    SET transport_type = 'http', 
                        url = 'http://localhost:3000', 
                        command = NULL,
                        auth_token = 'my-test-token-123'
                    WHERE server_id = ?;
                """, (row[0],))
                
                print(f"  Updated server {row[0]} to use HTTP transport.")
            conn.commit()
        else:
            print("No server named 'Docker MCP Toolkit' found in database.")
            
            # Insert a new record for the Docker MCP Toolkit
            cursor.execute("""
                INSERT INTO mcp_servers (server_id, name, transport_type, url, auth_token, status)
                VALUES (?, ?, ?, ?, ?, ?);
            """, ('mcp_fixed_server', 'Docker MCP Toolkit', 'http', 'http://localhost:3000', 'my-test-token-123', 'inactive'))
            
            print("Inserted new server record for Docker MCP Toolkit.")
            conn.commit()
    else:
        print("MCP servers table does not exist.")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()

print("Database fix script completed.")
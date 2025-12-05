import sqlite3
import os

# Connect to the database
db_path = os.path.join("backend", "agents.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query the MCP servers table
cursor.execute("SELECT server_id, name, transport_type, url, command FROM mcp_servers;")
rows = cursor.fetchall()

print("MCP Servers in Database:")
print("-" * 80)
for row in rows:
    print(f"Server ID: {row[0]}")
    print(f"Name: {row[1]}")
    print(f"Transport Type: {row[2]}")
    print(f"URL: {row[3]}")
    print(f"Command: {row[4]}")
    print("-" * 80)

conn.close()
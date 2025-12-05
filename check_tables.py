import sqlite3

# Connect to the database
conn = sqlite3.connect('backend/agents.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in database:")
for table in tables:
    print(f"  {table[0]}")

conn.close()
import sqlite3

# Connect to the database
conn = sqlite3.connect('agents.db')
cursor = conn.cursor()

# Query for the specific agent
cursor.execute("SELECT agent_id, name, llm_provider, llm_model FROM agents WHERE agent_id='e47bb822-c599-4df9-b632-4430b2f4af7b'")
results = cursor.fetchall()

print('Specific agent:')
for row in results:
    print(f'  ID: {row[0]}, Name: {row[1]}, Provider: {row[2]}, Model: "{row[3]}"')

conn.close()
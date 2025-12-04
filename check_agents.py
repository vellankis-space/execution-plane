import sqlite3

# Connect to the database
conn = sqlite3.connect('agents.db')
cursor = conn.cursor()

# Query agents
cursor.execute('SELECT agent_id, name, llm_provider, llm_model FROM agents')
results = cursor.fetchall()

print('Agents in database:')
for row in results:
    print(f'  ID: {row[0]}, Name: {row[1]}, Provider: {row[2]}, Model: {row[3]}')

conn.close()
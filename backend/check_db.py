from core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('PRAGMA table_info(agents)'))
    columns = [(row[1], row[2]) for row in result]
    print('Columns in agents table:')
    for name, type in columns:
        print(f'  {name}: {type}')
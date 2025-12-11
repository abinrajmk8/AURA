import sqlite3
import pandas as pd

conn = sqlite3.connect("database/aura.db")
df = pd.read_sql_query("SELECT * FROM alerts ORDER BY id DESC LIMIT 5", conn)
print(df)
conn.close()

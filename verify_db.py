import sqlite3
import pandas as pd

conn = sqlite3.connect("database/aura.db")
df = pd.read_sql_query("SELECT * FROM alerts", conn)
print(df)
conn.close()

import sqlite3
import json

conn = sqlite3.connect('database/aura.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get table info
cursor.execute('PRAGMA table_info(alerts)')
columns = [row[1] for row in cursor.fetchall()]
print("Columns:", columns)
print()

# Get sample data
cursor.execute('SELECT * FROM alerts LIMIT 5')
alerts = [dict(row) for row in cursor.fetchall()]
print("Sample alerts:")
print(json.dumps(alerts, indent=2, default=str))
print()

# Get alert type counts
cursor.execute('SELECT alert_type, COUNT(*) as count FROM alerts GROUP BY alert_type')
stats = {row['alert_type']: row['count'] for row in cursor.fetchall()}
print("Alert type stats:")
print(json.dumps(stats, indent=2))

conn.close()

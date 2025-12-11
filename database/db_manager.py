import sqlite3
import json
import os
from datetime import datetime

class DBManager:
    def __init__(self, db_path="database/aura.db", schema_path="database/schema.sql"):
        self.db_path = db_path
        self.schema_path = schema_path
        self._init_db()

    def _init_db(self):
        """Initialize the database with schema if it doesn't exist."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load schema
        if os.path.exists(self.schema_path):
            with open(self.schema_path, 'r') as f:
                schema = f.read()
                cursor.executescript(schema)
        
        conn.commit()
        conn.close()

    def log_alert(self, src_ip, alert_type, description, payload=None, action="BLOCKED", dst_ip=None):
        """Log an IDS alert to the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
                INSERT INTO alerts (src_ip, dst_ip, alert_type, description, payload, action_taken)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (src_ip, dst_ip, alert_type, description, payload, action))
            
            conn.commit()
            conn.close()
            # print(f"[DB] Alert logged: {alert_type} from {src_ip}")
        except Exception as e:
            print(f"[DB] Error logging alert: {e}")

    def log_flow(self, src_ip, dst_ip, dst_port, protocol, features, label="UNKNOWN"):
        """Log flow features for retraining."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert features list to JSON string
            features_json = json.dumps(features)
            
            query = """
                INSERT INTO flows (src_ip, dst_ip, dst_port, protocol, features, label)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (src_ip, dst_ip, dst_port, protocol, features_json, label))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[DB] Error logging flow: {e}")

    def fetch_recent_alerts(self, limit=10):
        """Fetch recent alerts for display."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row # Access columns by name
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"[DB] Error fetching alerts: {e}")
            return []

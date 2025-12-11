import sqlite3
import os

DB_PATH = "database/aura.db"

def init_service_status_table():
    """Create service_status table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create service_status table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_status (
            service_name TEXT PRIMARY KEY,
            enabled INTEGER DEFAULT 0,
            pid INTEGER DEFAULT NULL,
            last_started DATETIME DEFAULT NULL,
            last_stopped DATETIME DEFAULT NULL,
            uptime_seconds INTEGER DEFAULT 0,
            status TEXT DEFAULT 'inactive',
            error_message TEXT DEFAULT NULL
        )
    """)
    
    # Insert default services if they don't exist
    services = ['ids', 'osint', 'honeypot']
    for service in services:
        cursor.execute("""
            INSERT OR IGNORE INTO service_status (service_name, enabled, status)
            VALUES (?, 0, 'inactive')
        """, (service,))
    
    conn.commit()
    conn.close()
    print("✓ Service status table initialized")

if __name__ == "__main__":
    init_service_status_table()

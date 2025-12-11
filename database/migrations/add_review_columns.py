#!/usr/bin/env python3
"""
Database migration script to add review-related columns to the alerts table.
This enables proper tracking of alert reviews for ML model retraining.
"""

import sqlite3
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

DB_PATH = "database/aura.db"

def migrate():
    """Add review columns to alerts table."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("Starting migration: Adding review columns to alerts table...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(alerts)")
        columns = [row[1] for row in cursor.fetchall()]
        
        migrations = []
        
        if 'reviewed' not in columns:
            migrations.append(("reviewed", "ALTER TABLE alerts ADD COLUMN reviewed BOOLEAN DEFAULT 0"))
        
        if 'review_status' not in columns:
            migrations.append(("review_status", "ALTER TABLE alerts ADD COLUMN review_status TEXT DEFAULT 'pending'"))
        
        if 'reviewed_by' not in columns:
            migrations.append(("reviewed_by", "ALTER TABLE alerts ADD COLUMN reviewed_by TEXT"))
        
        if 'reviewed_at' not in columns:
            migrations.append(("reviewed_at", "ALTER TABLE alerts ADD COLUMN reviewed_at DATETIME"))
        
        if 'review_notes' not in columns:
            migrations.append(("review_notes", "ALTER TABLE alerts ADD COLUMN review_notes TEXT"))
        
        # Execute migrations
        for col_name, sql in migrations:
            print(f"  Adding column: {col_name}")
            cursor.execute(sql)
        
        conn.commit()
        
        if migrations:
            print(f"✓ Migration completed successfully! Added {len(migrations)} columns.")
        else:
            print("✓ All columns already exist. No migration needed.")
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(alerts)")
        print("\nCurrent alerts table schema:")
        for row in cursor.fetchall():
            print(f"  {row[1]} ({row[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)

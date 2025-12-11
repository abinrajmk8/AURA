from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

app = Flask(__name__)
CORS(app)  # Enable CORS for React dev server

DB_PATH = "database/aura.db"

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/alerts/recent', methods=['GET'])
def get_recent_alerts():
    """Get last 50 alerts."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, src_ip, alert_type, description, action_taken
            FROM alerts
            ORDER BY id DESC
            LIMIT 50
        """)
        alerts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(alerts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard overview statistics."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Total threats
        cursor.execute("SELECT COUNT(*) as total FROM alerts")
        total_threats = cursor.fetchone()['total']
        
        # Active alerts (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) as active 
            FROM alerts 
            WHERE timestamp >= datetime('now', '-24 hours')
        """)
        active_alerts = cursor.fetchone()['active']
        
        # Blocked attacks
        cursor.execute("""
            SELECT COUNT(*) as blocked 
            FROM alerts 
            WHERE action_taken = 'BLOCKED'
        """)
        blocked_attacks = cursor.fetchone()['blocked']
        
        # System health (percentage of successful blocks)
        health = (blocked_attacks / total_threats * 100) if total_threats > 0 else 100
        
        conn.close()
        
        return jsonify({
            "total_threats": total_threats,
            "active_alerts": active_alerts,
            "blocked_attacks": blocked_attacks,
            "system_health": int(health)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get formatted alerts for alerts panel."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, src_ip, alert_type, 
                   severity, description, action_taken
            FROM alerts
            ORDER BY id DESC
            LIMIT 10
        """)
        
        alerts = []
        for row in cursor.fetchall():
            # Calculate relative time
            try:
                alert_time = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                time_diff = datetime.now() - alert_time
                
                if time_diff.total_seconds() < 60:
                    time_str = f"{int(time_diff.total_seconds())} seconds ago"
                elif time_diff.total_seconds() < 3600:
                    time_str = f"{int(time_diff.total_seconds() // 60)} minutes ago"
                elif time_diff.days == 0:
                    time_str = f"{int(time_diff.total_seconds() // 3600)} hours ago"
                else:
                    time_str = f"{time_diff.days} days ago"
            except:
                time_str = row['timestamp']
            
            # Map to frontend format
            alerts.append({
                "id": row['id'],
                "severity": row['severity'].lower() if row['severity'] else 'medium',
                "title": row['alert_type'].replace('_', ' ').title() if row['alert_type'] else 'Alert',
                "description": row['description'] or 'No description',
                "timestamp": time_str,
                "source": "IDS" if row['alert_type'] == 'OSINT' else "Honeypot"
            })
        
        conn.close()
        return jsonify({"alerts": alerts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get attack statistics by type."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Count by alert type
        cursor.execute("""
            SELECT alert_type, COUNT(*) as count
            FROM alerts
            GROUP BY alert_type
        """)
        stats = {row['alert_type']: row['count'] for row in cursor.fetchall()}
        
        # Total alerts
        cursor.execute("SELECT COUNT(*) as total FROM alerts")
        total = cursor.fetchone()['total']
        
        conn.close()
        return jsonify({
            "total": total,
            "by_type": stats
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/timeline', methods=['GET'])
def get_timeline():
    """Get alerts over time (last 24 hours, grouped by hour)."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get alerts from last 24 hours
        cursor.execute("""
            SELECT 
                strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                COUNT(*) as count
            FROM alerts
            WHERE timestamp >= datetime('now', '-24 hours')
            GROUP BY hour
            ORDER BY hour
        """)
        timeline = [{"time": row['hour'], "count": row['count']} for row in cursor.fetchall()]
        
        conn.close()
        return jsonify(timeline)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def get_health():
    """Get system health status."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if we have recent alerts (last 5 minutes)
        cursor.execute("""
            SELECT COUNT(*) as recent_count
            FROM alerts
            WHERE timestamp >= datetime('now', '-5 minutes')
        """)
        recent = cursor.fetchone()['recent_count']
        
        conn.close()
        
        return jsonify({
            "ids_status": "active",
            "honeypot_status": "active",
            "database_status": "connected",
            "recent_activity": recent > 0
        })
    except Exception as e:
        return jsonify({
            "ids_status": "unknown",
            "honeypot_status": "unknown",
            "database_status": "error",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import service controller
from dashboard.api.service_controller import ServiceController

app = Flask(__name__)
CORS(app)  # Enable CORS for React dev server

DB_PATH = "database/aura.db"

# Initialize service controller
service_controller = ServiceController()

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

# ========================================
# Service Control Endpoints
# ========================================

@app.route('/api/control/<service>/start', methods=['POST'])
def start_service(service):
    """Start a service (ids, osint, honeypot)"""
    try:
        result = service_controller.start_service(service)
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/control/<service>/stop', methods=['POST'])
def stop_service(service):
    """Stop a service (ids, osint, honeypot)"""
    try:
        result = service_controller.stop_service(service)
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/status/all', methods=['GET'])
def get_all_status():
    """Get status of all services"""
    try:
        status = service_controller.get_all_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status/<service>', methods=['GET'])
def get_service_status(service):
    """Get status of a specific service"""
    try:
        status = service_controller.get_status(service)
        if status:
            return jsonify(status), 200
        else:
            return jsonify({"error": "Unknown service"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/osint/search', methods=['POST'])
def osint_search():
    """Trigger OSINT search with custom parameters"""
    try:
        import subprocess
        
        data = request.json
        keyword = data.get('keyword', '')
        severity = data.get('severity', '')
        live = data.get('live', False)
        poc = data.get('poc', False)
        correlate = data.get('correlate', False)
        forecast = data.get('forecast', False)
        
        # Build command
        cmd = ['python3', 'osint-harvester/main.py']
        
        if keyword:
            cmd.extend(['--keyword', keyword])
        if severity:
            cmd.extend(['--severity', severity])
        if live:
            cmd.append('--live')
        if poc:
            cmd.append('--poc')
        if correlate:
            cmd.append('--correlate')
        if forecast:
            cmd.append('--forecast')
        
        # Run OSINT harvester in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )
        
        return jsonify({
            "success": True,
            "message": "OSINT search started",
            "pid": process.pid,
            "parameters": {
                "keyword": keyword or "All CVEs",
                "severity": severity or "All",
                "live": live,
                "poc": poc,
                "correlate": correlate,
                "forecast": forecast
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/osint/results', methods=['GET'])
def get_osint_results():
    """Get latest OSINT search results"""
    try:
        import json
        from pathlib import Path
        
        results = {
            "cves": [],
            "reddit": [],
            "github": [],
            "cisa": [],
            "forecast": []
        }
        
        # Load CVEs
        cve_file = Path("data/latest_cves.json")
        if cve_file.exists():
            with open(cve_file, 'r') as f:
                results["cves"] = json.load(f)[:20]  # Limit to 20
        
        # Load Reddit posts
        reddit_file = Path("data/reddit_posts.json")
        if reddit_file.exists():
            with open(reddit_file, 'r') as f:
                results["reddit"] = json.load(f)[:10]
        
        # Load GitHub repos
        github_file = Path("data/github_repos.json")
        if github_file.exists():
            with open(github_file, 'r') as f:
                results["github"] = json.load(f)[:10]
        
        # Load CISA vulnerabilities
        cisa_file = Path("data/cisa_vulns.json")
        if cisa_file.exists():
            with open(cisa_file, 'r') as f:
                results["cisa"] = json.load(f)[:10]
        
        # Load forecast
        forecast_file = Path("data/forecast.json")
        if forecast_file.exists():
            with open(forecast_file, 'r') as f:
                results["forecast"] = json.load(f)[:5]
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========================================
# Assessment Management Endpoints
# ========================================

@app.route('/api/alerts/assess', methods=['GET'])
def get_alerts_for_assessment():
    """Get alerts with pagination and filtering for review."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        status = request.args.get('status', '')  # pending, approved, rejected, false_positive
        severity = request.args.get('severity', '')
        alert_type = request.args.get('alert_type', '')
        search = request.args.get('search', '')
        
        # Build WHERE clause
        where_clauses = []
        params = []
        
        if status:
            where_clauses.append("review_status = ?")
            params.append(status)
        
        if severity:
            where_clauses.append("severity = ?")
            params.append(severity.upper())
        
        if alert_type:
            where_clauses.append("alert_type = ?")
            params.append(alert_type)
        
        if search:
            where_clauses.append("(src_ip LIKE ? OR description LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Get total count (grouped)
        cursor.execute(f"""
            SELECT COUNT(*) as total FROM (
                SELECT 1
                FROM alerts
                WHERE {where_sql}
                GROUP BY src_ip, alert_type, severity, review_status, action_taken, description
            )
        """, params)
        total = cursor.fetchone()['total']
        
        # Get paginated results (grouped)
        offset = (page - 1) * per_page
        cursor.execute(f"""
            SELECT MAX(id) as id, MAX(timestamp) as timestamp, src_ip, dst_ip, alert_type, severity, 
                   description, payload, action_taken, reviewed, review_status,
                   reviewed_by, reviewed_at, review_notes, COUNT(*) as count
            FROM alerts
            WHERE {where_sql}
            GROUP BY src_ip, alert_type, severity, review_status, action_taken, description
            ORDER BY MAX(id) DESC
            LIMIT ? OFFSET ?
        """, params + [per_page, offset])
        
        alerts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            "alerts": alerts,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/alerts/assess/<int:alert_id>', methods=['GET'])
def get_alert_detail_for_assessment(alert_id):
    """Get detailed information for a specific alert."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, src_ip, dst_ip, alert_type, severity,
                   description, payload, action_taken, reviewed, review_status,
                   reviewed_by, reviewed_at, review_notes
            FROM alerts
            WHERE id = ?
        """, (alert_id,))
        
        alert = cursor.fetchone()
        conn.close()
        
        if alert:
            return jsonify(dict(alert)), 200
        else:
            return jsonify({"error": "Alert not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/alerts/assess/<int:alert_id>', methods=['PUT'])
def update_alert_assessment(alert_id):
    """Update review status of an alert."""
    try:
        data = request.json
        review_status = data.get('review_status')  # approved, rejected, false_positive
        review_notes = data.get('review_notes', '')
        reviewed_by = data.get('reviewed_by', 'admin')
        
        if review_status not in ['approved', 'rejected', 'false_positive']:
            return jsonify({"error": "Invalid review status"}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Get details of the alert being updated
        cursor.execute("SELECT src_ip, alert_type, description FROM alerts WHERE id = ?", (alert_id,))
        alert_details = cursor.fetchone()
        
        if alert_details:
            # Update all similar pending alerts
            cursor.execute("""
                UPDATE alerts
                SET reviewed = 1,
                    review_status = ?,
                    reviewed_by = ?,
                    reviewed_at = CURRENT_TIMESTAMP,
                    review_notes = ?
                WHERE src_ip = ? 
                AND alert_type = ? 
                AND description = ?
                AND review_status = 'pending'
            """, (review_status, reviewed_by, review_notes, alert_details['src_ip'], alert_details['alert_type'], alert_details['description']))
            
            # Also ensure the specific ID is updated even if it wasn't pending (though it should be)
            cursor.execute("""
                UPDATE alerts
                SET reviewed = 1,
                    review_status = ?,
                    reviewed_by = ?,
                    reviewed_at = CURRENT_TIMESTAMP,
                    review_notes = ?
                WHERE id = ?
            """, (review_status, reviewed_by, review_notes, alert_id))
        else:
            # Fallback for single update if not found (shouldn't happen)
            cursor.execute("""
                UPDATE alerts
                SET reviewed = 1,
                    review_status = ?,
                    reviewed_by = ?,
                    reviewed_at = CURRENT_TIMESTAMP,
                    review_notes = ?
                WHERE id = ?
            """, (review_status, reviewed_by, review_notes, alert_id))
        
        conn.commit()
        
        # --- Save to CSV for Training ---
        try:
            import csv
            import os
            
            csv_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'alerts.csv')
            os.makedirs(os.path.dirname(csv_file), exist_ok=True)
            
            file_exists = os.path.isfile(csv_file)
            
            # Get the updated alerts to write to CSV
            if alert_details:
                cursor.execute("""
                    SELECT timestamp, src_ip, dst_ip, alert_type, severity, description, payload, review_status
                    FROM alerts
                    WHERE src_ip = ? AND alert_type = ? AND description = ? AND review_status = ?
                """, (alert_details['src_ip'], alert_details['alert_type'], alert_details['description'], review_status))
            else:
                cursor.execute("""
                    SELECT timestamp, src_ip, dst_ip, alert_type, severity, description, payload, review_status
                    FROM alerts
                    WHERE id = ?
                """, (alert_id,))
                
            updated_alerts = cursor.fetchall()
            
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['timestamp', 'src_ip', 'dst_ip', 'alert_type', 'severity', 'description', 'payload', 'label'])
                
                for alert in updated_alerts:
                    writer.writerow([
                        alert['timestamp'],
                        alert['src_ip'],
                        alert['dst_ip'],
                        alert['alert_type'],
                        alert['severity'],
                        alert['description'],
                        alert['payload'],
                        alert['review_status']
                    ])
                    
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Alert {alert_id} marked as {review_status}"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/alerts/assess/bulk', methods=['PUT'])
def bulk_update_assessment():
    """Bulk update review status for multiple alerts."""
    try:
        data = request.json
        alert_ids = data.get('alert_ids', [])
        review_status = data.get('review_status')
        reviewed_by = data.get('reviewed_by', 'admin')
        
        if not alert_ids:
            return jsonify({"error": "No alert IDs provided"}), 400
        
        if review_status not in ['approved', 'rejected', 'false_positive']:
            return jsonify({"error": "Invalid review status"}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(alert_ids))
        cursor.execute(f"""
            UPDATE alerts
            SET reviewed = 1,
                review_status = ?,
                reviewed_by = ?,
                reviewed_at = CURRENT_TIMESTAMP
            WHERE id IN ({placeholders})
        """, [review_status, reviewed_by] + alert_ids)
        
        updated_count = cursor.rowcount
        conn.commit()
        
        # --- Save to CSV for Training ---
        try:
            import csv
            import os
            
            csv_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'alerts.csv')
            os.makedirs(os.path.dirname(csv_file), exist_ok=True)
            
            file_exists = os.path.isfile(csv_file)
            
            # Get the updated alerts to write to CSV
            cursor.execute(f"""
                SELECT timestamp, src_ip, dst_ip, alert_type, severity, description, payload, review_status
                FROM alerts
                WHERE id IN ({placeholders})
            """, alert_ids)
            
            updated_alerts = cursor.fetchall()
            
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['timestamp', 'src_ip', 'dst_ip', 'alert_type', 'severity', 'description', 'payload', 'label'])
                
                for alert in updated_alerts:
                    writer.writerow([
                        alert['timestamp'],
                        alert['src_ip'],
                        alert['dst_ip'],
                        alert['alert_type'],
                        alert['severity'],
                        alert['description'],
                        alert['payload'],
                        alert['review_status']
                    ])
                    
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Updated {updated_count} alerts to {review_status}"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/alerts/stats/assess', methods=['GET'])
def get_assessment_stats():
    """Get review statistics."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Count by review status
        cursor.execute("""
            SELECT review_status, COUNT(*) as count
            FROM alerts
            GROUP BY review_status
        """)
        stats = {row['review_status']: row['count'] for row in cursor.fetchall()}
        
        # Total alerts
        cursor.execute("SELECT COUNT(*) as total FROM alerts")
        total = cursor.fetchone()['total']
        
        conn.close()
        
        return jsonify({
            "total": total,
            "pending": stats.get('pending', 0),
            "approved": stats.get('approved', 0),
            "rejected": stats.get('rejected', 0),
            "false_positive": stats.get('false_positive', 0)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/alerts/export/assessed', methods=['GET'])
def export_assessed_alerts():
    """Export reviewed alerts for ML model retraining."""
    try:
        import csv
        from io import StringIO
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Get only reviewed alerts
        cursor.execute("""
            SELECT id, timestamp, src_ip, dst_ip, alert_type, severity,
                   description, payload, action_taken, review_status,
                   reviewed_by, reviewed_at, review_notes
            FROM alerts
            WHERE reviewed = 1
            ORDER BY reviewed_at DESC
        """)
        
        alerts = cursor.fetchall()
        conn.close()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'id', 'timestamp', 'src_ip', 'dst_ip', 'alert_type', 'severity',
            'description', 'payload', 'action_taken', 'review_status',
            'reviewed_by', 'reviewed_at', 'review_notes'
        ])
        
        # Write data
        for alert in alerts:
            writer.writerow(alert)
        
        csv_data = output.getvalue()
        
        return jsonify({
            "success": True,
            "data": csv_data,
            "count": len(alerts)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

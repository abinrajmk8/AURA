"""
Service Controller for AURA
Manages IDS, OSINT, and Honeypot services
"""
import subprocess
import psutil
import json
import os
from datetime import datetime
from pathlib import Path

# Status file directory
STATUS_DIR = Path("dashboard/api/status")
STATUS_DIR.mkdir(parents=True, exist_ok=True)

class ServiceController:
    def __init__(self):
        self.services = {
            'ids': {
                'name': 'IDS',
                'script': 'IDS/main.py',
                'status_file': STATUS_DIR / 'ids.json'
            },
            'osint': {
                'name': 'OSINT',
                'script': 'osint-harvester/main.py',
                'status_file': STATUS_DIR / 'osint.json'
            },
            'honeypot': {
                'name': 'Honeypot',
                'script': 'HONEYPOT/log_bridge.py',
                'status_file': STATUS_DIR / 'honeypot.json'
            }
        }
        
        # Load existing status
        for service_id in self.services:
            self._load_status(service_id)
    
    def _load_status(self, service_id):
        """Load service status from file"""
        status_file = self.services[service_id]['status_file']
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    status = json.load(f)
                    # Check if PID is still valid
                    if status.get('pid') and not psutil.pid_exists(status['pid']):
                        status['enabled'] = False
                        status['status'] = 'inactive'
                        status['pid'] = None
                        self._save_status(service_id, status)
                    return status
            except:
                pass
        
        # Default status
        return {
            'enabled': False,
            'status': 'inactive',
            'pid': None,
            'last_started': None,
            'uptime': '0s'
        }
    
    def _save_status(self, service_id, status):
        """Save service status to file"""
        status_file = self.services[service_id]['status_file']
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
    
    def start_service(self, service_id):
        """Start a service"""
        if service_id not in self.services:
            return {'success': False, 'error': 'Unknown service'}
        
        status = self._load_status(service_id)
        
        # Check if already running
        if status['enabled'] and status.get('pid') and psutil.pid_exists(status['pid']):
            return {'success': False, 'error': 'Service already running'}
        
        try:
            script_path = self.services[service_id]['script']
            
            # Start the service as a background process
            process = subprocess.Popen(
                ['python3', script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Update status
            status = {
                'enabled': True,
                'status': 'active',
                'pid': process.pid,
                'last_started': datetime.now().isoformat(),
                'uptime': '0s'
            }
            self._save_status(service_id, status)
            
            return {
                'success': True,
                'message': f'{self.services[service_id]["name"]} started',
                'pid': process.pid
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def stop_service(self, service_id):
        """Stop a service"""
        if service_id not in self.services:
            return {'success': False, 'error': 'Unknown service'}
        
        status = self._load_status(service_id)
        
        if not status.get('pid'):
            return {'success': False, 'error': 'Service not running'}
        
        try:
            # Kill the process
            if psutil.pid_exists(status['pid']):
                process = psutil.Process(status['pid'])
                process.terminate()
                process.wait(timeout=5)
            
            # Update status
            status = {
                'enabled': False,
                'status': 'inactive',
                'pid': None,
                'last_stopped': datetime.now().isoformat(),
                'uptime': '0s'
            }
            self._save_status(service_id, status)
            
            return {
                'success': True,
                'message': f'{self.services[service_id]["name"]} stopped'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_status(self, service_id):
        """Get service status with metrics from database"""
        if service_id not in self.services:
            return None
        
        status = self._load_status(service_id)
        
        # Calculate uptime if running
        if status['enabled'] and status.get('last_started'):
            try:
                start_time = datetime.fromisoformat(status['last_started'])
                uptime_seconds = (datetime.now() - start_time).total_seconds()
                
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                seconds = int(uptime_seconds % 60)
                
                if days > 0:
                    status['uptime'] = f"{days}d {hours}h {minutes}m"
                elif hours > 0:
                    status['uptime'] = f"{hours}h {minutes}m"
                elif minutes > 0:
                    status['uptime'] = f"{minutes}m {seconds}s"
                else:
                    status['uptime'] = f"{seconds}s"
            except:
                status['uptime'] = 'Not running'
        else:
            status['uptime'] = 'Not running'
        
        # Get detection count and last activity from database
        try:
            import sqlite3
            conn = sqlite3.connect('database/aura.db')
            cursor = conn.cursor()
            
            # Map service_id to alert_type prefix
            alert_type_map = {
                'ids': ['ML', 'OSINT', 'JA3', 'HEURISTIC'],
                'osint': ['OSINT'],
                'honeypot': ['HONEYPOT']
            }
            
            alert_types = alert_type_map.get(service_id, [])
            
            if alert_types:
                # Build query for detection count
                placeholders = ','.join('?' * len(alert_types))
                like_conditions = ' OR '.join([f"alert_type LIKE ?" for _ in alert_types])
                like_params = [f"{t}%" for t in alert_types]
                
                # Get total detections
                cursor.execute(f"""
                    SELECT COUNT(*) as count
                    FROM alerts
                    WHERE {like_conditions}
                """, like_params)
                
                result = cursor.fetchone()
                status['detection_count'] = result[0] if result else 0
                
                # Get last activity
                cursor.execute(f"""
                    SELECT timestamp
                    FROM alerts
                    WHERE {like_conditions}
                    ORDER BY id DESC
                    LIMIT 1
                """, like_params)
                
                result = cursor.fetchone()
                if result:
                    last_time = datetime.fromisoformat(result[0])
                    time_diff = (datetime.now() - last_time).total_seconds()
                    
                    if time_diff < 60:
                        status['last_activity'] = f"{int(time_diff)}s ago"
                    elif time_diff < 3600:
                        status['last_activity'] = f"{int(time_diff / 60)}m ago"
                    elif time_diff < 86400:
                        status['last_activity'] = f"{int(time_diff / 3600)}h ago"
                    else:
                        status['last_activity'] = f"{int(time_diff / 86400)}d ago"
                else:
                    status['last_activity'] = 'No activity'
            else:
                status['detection_count'] = 0
                status['last_activity'] = 'N/A'
            
            conn.close()
        except Exception as e:
            print(f"Error fetching metrics: {e}")
            status['detection_count'] = 0
            status['last_activity'] = 'N/A'
        
        return status
    
    def get_all_status(self):
        """Get status of all services"""
        return {
            service_id: self.get_status(service_id)
            for service_id in self.services
        }

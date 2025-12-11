import { useState, useEffect } from 'react';
import './RecentActivity.css';

const RecentActivity = () => {
    const [activities, setActivities] = useState([]);

    useEffect(() => {
        const fetchActivities = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/alerts/recent');
                const data = await response.json();

                // Map alerts to activity format
                const mappedActivities = data.slice(0, 6).map(alert => {
                    let icon = '🔔';
                    let type = 'alert';
                    let severity = 'info';

                    // Map based on alert type and action
                    if (alert.action_taken === 'BLOCKED') {
                        icon = '🛡️';
                        type = 'threat_blocked';
                        severity = 'success';
                    } else if (alert.alert_type === 'HONEYPOT_AUTH') {
                        icon = '🚨';
                        type = 'honeypot_alert';
                        severity = 'warning';
                    } else if (alert.alert_type === 'OSINT') {
                        icon = '⚔️';
                        type = 'ids_alert';
                        severity = alert.action_taken === 'BLOCKED' ? 'success' : 'warning';
                    }

                    // Calculate relative time
                    const alertTime = new Date(alert.timestamp);
                    const now = new Date();
                    const diffMs = now - alertTime;
                    const diffMins = Math.floor(diffMs / 60000);
                    const diffHours = Math.floor(diffMins / 60);

                    let timeStr;
                    if (diffMins < 1) {
                        timeStr = 'just now';
                    } else if (diffMins < 60) {
                        timeStr = `${diffMins} min ago`;
                    } else if (diffHours < 24) {
                        timeStr = `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
                    } else {
                        const diffDays = Math.floor(diffHours / 24);
                        timeStr = `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
                    }

                    return {
                        id: alert.id,
                        type: type,
                        icon: icon,
                        title: alert.action_taken === 'BLOCKED' ? 'Threat Blocked' : 'Alert Detected',
                        description: `${alert.description.substring(0, 50)}${alert.description.length > 50 ? '...' : ''} from ${alert.src_ip}`,
                        timestamp: timeStr,
                        severity: severity
                    };
                });

                setActivities(mappedActivities);
            } catch (error) {
                console.error('Error fetching activities:', error);
                // Keep empty or show error state
            }
        };

        fetchActivities();
        const interval = setInterval(fetchActivities, 30000); // Refresh every 30 seconds
        return () => clearInterval(interval);
    }, []);

    const getSeverityClass = (severity) => {
        switch (severity) {
            case 'success': return 'activity-success';
            case 'warning': return 'activity-warning';
            case 'danger': return 'activity-danger';
            case 'info': return 'activity-info';
            default: return 'activity-info';
        }
    };

    return (
        <div className="recent-activity card">
            <div className="panel-header">
                <h3 className="panel-title">Recent Activity</h3>
                <button className="btn btn-ghost btn-sm">View All</button>
            </div>

            <div className="activity-timeline">
                {activities.map((activity, index) => (
                    <div key={activity.id} className={`activity-item ${getSeverityClass(activity.severity)}`}>
                        <div className="activity-line">
                            {index !== activities.length - 1 && <div className="timeline-connector"></div>}
                        </div>
                        <div className="activity-icon">
                            <span>{activity.icon}</span>
                        </div>
                        <div className="activity-content">
                            <div className="activity-header">
                                <h4 className="activity-title">{activity.title}</h4>
                                <span className="activity-time">{activity.timestamp}</span>
                            </div>
                            <p className="activity-description">{activity.description}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default RecentActivity;

import { useState, useEffect } from 'react';
import './AlertsPanel.css';

const AlertsPanel = () => {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch alerts from API
        const fetchAlerts = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/alerts');
                const data = await response.json();
                setAlerts(data.alerts || []);
            } catch (error) {
                console.error('Error fetching alerts:', error);
                // Use mock data if API fails
                setAlerts([
                    {
                        id: 1,
                        severity: 'high',
                        title: 'Suspicious Network Activity',
                        description: 'Multiple failed login attempts detected from IP 192.168.1.100',
                        timestamp: '2 minutes ago',
                        source: 'IDS'
                    },
                    {
                        id: 2,
                        severity: 'critical',
                        title: 'Malware Detected',
                        description: 'Trojan.Generic found in system32 directory',
                        timestamp: '5 minutes ago',
                        source: 'Antivirus'
                    },
                    {
                        id: 3,
                        severity: 'medium',
                        title: 'Unusual Outbound Traffic',
                        description: 'High volume of data transfer to unknown IP',
                        timestamp: '12 minutes ago',
                        source: 'Firewall'
                    },
                    {
                        id: 4,
                        severity: 'low',
                        title: 'Configuration Change',
                        description: 'Security policy updated by admin',
                        timestamp: '1 hour ago',
                        source: 'System'
                    },
                    {
                        id: 5,
                        severity: 'high',
                        title: 'Port Scan Detected',
                        description: 'Sequential port scanning from external source',
                        timestamp: '2 hours ago',
                        source: 'IDS'
                    }
                ]);
            } finally {
                setLoading(false);
            }
        };

        fetchAlerts();
        const interval = setInterval(fetchAlerts, 30000); // Refresh every 30 seconds
        return () => clearInterval(interval);
    }, []);

    const getSeverityClass = (severity) => {
        switch (severity) {
            case 'critical': return 'severity-critical';
            case 'high': return 'severity-high';
            case 'medium': return 'severity-medium';
            case 'low': return 'severity-low';
            default: return 'severity-low';
        }
    };

    const getSeverityIcon = (severity) => {
        switch (severity) {
            case 'critical': return '🚨';
            case 'high': return '⚠️';
            case 'medium': return '⚡';
            case 'low': return 'ℹ️';
            default: return 'ℹ️';
        }
    };

    if (loading) {
        return (
            <div className="alerts-panel card">
                <div className="panel-header">
                    <h3 className="panel-title">Recent Alerts</h3>
                </div>
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Loading alerts...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="alerts-panel card">
            <div className="panel-header">
                <h3 className="panel-title">Recent Alerts</h3>
                <span className="alert-count badge badge-danger">{alerts.length}</span>
            </div>

            <div className="alerts-list">
                {alerts.map((alert) => (
                    <div key={alert.id} className={`alert-item ${getSeverityClass(alert.severity)}`}>
                        <div className="alert-icon">
                            {getSeverityIcon(alert.severity)}
                        </div>
                        <div className="alert-content">
                            <div className="alert-header">
                                <h4 className="alert-title">{alert.title}</h4>
                                <span className="alert-time">{alert.timestamp}</span>
                            </div>
                            <p className="alert-description">{alert.description}</p>
                            <div className="alert-footer">
                                <span className={`alert-badge badge ${getSeverityClass(alert.severity)}`}>
                                    {alert.severity}
                                </span>
                                <span className="alert-source">{alert.source}</span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="panel-footer">
                <button className="btn btn-ghost">View All Alerts →</button>
            </div>
        </div>
    );
};

export default AlertsPanel;

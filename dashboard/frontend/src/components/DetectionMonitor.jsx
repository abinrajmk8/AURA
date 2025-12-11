import { useState, useEffect } from 'react';
import './DetectionMonitor.css';

const DetectionMonitor = () => {
    const [detections, setDetections] = useState([]);
    const [isLive, setIsLive] = useState(true);

    useEffect(() => {
        const fetchDetections = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/alerts/recent');
                const data = await response.json();

                // Map to detection format
                const mappedDetections = data.slice(0, 10).map(alert => ({
                    id: alert.id,
                    service: alert.alert_type === 'OSINT' ? 'IDS' : 'Honeypot',
                    type: alert.alert_type,
                    message: alert.description,
                    ip: alert.src_ip,
                    action: alert.action_taken,
                    timestamp: alert.timestamp,
                    severity: alert.severity?.toLowerCase() || 'medium'
                }));

                setDetections(mappedDetections);
            } catch (error) {
                console.error('Failed to fetch detections:', error);
            }
        };

        fetchDetections();

        if (isLive) {
            const interval = setInterval(fetchDetections, 5000); // Refresh every 5 seconds
            return () => clearInterval(interval);
        }
    }, [isLive]);

    const getServiceIcon = (service) => {
        switch (service) {
            case 'IDS': return '⚔️';
            case 'Honeypot': return '🚨';
            case 'OSINT': return '🔍';
            default: return '🔔';
        }
    };

    const getServiceColor = (service) => {
        switch (service) {
            case 'IDS': return 'service-ids';
            case 'Honeypot': return 'service-honeypot';
            case 'OSINT': return 'service-osint';
            default: return 'service-default';
        }
    };

    const getActionBadge = (action) => {
        if (action === 'BLOCKED') {
            return <span className="action-badge badge-success">🛡️ Blocked</span>;
        } else if (action === 'MONITORED') {
            return <span className="action-badge badge-warning">👁️ Monitored</span>;
        }
        return <span className="action-badge badge-info">ℹ️ Detected</span>;
    };

    return (
        <div className="detection-monitor card">
            <div className="monitor-header">
                <div>
                    <h3 className="panel-title">📡 Live Detection Monitor</h3>
                    <p className="panel-subtitle">Real-time security events from all services</p>
                </div>
                <div className="monitor-controls">
                    <button
                        className={`live-indicator ${isLive ? 'live-active' : ''}`}
                        onClick={() => setIsLive(!isLive)}
                    >
                        <span className="live-dot"></span>
                        {isLive ? 'LIVE' : 'PAUSED'}
                    </button>
                </div>
            </div>

            <div className="detections-list">
                {detections.length > 0 ? (
                    detections.map((detection) => (
                        <div key={detection.id} className={`detection-item ${getServiceColor(detection.service)}`}>
                            <div className="detection-icon">
                                {getServiceIcon(detection.service)}
                            </div>
                            <div className="detection-content">
                                <div className="detection-header">
                                    <span className="detection-service">{detection.service}</span>
                                    <span className="detection-time">{detection.timestamp}</span>
                                </div>
                                <p className="detection-message">{detection.message}</p>
                                <div className="detection-footer">
                                    <span className="detection-ip">
                                        <span className="ip-label">IP:</span>
                                        <code>{detection.ip}</code>
                                    </span>
                                    {getActionBadge(detection.action)}
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="no-detections">
                        <span className="no-detections-icon">📡</span>
                        <p>No recent detections</p>
                        <span className="no-detections-subtitle">Monitoring for threats...</span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default DetectionMonitor;

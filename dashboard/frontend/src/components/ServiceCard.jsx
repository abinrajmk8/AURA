import { useState } from 'react';
import './ServiceCard.css';

const ServiceCard = ({
    serviceName,
    status,
    uptime,
    lastActivity,
    detectionCount,
    icon,
    onToggle,
    onRestart,
    metrics
}) => {
    const [isEnabled, setIsEnabled] = useState(status === 'active');
    const [isLoading, setIsLoading] = useState(false);

    const handleToggle = async () => {
        setIsLoading(true);
        try {
            await onToggle(!isEnabled);
            setIsEnabled(!isEnabled);
        } catch (error) {
            console.error('Failed to toggle service:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleRestart = async () => {
        setIsLoading(true);
        try {
            await onRestart();
        } catch (error) {
            console.error('Failed to restart service:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const getStatusClass = () => {
        if (isLoading) return 'status-loading';
        if (!isEnabled) return 'status-inactive';
        if (status === 'error') return 'status-error';
        return 'status-active';
    };

    const getStatusText = () => {
        if (isLoading) return 'Loading...';
        if (!isEnabled) return 'Inactive';
        if (status === 'error') return 'Error';
        return 'Active';
    };

    return (
        <div className={`service-card ${getStatusClass()}`}>
            <div className="service-header">
                <div className="service-icon">{icon}</div>
                <div className="service-title-section">
                    <h3 className="service-title">{serviceName}</h3>
                    <div className="service-status">
                        <span className={`status-dot ${getStatusClass()}`}></span>
                        <span className="status-text">{getStatusText()}</span>
                    </div>
                </div>
            </div>

            <div className="service-metrics">
                <div className="metric">
                    <span className="metric-label">Uptime</span>
                    <span className="metric-value">{uptime || 'N/A'}</span>
                </div>
                <div className="metric">
                    <span className="metric-label">Detections</span>
                    <span className="metric-value">{detectionCount || 0}</span>
                </div>
                {lastActivity && (
                    <div className="metric">
                        <span className="metric-label">Last Activity</span>
                        <span className="metric-value">{lastActivity}</span>
                    </div>
                )}
            </div>

            {metrics && (
                <div className="service-stats">
                    {Object.entries(metrics).map(([key, value]) => (
                        <div key={key} className="stat-item">
                            <span className="stat-label">{key}</span>
                            <span className="stat-value">{value}</span>
                        </div>
                    ))}
                </div>
            )}

            <div className="service-controls">
                <div className="toggle-control">
                    <label className="toggle-switch">
                        <input
                            type="checkbox"
                            checked={isEnabled}
                            onChange={handleToggle}
                            disabled={isLoading}
                        />
                        <span className="toggle-slider"></span>
                    </label>
                    <span className="toggle-label">
                        {isEnabled ? 'Enabled' : 'Disabled'}
                    </span>
                </div>
                <div className="action-buttons">
                    <button
                        className="btn btn-secondary btn-sm"
                        onClick={handleRestart}
                        disabled={isLoading || !isEnabled}
                    >
                        ⟳ Restart
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ServiceCard;

import { useState, useEffect } from 'react';
import './ThreatMap.css';

const ThreatMap = () => {
    const [threats, setThreats] = useState([]);

    useEffect(() => {
        // Mock threat data - in production, this would come from the API
        const mockThreats = [
            { id: 1, country: 'Russia', count: 45, severity: 'high', lat: 55, lng: 37 },
            { id: 2, country: 'China', count: 32, severity: 'critical', lat: 35, lng: 105 },
            { id: 3, country: 'USA', count: 18, severity: 'medium', lat: 37, lng: -95 },
            { id: 4, country: 'Brazil', count: 12, severity: 'low', lat: -14, lng: -51 },
            { id: 5, country: 'Germany', count: 8, severity: 'medium', lat: 51, lng: 10 },
        ];
        setThreats(mockThreats);
    }, []);

    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'critical': return '#ef4444';
            case 'high': return '#f59e0b';
            case 'medium': return '#06b6d4';
            case 'low': return '#6b7280';
            default: return '#6b7280';
        }
    };

    return (
        <div className="threat-map card">
            <div className="panel-header">
                <h3 className="panel-title">Global Threat Map</h3>
                <span className="live-indicator">
                    <span className="live-dot"></span>
                    Live
                </span>
            </div>

            <div className="map-container">
                <div className="world-map">
                    <div className="map-overlay">
                        {threats.map((threat) => (
                            <div
                                key={threat.id}
                                className="threat-marker"
                                style={{
                                    left: `${((threat.lng + 180) / 360) * 100}%`,
                                    top: `${((90 - threat.lat) / 180) * 100}%`,
                                }}
                            >
                                <div
                                    className="marker-pulse"
                                    style={{ backgroundColor: getSeverityColor(threat.severity) }}
                                ></div>
                                <div className="marker-tooltip">
                                    <strong>{threat.country}</strong>
                                    <span>{threat.count} threats</span>
                                    <span className="tooltip-severity">{threat.severity}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="map-grid"></div>
                </div>
            </div>

            <div className="threat-legend">
                <div className="legend-item">
                    <span className="legend-dot" style={{ backgroundColor: '#ef4444' }}></span>
                    <span>Critical</span>
                </div>
                <div className="legend-item">
                    <span className="legend-dot" style={{ backgroundColor: '#f59e0b' }}></span>
                    <span>High</span>
                </div>
                <div className="legend-item">
                    <span className="legend-dot" style={{ backgroundColor: '#06b6d4' }}></span>
                    <span>Medium</span>
                </div>
                <div className="legend-item">
                    <span className="legend-dot" style={{ backgroundColor: '#6b7280' }}></span>
                    <span>Low</span>
                </div>
            </div>
        </div>
    );
};

export default ThreatMap;
